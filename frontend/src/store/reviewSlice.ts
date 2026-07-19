import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface ReviewUser {
  id: number;
  first_name?: string;
  last_name?: string;
}

export interface Review {
  id: number;
  product_id: number;
  user_id: number;
  rating: number;
  title?: string;
  comment?: string;
  is_verified_purchase: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user?: ReviewUser;
}

interface ReviewState {
  items: Review[];
  status: "idle" | "loading" | "failed";
}

const initialState: ReviewState = {
  items: [],
  status: "idle",
};

export const fetchReviews = createAsyncThunk("reviews/fetchAll", async (params?: { is_active?: boolean; limit?: number }) => {
  const response = await api.get<Review[]>("/reviews", { params });
  return response.data;
});

export const reviewSlice = createSlice({
  name: "reviews",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchReviews.pending, (state) => { state.status = "loading"; })
      .addCase(fetchReviews.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchReviews.rejected, (state) => { state.status = "failed"; });
  },
});

export default reviewSlice.reducer;