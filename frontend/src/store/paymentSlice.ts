import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface Payment {
  id: number;
  order_id: number;
  user_id: number;
  payment_method: string;
  payment_gateway?: string;
  gateway_order_id?: string;
  gateway_transaction_id?: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

interface PaymentState {
  items: Payment[];
  razorpayOrder: RazorpayOrder | null;
  status: "idle" | "loading" | "failed";
}

export interface RazorpayOrder {
  id: string;
  amount: number;
  currency: string;
  status: string;
}

const initialState: PaymentState = {
  items: [],
  razorpayOrder: null,
  status: "idle",
};

export const fetchPayments = createAsyncThunk("payments/fetchAll", async () => {
  const response = await api.get<Payment[]>("/payments/history");
  return response.data;
});

export const createRazorpayOrder = createAsyncThunk(
  "payments/createRazorpayOrder",
  async (payload: { amount: number; receipt: string }) => {
    const response = await api.post<RazorpayOrder>("/payments/create-order", payload);
    return response.data;
  }
);

export const verifyPayment = createAsyncThunk(
  "payments/verify",
  async (payload: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  }) => {
    const response = await api.post<Payment>("/payments/verify", payload);
    return response.data;
  }
);

export const paymentSlice = createSlice({
  name: "payments",
  initialState,
  reducers: {
    clearRazorpayOrder: (state) => {
      state.razorpayOrder = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPayments.pending, (state) => { state.status = "loading"; })
      .addCase(fetchPayments.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchPayments.rejected, (state) => { state.status = "failed"; })
      .addCase(createRazorpayOrder.fulfilled, (state, action) => {
        state.razorpayOrder = action.payload;
      });
  },
});

export const { clearRazorpayOrder } = paymentSlice.actions;
export default paymentSlice.reducer;