import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import api from "../api/client";
import type { CartItem, Cart, LocalCartItem } from "../types/cart";

interface CartState {
  items: CartItem[];
  localItems: LocalCartItem[];
  cart: Cart | null;
  status: "idle" | "loading" | "failed";
  lastSynced: number | null;
}

const LOCAL_STORAGE_KEY = "guest_cart";

const getStoredLocalCart = (): LocalCartItem[] => {
  try {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

const persistLocalCart = (items: LocalCartItem[]) => {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(items));
};

const initialState: CartState = {
  items: [],
  localItems: getStoredLocalCart(),
  cart: null,
  status: "idle",
  lastSynced: null,
};

export const fetchCart = createAsyncThunk("cart/fetch", async () => {
  const response = await api.get<Cart>("/cart");
  return response.data;
});

export const addCartItem = createAsyncThunk(
  "cart/add",
  async (payload: { product_id: number; quantity?: number; variant_id?: number }, { getState }) => {
    const state = getState() as { cart: CartState; auth: { isAuthenticated: boolean } };
    if (state.auth.isAuthenticated) {
      const response = await api.post<CartItem>("/cart/items", payload);
      return { item: response.data, isLocal: false };
    }
    const newLocalItem: LocalCartItem = {
      product_id: payload.product_id,
      variant_id: payload.variant_id,
      quantity: payload.quantity || 1,
      added_at: new Date().toISOString(),
    };
    return { item: newLocalItem as any, isLocal: true };
  }
);

export const updateCartItem = createAsyncThunk(
  "cart/update",
  async (
    { itemId, quantity, is_saved_for_later, product_id }: {
      itemId?: number;
      product_id?: number;
      quantity: number;
      is_saved_for_later?: boolean;
    },
    { getState }
  ) => {
    const state = getState() as { cart: CartState; auth: { isAuthenticated: boolean } };
    if (state.auth.isAuthenticated) {
      const response = await api.put<CartItem>(
        `/cart/items/${itemId}?quantity=${quantity}${is_saved_for_later !== undefined ? `&is_saved_for_later=${is_saved_for_later}` : ""}`
      );
      return { item: response.data, isLocal: false };
    }
    const localItem = state.cart.localItems.find((i) => i.product_id === product_id);
    if (localItem) {
      return { item: { ...localItem, quantity } as any, isLocal: true };
    }
    return null;
  }
);

export const deleteCartItem = createAsyncThunk(
  "cart/delete",
  async (itemId: number | string, { getState }) => {
    const state = getState() as { cart: CartState; auth: { isAuthenticated: boolean } };
    if (state.auth.isAuthenticated) {
      await api.delete(`/cart/items/${itemId}`);
      return { itemId, isLocal: false };
    }
    return { itemId: Number(itemId), isLocal: true };
  }
);

export const clearCart = createAsyncThunk("cart/clear", async (_, { getState }) => {
  const state = getState() as { cart: CartState; auth: { isAuthenticated: boolean } };
  if (state.auth.isAuthenticated) {
    await api.post("/cart/clear");
  }
  localStorage.removeItem(LOCAL_STORAGE_KEY);
});

export const fetchCartTotals = createAsyncThunk("cart/totals", async (coupon_code?: string) => {
  const response = await api.get("/cart/totals", { params: { coupon_code } });
  return response.data;
});

export const syncLocalCartToServer = createAsyncThunk(
  "cart/syncToServer",
  async (_, { getState }) => {
    const state = getState() as { cart: CartState };
    const localItems = state.cart.localItems;
    if (!localItems.length) return null;
    for (const item of localItems) {
      await api.post<CartItem>("/cart/items", {
        product_id: item.product_id,
        quantity: item.quantity,
        variant_id: item.variant_id,
      });
    }
    return localItems;
  }
);

export const cartSlice = createSlice({
  name: "cart",
  initialState,
  reducers: {
    addLocalCartItem: (state, action: PayloadAction<LocalCartItem>) => {
      const exists = state.localItems.find(
        (i) => i.product_id === action.payload.product_id && i.variant_id === action.payload.variant_id
      );
      if (exists) {
        exists.quantity += action.payload.quantity;
      } else {
        state.localItems.push(action.payload);
      }
      persistLocalCart(state.localItems);
    },
    updateLocalCartItem: (
      state,
      action: PayloadAction<{ product_id: number; quantity: number; variant_id?: number }>
    ) => {
      const item = state.localItems.find(
        (i) => i.product_id === action.payload.product_id && i.variant_id === action.payload.variant_id
      );
      if (item && action.payload.quantity > 0) {
        item.quantity = action.payload.quantity;
      }
      persistLocalCart(state.localItems);
    },
    removeLocalCartItem: (
      state,
      action: PayloadAction<{ product_id: number; variant_id?: number }>
    ) => {
      state.localItems = state.localItems.filter(
        (i) => !(i.product_id === action.payload.product_id && i.variant_id === action.payload.variant_id)
      );
      persistLocalCart(state.localItems);
    },
    clearLocalCart: (state) => {
      state.localItems = [];
      localStorage.removeItem(LOCAL_STORAGE_KEY);
    },
    mergeLocalCart: (state, action: PayloadAction<CartItem[]>) => {
      state.items = action.payload;
      state.localItems = [];
      localStorage.removeItem(LOCAL_STORAGE_KEY);
      state.lastSynced = Date.now();
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCart.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchCart.fulfilled, (state, action) => {
        state.status = "idle";
        state.cart = action.payload;
        state.items = action.payload.items;
        state.lastSynced = Date.now();
      })
      .addCase(fetchCart.rejected, (state) => {
        state.status = "failed";
      })
      .addCase(addCartItem.fulfilled, (state, action) => {
        if (!action.payload) return;
        if (action.payload.isLocal) {
          const exists = state.localItems.find(
            (i) =>
              i.product_id === action.payload!.item.product_id &&
              (i.variant_id === action.payload!.item.variant_id || (!i.variant_id && !action.payload!.item.variant_id))
          );
          if (exists) {
            exists.quantity = action.payload.item.quantity;
          } else {
            state.localItems.push(action.payload.item);
          }
          persistLocalCart(state.localItems);
        } else {
          const exists = state.items.find((i) => i.id === action.payload!.item.id);
          if (exists) {
            state.items = state.items.map((i) =>
              i.id === action.payload!.item.id ? action.payload!.item : i
            );
          } else {
            state.items.push(action.payload!.item);
          }
        }
      })
      .addCase(updateCartItem.fulfilled, (state, action) => {
        if (!action.payload) return;
        if (action.payload.isLocal) {
          const item = state.localItems.find(
            (i) => i.product_id === action.payload!.item.product_id
          );
          if (item && action.payload.item.quantity) {
            item.quantity = action.payload.item.quantity;
          }
          persistLocalCart(state.localItems);
        } else {
          state.items = state.items.map((i) =>
            i.id === action.payload!.item.id ? action.payload!.item : i
          );
        }
      })
      .addCase(deleteCartItem.fulfilled, (state, action) => {
        if (action.payload.isLocal) {
          state.localItems = state.localItems.filter(
            (i) => !(i.product_id === action.payload.itemId || i.product_id === action.payload.itemId)
          );
          persistLocalCart(state.localItems);
        } else {
          state.items = state.items.filter((i) => i.id !== action.payload.itemId);
        }
      })
      .addCase(clearCart.fulfilled, (state) => {
        state.items = [];
        state.localItems = [];
        state.cart = null;
      })
      .addCase(syncLocalCartToServer.fulfilled, (state) => {
        state.lastSynced = Date.now();
      });
  },
});

export const {
  addLocalCartItem,
  updateLocalCartItem,
  removeLocalCartItem,
  clearLocalCart,
  mergeLocalCart,
} = cartSlice.actions;

export const selectCartItemCount = (state: { cart: CartState; auth: { isAuthenticated: boolean } }) => {
  return state.auth.isAuthenticated
    ? state.cart.items.reduce((sum, item) => sum + item.quantity, 0)
    : state.cart.localItems.reduce((sum, item) => sum + item.quantity, 0);
};

export const selectCartItems = (state: { cart: CartState; auth: { isAuthenticated: boolean } }) => {
  return state.auth.isAuthenticated ? state.cart.items : state.cart.localItems as any[];
};

export const selectCartSubtotal = (state: { cart: CartState; auth: { isAuthenticated: boolean } }) => {
  if (state.auth.isAuthenticated) {
    return state.cart.items.reduce((sum, item) => {
      const price = item.product?.selling_price || item.product?.mrp || 0;
      return sum + price * item.quantity;
    }, 0);
  }
  return state.cart.localItems.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0);
};

export const selectCartGrandTotal = (state: { cart: CartState; auth: { isAuthenticated: boolean } }) => {
  const subtotal = selectCartSubtotal(state);
  const gst = Math.round(subtotal * 0.18);
  const shipping = subtotal >= 1000 ? 0 : 50;
  return subtotal + gst + shipping;
};

export default cartSlice.reducer;