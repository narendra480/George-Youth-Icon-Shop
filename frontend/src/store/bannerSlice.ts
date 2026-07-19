import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface Banner {
  id: number;
  title?: string;
  subtitle?: string;
  description?: string;
  image_url: string;
  mobile_image_url?: string;
  link_url?: string;
  position?: string;
  sort_order?: number;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  background_color?: string;
  text_color?: string;
  overlay_opacity?: number;
  banner_type?: string;
  redirect_type?: string;
  cta_button_1_text?: string;
  cta_button_1_url?: string;
  cta_button_2_text?: string;
  cta_button_2_url?: string;
  category_id?: number;
  product_id?: number;
  is_featured?: boolean;
  view_count?: number;
  click_count?: number;
}

interface BannerState {
  items: Banner[];
  heroBanners: Banner[];
  status: "idle" | "loading" | "failed";
}

const initialState: BannerState = {
  items: [],
  heroBanners: [],
  status: "idle",
};

export const fetchBanners = createAsyncThunk("banners/fetchAll", async (position?: string) => {
  const response = await api.get<Banner[]>("/banners", { params: { position } });
  return response.data;
});

export const fetchHeroBanners = createAsyncThunk("banners/fetchHero", async () => {
  const response = await api.get<Banner[]>("/banners/hero");
  return response.data;
});

export const bannerSlice = createSlice({
  name: "banners",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBanners.pending, (state) => { state.status = "loading"; })
      .addCase(fetchBanners.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchBanners.rejected, (state) => { state.status = "failed"; })
      .addCase(fetchHeroBanners.fulfilled, (state, action) => {
        state.heroBanners = action.payload;
      });
  },
});

export default bannerSlice.reducer;