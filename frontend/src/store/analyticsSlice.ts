import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface DashboardMetrics {
  sales: {
    today: number;
    yesterday: number;
    this_month: number;
    total: number;
    average_order_value: number;
  };
  orders: {
    total: number;
    pending: number;
    cancelled: number;
  };
  customers: {
    total: number;
  };
  inventory: {
    total_products: number;
    out_of_stock: number;
    low_stock: number;
  };
  suppliers: {
    total: number;
    pending_pos: number;
  };
}

interface AnalyticsState {
  dashboard: DashboardMetrics | null;
  salesData: any[];
  status: "idle" | "loading" | "failed";
}

const initialState: AnalyticsState = {
  dashboard: null,
  salesData: [],
  status: "idle",
};

export const fetchDashboardAnalytics = createAsyncThunk(
  "analytics/dashboard",
  async () => {
    const response = await api.get<DashboardMetrics>("/analytics/dashboard");
    return response.data;
  }
);

export const fetchSalesAnalytics = createAsyncThunk(
  "analytics/sales",
  async (period: string = "month") => {
    const response = await api.get(`/analytics/sales?period=${period}`);
    return response.data;
  }
);

export const fetchTopProducts = createAsyncThunk(
  "analytics/top-products",
  async () => {
    const response = await api.get("/analytics/products/top");
    return response.data;
  }
);

export const analyticsSlice = createSlice({
  name: "analytics",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardAnalytics.pending, (state) => { state.status = "loading"; })
      .addCase(fetchDashboardAnalytics.fulfilled, (state, action) => {
        state.status = "idle";
        state.dashboard = action.payload;
      })
      .addCase(fetchDashboardAnalytics.rejected, (state) => { state.status = "failed"; })
      .addCase(fetchSalesAnalytics.fulfilled, (state, action) => {
        state.salesData = action.payload;
      });
  },
});

export default analyticsSlice.reducer;