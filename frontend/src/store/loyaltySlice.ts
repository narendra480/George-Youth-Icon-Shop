import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface LoyaltyPoint {
  id: number;
  points: number;
  source: string;
  reference_id?: string;
  created_at: string;
}

export interface Referral {
  id: number;
  referral_code: string;
  status: string;
  reward_points: number;
  created_at: string;
}

export interface GiftCard {
  id: number;
  code: string;
  amount: number;
  balance: number;
  expiry_date?: string;
}

interface LoyaltyState {
  points: LoyaltyPoint[];
  referrals: Referral[];
  giftCards: GiftCard[];
  totalPoints: number;
  status: "idle" | "loading" | "failed";
}

const initialState: LoyaltyState = {
  points: [],
  referrals: [],
  giftCards: [],
  totalPoints: 0,
  status: "idle",
};

export const fetchLoyaltyPoints = createAsyncThunk(
  "loyalty/points",
  async () => {
    const response = await api.get<LoyaltyPoint[]>("/loyalty/points");
    return response.data;
  }
);

export const fetchReferrals = createAsyncThunk(
  "loyalty/referrals",
  async () => {
    const response = await api.get<Referral[]>("/loyalty/referrals");
    return response.data;
  }
);

export const createReferral = createAsyncThunk(
  "loyalty/create-referral",
  async () => {
    const response = await api.post<Referral>("/loyalty/referrals");
    return response.data;
  }
);

export const loyaltySlice = createSlice({
  name: "loyalty",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchLoyaltyPoints.fulfilled, (state, action) => {
        state.points = action.payload;
        state.totalPoints = action.payload.reduce((sum, p) => sum + p.points, 0);
      })
      .addCase(fetchReferrals.fulfilled, (state, action) => {
        state.referrals = action.payload;
      })
      .addCase(createReferral.fulfilled, (state, action) => {
        state.referrals.unshift(action.payload);
      });
  },
});

export default loyaltySlice.reducer;