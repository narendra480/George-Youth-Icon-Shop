import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./authSlice";
import productReducer from "./productSlice";
import categoryReducer from "./categorySlice";
import shopSettingsReducer from "./shopSettingsSlice";
import cartReducer from "./cartSlice";
import wishlistReducer from "./wishlistSlice";
import bannerReducer from "./bannerSlice";
import reviewReducer from "./reviewSlice";
import orderReducer from "./orderSlice";
import addressReducer from "./addressSlice";
import paymentReducer from "./paymentSlice";
import notificationReducer from "./notificationSlice";
import analyticsReducer from "./analyticsSlice";
import loyaltyReducer from "./loyaltySlice";
import recommendationReducer from "./recommendationSlice";
import vendorReducer from "./vendorSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    products: productReducer,
    categories: categoryReducer,
    shopSettings: shopSettingsReducer,
    cart: cartReducer,
    wishlist: wishlistReducer,
    banners: bannerReducer,
    reviews: reviewReducer,
    orders: orderReducer,
    addresses: addressReducer,
    payments: paymentReducer,
    analytics: analyticsReducer,
    loyalty: loyaltyReducer,
    vendors: vendorReducer,
    recommendations: recommendationReducer,
    notifications: notificationReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
