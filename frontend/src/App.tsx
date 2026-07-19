import { useEffect } from "react";
import { Container } from "@mui/material";
import { Route, Routes, useLocation } from "react-router-dom";

import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { VerifyEmailPage } from "./pages/VerifyEmailPage";
import { ProductListPage } from "./pages/ProductListPage";
import { ProductDetailPage } from "./pages/ProductDetailPage";
import { SearchPage } from "./pages/SearchPage";
import { CartPage } from "./pages/CartPage";
import { WishlistPage } from "./pages/WishlistPage";
import { CategoryListPage } from "./pages/CategoryListPage";
import { ProfilePage } from "./pages/ProfilePage";
import { AdminProductCreatePage } from "./pages/AdminProductCreatePage";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { AdminProductsPage } from "./pages/admin/AdminProductsPage";
import { AdminInventoryPage } from "./pages/admin/AdminInventoryPage";
import { AdminBannersPage } from "./pages/admin/AdminBannersPage";
import { CheckoutPage } from "./pages/CheckoutPage";
import { OrdersPage } from "./pages/OrdersPage";
import { AccountCenterPage } from "./pages/AccountCenterPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { PublicRoute } from "./components/PublicRoute";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { fetchCurrentUser } from "./store/authSlice";

export function App() {
  const dispatch = useAppDispatch();
  const location = useLocation();
  const { accessToken, isAuthenticated, user } = useAppSelector((state) => state.auth);

  const isHomePage = location.pathname === "/";

  useEffect(() => {
    if (accessToken && isAuthenticated && !user) {
      dispatch(fetchCurrentUser());
    }
  }, [accessToken, dispatch, isAuthenticated, user]);

  return (
    <>
      <Header />
      {isHomePage ? (
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      ) : (
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Routes>
            <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
            <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />
            <Route path="/reset-password" element={<PublicRoute><ResetPasswordPage /></PublicRoute>} />
            <Route path="/verify-email" element={<PublicRoute><VerifyEmailPage /></PublicRoute>} />
            <Route path="/products" element={<ProductListPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/wishlist" element={<WishlistPage />} />
<Route path="/categories" element={<CategoryListPage />} />
            <Route path="/checkout" element={<ProtectedRoute><CheckoutPage /></ProtectedRoute>} />
            <Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
            <Route path="/orders/:id" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
            <Route path="/account" element={<ProtectedRoute><AccountCenterPage /></ProtectedRoute>}>
              <Route path="profile" element={<ProfilePage />} />
              <Route path="orders" element={<OrdersPage />} />
              <Route path="wishlist" element={<WishlistPage />} />
              <Route path="addresses" element={<ProfilePage />} />
              <Route path="notifications" element={<ProfilePage />} />
              <Route path="settings" element={<ProfilePage />} />
              <Route path="security" element={<ProfilePage />} />
            </Route>
            <Route path="/admin/dashboard" element={<ProtectedRoute><AdminDashboardPage /></ProtectedRoute>} />
            <Route path="/admin/products" element={<ProtectedRoute><AdminProductsPage /></ProtectedRoute>} />
            <Route path="/admin/products/new" element={<ProtectedRoute><AdminProductCreatePage /></ProtectedRoute>} />
            <Route path="/admin/inventory" element={<ProtectedRoute><AdminInventoryPage /></ProtectedRoute>} />
            <Route path="/admin/banners" element={<ProtectedRoute><AdminBannersPage /></ProtectedRoute>} />
          </Routes>
        </Container>
      )}
      <Footer />
    </>
  );
}
