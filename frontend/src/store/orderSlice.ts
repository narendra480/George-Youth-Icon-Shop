import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface OrderItem {
  id: number;
  product_id: number;
  variant_id?: number;
  quantity: number;
  price: number;
  mrp: number;
  product?: { id: number; name: string; images?: { image_path: string }[] };
}

export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  address_id: number;
  subtotal: number;
  gst_amount: number;
  shipping_amount: number;
  discount_amount: number;
  total_amount: number;
  status: string;
  payment_status: string;
  payment_method?: string;
  delivery_estimate?: string;
  coupon_code?: string;
  created_at: string;
  updated_at: string;
  items?: OrderItem[];
  address?: {
    id: number;
    name: string;
    mobile: string;
    house_flat: string;
    street: string;
    city: string;
    state: string;
    pincode: string;
  };
}

interface OrderState {
  items: Order[];
  selected: Order | null;
  status: "idle" | "loading" | "failed";
}

const initialState: OrderState = {
  items: [],
  selected: null,
  status: "idle",
};

export const fetchOrders = createAsyncThunk("orders/fetchAll", async () => {
  const response = await api.get<Order[]>("/orders");
  return response.data;
});

export const fetchOrderById = createAsyncThunk("orders/fetchById", async (orderId: number) => {
  const response = await api.get<Order>(`/orders/${orderId}`);
  return response.data;
});

export const createOrder = createAsyncThunk("orders/create", async (payload: { address_id: number; items: any[]; coupon_code?: string }) => {
  const response = await api.post<Order>("/orders", payload);
  return response.data;
});

export const updateOrderStatus = createAsyncThunk(
  "orders/updateStatus",
  async ({ orderId, status }: { orderId: number; status: string }) => {
    const response = await api.put<Order>(`/orders/${orderId}`, { status });
    return response.data;
  }
);

export const orderSlice = createSlice({
  name: "orders",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrders.pending, (state) => { state.status = "loading"; })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchOrders.rejected, (state) => { state.status = "failed"; })
      .addCase(fetchOrderById.fulfilled, (state, action) => { state.selected = action.payload; })
      .addCase(createOrder.fulfilled, (state, action) => { state.items.unshift(action.payload); });
  },
});

export default orderSlice.reducer;