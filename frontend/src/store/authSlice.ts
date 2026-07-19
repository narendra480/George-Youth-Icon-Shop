import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import api from "../api/client";
import authClient from "../api/authClient";

export interface AuthUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  profile_image?: string | null;
  is_active: boolean;
  is_superuser: boolean;
  email_verified: boolean;
  last_login?: string | null;
  created_at: string;
  updated_at: string;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  rememberMe: boolean;
  loading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  message: string | null;
}

const getStoredItem = (key: string): string | null => {
  return localStorage.getItem(key) ?? sessionStorage.getItem(key);
};

const initialState: AuthState = {
  user: null,
  accessToken: getStoredItem("access_token"),
  refreshToken: getStoredItem("refresh_token"),
  rememberMe: getStoredItem("rememberMe") === "true",
  loading: false,
  isAuthenticated: Boolean(getStoredItem("access_token") || getStoredItem("refresh_token")),
  error: null,
  message: null,
};

const persistAuth = (
  accessToken: string | null,
  refreshToken: string | null,
  rememberMe: boolean,
) => {
  const storage = rememberMe ? localStorage : sessionStorage;
  const otherStorage = rememberMe ? sessionStorage : localStorage;

  if (accessToken) {
    storage.setItem("access_token", accessToken);
  } else {
    localStorage.removeItem("access_token");
    sessionStorage.removeItem("access_token");
  }

  if (refreshToken) {
    storage.setItem("refresh_token", refreshToken);
  } else {
    localStorage.removeItem("refresh_token");
    sessionStorage.removeItem("refresh_token");
  }

  storage.setItem("rememberMe", String(rememberMe));
  otherStorage.removeItem("rememberMe");
};

export const login = createAsyncThunk(
  "auth/login",
  async (
    payload: { email: string; password: string; rememberMe: boolean },
    { rejectWithValue },
  ) => {
    try {
      const response = await authClient.post("/login", {
        email: payload.email,
        password: payload.password,
      });
      return { ...response.data.data, rememberMe: payload.rememberMe };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || "Login failed");
    }
  },
);

export const register = createAsyncThunk(
  "auth/register",
  async (
    payload: { first_name: string; last_name: string; email: string; phone?: string; password: string; confirm_password: string; acceptTerms: boolean },
    { rejectWithValue },
  ) => {
    try {
      const response = await authClient.post("/register", {
        first_name: payload.first_name,
        last_name: payload.last_name,
        email: payload.email,
        phone: payload.phone,
        password: payload.password,
        confirm_password: payload.confirm_password,
      });
      return response.data.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || "Registration failed");
    }
  },
);

export const fetchCurrentUser = createAsyncThunk(
  "auth/fetchCurrentUser",
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get("/auth/me");
      return response.data.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || "Could not load user");
    }
  },
);

export const forgotPassword = createAsyncThunk(
  "auth/forgotPassword",
  async (payload: { email: string }, { rejectWithValue }) => {
    try {
      await authClient.post("/forgot-password", { email: payload.email });
      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || "Failed to submit request");
    }
  },
);

export const resetPassword = createAsyncThunk(
  "auth/resetPassword",
  async (
    payload: { token: string; password: string; confirm_password: string },
    { rejectWithValue },
  ) => {
    try {
      await authClient.post("/reset-password", payload);
      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || "Failed to reset password");
    }
  },
);

export const verifyEmail = createAsyncThunk(
  "auth/verifyEmail",
  async (payload: { token: string }, { rejectWithValue }) => {
    try {
      const response = await authClient.post("/verify-email", payload);
      return response.data.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || "Email verification failed");
    }
  },
);

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.rememberMe = false;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
      state.message = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("rememberMe");
      sessionStorage.removeItem("access_token");
      sessionStorage.removeItem("refresh_token");
      sessionStorage.removeItem("rememberMe");
    },
    setAuthTokens(
      state,
      action: PayloadAction<{ accessToken: string; refreshToken: string; rememberMe: boolean }>,
    ) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.rememberMe = action.payload.rememberMe;
      state.isAuthenticated = true;
      persistAuth(action.payload.accessToken, action.payload.refreshToken, action.payload.rememberMe);
    },
    clearError(state) {
      state.error = null;
    },
    setMessage(state, action: PayloadAction<string | null>) {
      state.message = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.message = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.error = null;
        state.message = "Login successful! Welcome back.";
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.rememberMe = action.payload.rememberMe;
        persistAuth(action.payload.access_token, action.payload.refresh_token, action.payload.rememberMe);
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.message = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
        state.message = "Registration completed successfully. Please verify your email before login.";
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(forgotPassword.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.message = null;
      })
      .addCase(forgotPassword.fulfilled, (state) => {
        state.loading = false;
        state.message = "If the email exists, password reset instructions were sent.";
      })
      .addCase(forgotPassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(resetPassword.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.message = null;
      })
      .addCase(resetPassword.fulfilled, (state) => {
        state.loading = false;
        state.message = "Password has been reset successfully.";
      })
      .addCase(resetPassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(verifyEmail.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.message = null;
      })
      .addCase(verifyEmail.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.message = "Your email address has been verified.";
      })
      .addCase(verifyEmail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, setAuthTokens, clearError, setMessage } = authSlice.actions;
export default authSlice.reducer;