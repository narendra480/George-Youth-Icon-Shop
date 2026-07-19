import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface Vendor {
  id: number;
  user_id: number;
  vendor_code: string;
  shop_name: string;
  status: string;
  commission_percentage: number;
  rating?: number;
}

export interface Settlement {
  id: number;
  vendor_id: number;
  amount: number;
  commission: number;
  status: string;
  created_at: string;
}

interface VendorState {
  vendors: Vendor[];
  myVendor: Vendor | null;
  settlements: Settlement[];
  status: "idle" | "loading" | "failed";
}

const initialState: VendorState = {
  vendors: [],
  myVendor: null,
  settlements: [],
  status: "idle",
};

export const fetchVendors = createAsyncThunk(
  "vendors/all",
  async () => {
    const response = await api.get<Vendor[]>("/vendors");
    return response.data;
  }
);

export const fetchMyVendor = createAsyncThunk(
  "vendors/me",
  async () => {
    const response = await api.get<Vendor>("/vendors/me");
    return response.data;
  }
);

export const applyVendor = createAsyncThunk(
  "vendors/apply",
  async (payload: { shop_name: string; gstin?: string; pan?: string; bank_account?: string }) => {
    const response = await api.post<Vendor>("/vendors/apply", payload);
    return response.data;
  }
);

export const fetchSettlements = createAsyncThunk(
  "vendors/settlements",
  async () => {
    const response = await api.get<Settlement[]>("/settlements");
    return response.data;
  }
);

export const vendorSlice = createSlice({
  name: "vendors",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchVendors.fulfilled, (state, action) => {
        state.vendors = action.payload;
      })
      .addCase(fetchMyVendor.fulfilled, (state, action) => {
        state.myVendor = action.payload;
      })
      .addCase(applyVendor.fulfilled, (state, action) => {
        state.myVendor = action.payload;
      })
      .addCase(fetchSettlements.fulfilled, (state, action) => {
        state.settlements = action.payload;
      });
  },
});

export default vendorSlice.reducer;