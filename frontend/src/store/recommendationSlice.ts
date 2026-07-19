import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface Recommendation {
  id: number;
  product_id: number;
  recommendation_type: string;
  score: number;
  is_clicked: boolean;
  is_purchased: boolean;
  product?: any;
}

interface RecommendationState {
  forYou: Recommendation[];
  similar: Recommendation[];
  frequentlyBoughtTogether: Recommendation[];
  trending: any[];
  recentlyViewed: any[];
  status: "idle" | "loading" | "failed";
}

const initialState: RecommendationState = {
  forYou: [],
  similar: [],
  frequentlyBoughtTogether: [],
  trending: [],
  recentlyViewed: [],
  status: "idle",
};

export const fetchRecommendationsForYou = createAsyncThunk(
  "recommendations/for-you",
  async (limit: number = 10) => {
    const response = await api.get<Recommendation[]>(`/recommendations/for-you?limit=${limit}`);
    return response.data;
  }
);

export const fetchSimilarProducts = createAsyncThunk(
  "recommendations/similar",
  async (product_id: number) => {
    const response = await api.get<Recommendation[]>(`/recommendations/similar/${product_id}`);
    return response.data;
  }
);

export const fetchFrequentlyBoughtTogether = createAsyncThunk(
  "recommendations/frequently-bought-together",
  async (product_id: number) => {
    const response = await api.get<any[]>(`/recommendations/frequently-bought-together/${product_id}`);
    return response.data;
  }
);

export const fetchTrendingProducts = createAsyncThunk(
  "recommendations/trending",
  async (period: string = "all") => {
    const response = await api.get<any[]>(`/recommendations/trending/${period}`);
    return response.data;
  }
);

export const fetchRecentlyViewed = createAsyncThunk(
  "recommendations/recently-viewed",
  async () => {
    const response = await api.get<any[]>("/recommendations/recently-viewed");
    return response.data;
  }
);

export const fetchSearchSuggestions = createAsyncThunk(
  "recommendations/search-suggestions",
  async (query: string) => {
    const response = await api.get<string[]>(`/recommendations/search/suggestions?query=${query}`);
    return response.data;
  }
);

export const recommendationSlice = createSlice({
  name: "recommendations",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchRecommendationsForYou.fulfilled, (state, action) => {
        state.forYou = action.payload;
      })
      .addCase(fetchSimilarProducts.fulfilled, (state, action) => {
        state.similar = action.payload;
      })
      .addCase(fetchFrequentlyBoughtTogether.fulfilled, (state, action) => {
        state.frequentlyBoughtTogether = action.payload;
      })
      .addCase(fetchTrendingProducts.fulfilled, (state, action) => {
        state.trending = action.payload;
      })
      .addCase(fetchRecentlyViewed.fulfilled, (state, action) => {
        state.recentlyViewed = action.payload;
      });
  },
});

export default recommendationSlice.reducer;