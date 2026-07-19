import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

interface ShopSettings {
  id: number;
  shop_name: string;
  tagline: string | null;
  description: string | null;
  owner_name: string | null;
  logo_url: string | null;
  hero_banner_url: string | null;
  primary_phone: string | null;
  phone_numbers: string[] | null;
  whatsapp: string | null;
  email: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;
  business_hours: Record<string, { open: string; close: string }> | null;
  google_maps_url: string | null;
  facebook_url: string | null;
  instagram_url: string | null;
  twitter_url: string | null;
  youtube_url: string | null;
  linkedin_url: string | null;
  footer_text: string | null;
  copyright_text: string | null;
  privacy_policy_url: string | null;
  terms_url: string | null;
  faq_url: string | null;
}

interface ShopSettingsState {
  data: ShopSettings | null;
  status: "idle" | "loading" | "failed";
}

const initialState: ShopSettingsState = {
  data: null,
  status: "idle",
};

export const fetchShopSettings = createAsyncThunk("shopSettings/fetch", async () => {
  const response = await api.get<ShopSettings>("/shop-settings/public");
  return response.data;
});

export const shopSettingsSlice = createSlice({
  name: "shopSettings",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchShopSettings.pending, (state) => { state.status = "loading"; })
      .addCase(fetchShopSettings.fulfilled, (state, action) => {
        state.status = "idle";
        state.data = action.payload;
      })
      .addCase(fetchShopSettings.rejected, (state) => { state.status = "failed"; });
  },
});

export default shopSettingsSlice.reducer;