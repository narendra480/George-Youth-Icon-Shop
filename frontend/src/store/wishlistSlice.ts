import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import api from "../api/client";
import type { WishlistItem } from "../types/wishlist";

interface WishlistState {
  items: WishlistItem[];
  localItems: number[];
  status: "idle" | "loading" | "failed";
}

const LOCAL_STORAGE_KEY = "guest_wishlist";

const getStoredLocalWishlist = (): number[] => {
  try {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

const persistLocalWishlist = (items: number[]) => {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(items));
};

const initialState: WishlistState = {
  items: [],
  localItems: getStoredLocalWishlist(),
  status: "idle",
};

export const fetchWishlist = createAsyncThunk("wishlist/fetch", async () => {
  const response = await api.get<WishlistItem[]>("/wishlist");
  return response.data;
});

interface AddWishlistPayload {
  item: WishlistItem;
  isLocal: boolean;
  product_id: number;
}

export const addToWishlist = createAsyncThunk<
  AddWishlistPayload | null,
  { product_id: number; variant_id?: number },
  { state: { wishlist: WishlistState; auth: { isAuthenticated: boolean } } }
>("wishlist/add", async (payload, { getState }) => {
  const state = getState();
  if (state.auth.isAuthenticated) {
    const response = await api.post<WishlistItem>("/wishlist", payload);
    return { item: response.data, isLocal: false, product_id: payload.product_id };
  }
  return { product_id: payload.product_id, isLocal: true, item: null as any };
});

export const removeFromWishlist = createAsyncThunk(
  "wishlist/remove",
  async (productId: number, { getState }) => {
    const state = getState() as { wishlist: WishlistState; auth: { isAuthenticated: boolean } };
    if (state.auth.isAuthenticated) {
      await api.delete(`/wishlist/${productId}`);
      return { productId, isLocal: false };
    }
    return { productId, isLocal: true };
  }
);

export const syncLocalWishlistToServer = createAsyncThunk(
  "wishlist/syncToServer",
  async (_, { getState }) => {
    const state = getState() as { wishlist: WishlistState };
    const localItems = state.wishlist.localItems;
    if (!localItems.length) return null;
    for (const productId of localItems) {
      await api.post<WishlistItem>("/wishlist", { product_id: productId });
    }
    return localItems;
  }
);

export const wishlistSlice = createSlice({
  name: "wishlist",
  initialState,
  reducers: {
    addLocalWishlistItem: (state, action: PayloadAction<number>) => {
      if (!state.localItems.includes(action.payload)) {
        state.localItems.push(action.payload);
        persistLocalWishlist(state.localItems);
      }
    },
    removeLocalWishlistItem: (state, action: PayloadAction<number>) => {
      state.localItems = state.localItems.filter((id) => id !== action.payload);
      persistLocalWishlist(state.localItems);
    },
    clearLocalWishlist: (state) => {
      state.localItems = [];
      localStorage.removeItem(LOCAL_STORAGE_KEY);
    },
    mergeLocalWishlist: (state, action: PayloadAction<WishlistItem[]>) => {
      state.items = action.payload;
      state.localItems = [];
      localStorage.removeItem(LOCAL_STORAGE_KEY);
    },
    toggleLocalWishlist: (state, action: PayloadAction<number>) => {
      if (state.localItems.includes(action.payload)) {
        state.localItems = state.localItems.filter((id) => id !== action.payload);
      } else {
        state.localItems.push(action.payload);
      }
      persistLocalWishlist(state.localItems);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWishlist.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchWishlist.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchWishlist.rejected, (state) => {
        state.status = "failed";
      })
      .addCase(addToWishlist.fulfilled, (state, action) => {
        const payload = action.payload;
        if (payload && payload.isLocal && payload.product_id !== undefined) {
          if (!state.localItems.includes(payload.product_id)) {
            state.localItems.push(payload.product_id);
          }
          persistLocalWishlist(state.localItems);
        } else if (payload && payload.item) {
          const exists = state.items.find((i) => i.product_id === payload.item!.product_id);
          if (!exists) {
            state.items.push(payload.item);
          }
        }
      })
      .addCase(removeFromWishlist.fulfilled, (state, action) => {
        if (action.payload.isLocal) {
          state.localItems = state.localItems.filter(
            (id) => id !== action.payload.productId
          );
          persistLocalWishlist(state.localItems);
        } else {
          state.items = state.items.filter((i) => i.product_id !== action.payload.productId);
        }
      });
  },
});

export const {
  addLocalWishlistItem,
  removeLocalWishlistItem,
  clearLocalWishlist,
  mergeLocalWishlist,
  toggleLocalWishlist,
} = wishlistSlice.actions;

export const selectWishlistCount = (state: { wishlist: WishlistState; auth: { isAuthenticated: boolean } }) => {
  return state.auth.isAuthenticated ? state.wishlist.items.length : state.wishlist.localItems.length;
};

export const selectWishlistItems = (state: { wishlist: WishlistState; auth: { isAuthenticated: boolean } }) => {
  return state.auth.isAuthenticated ? state.wishlist.items : state.wishlist.localItems.map(id => ({ product_id: id } as WishlistItem));
};

export const selectIsProductInWishlist = (productId: number) => (
  state: { wishlist: WishlistState; auth: { isAuthenticated: boolean } }
) => {
  return state.auth.isAuthenticated
    ? state.wishlist.items.some((i) => i.product_id === productId)
    : state.wishlist.localItems.includes(productId);
};

export default wishlistSlice.reducer;