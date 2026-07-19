import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import api from "../api/client";

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: string;
  link_url?: string;
  is_read: boolean;
  created_at: string;
}

interface NotificationState {
  items: Notification[];
  unreadCount: number;
  status: "idle" | "loading" | "failed";
  lastFetched: number | null;
}

const CACHE_DURATION = 2 * 60 * 1000; // 2 minutes

const initialState: NotificationState = {
  items: [],
  unreadCount: 0,
  status: "idle",
  lastFetched: null,
};

export const fetchNotifications = createAsyncThunk("notifications/fetchAll", async () => {
  const response = await api.get<Notification[]>("/notifications");
  return response.data;
});

export const markNotificationRead = createAsyncThunk(
  "notifications/markRead",
  async (id: number) => {
    const response = await api.put(`/notifications/${id}`, { is_read: true });
    return response.data;
  }
);

export const markAllNotificationsRead = createAsyncThunk(
  "notifications/markAllRead",
  async () => {
    await api.post("/notifications/mark-all");
    return true;
  }
);

export const deleteNotification = createAsyncThunk(
  "notifications/delete",
  async (id: number) => {
    await api.delete(`/notifications/${id}`);
    return id;
  }
);

export const notificationSlice = createSlice({
  name: "notifications",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchNotifications.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
        state.unreadCount = action.payload.filter((n) => !n.is_read).length;
        state.lastFetched = Date.now();
      })
      .addCase(fetchNotifications.rejected, (state) => {
        state.status = "failed";
      })
      .addCase(markNotificationRead.fulfilled, (state, action) => {
        const idx = state.items.findIndex((n) => n.id === action.payload.id);
        if (idx >= 0) {
          if (!state.items[idx].is_read) {
            state.unreadCount--;
          }
          state.items[idx] = action.payload;
        }
      })
      .addCase(markAllNotificationsRead.fulfilled, (state) => {
        state.items = state.items.map((n) => ({ ...n, is_read: true }));
        state.unreadCount = 0;
      })
      .addCase(deleteNotification.fulfilled, (state, action) => {
        const deleted = state.items.find((n) => n.id === action.payload);
        if (deleted && !deleted.is_read) {
          state.unreadCount--;
        }
        state.items = state.items.filter((n) => n.id !== action.payload);
      });
  },
});

export const selectNotifications = (state: { notifications: NotificationState }) => state.notifications.items;
export const selectUnreadCount = (state: { notifications: NotificationState }) => state.notifications.unreadCount;
export const selectNotificationsStatus = (state: { notifications: NotificationState }) => state.notifications.status;
export const selectShouldFetchNotifications = (state: { notifications: NotificationState }) => {
  const now = Date.now();
  return state.notifications.status !== "loading" &&
    (!state.notifications.lastFetched || (now - state.notifications.lastFetched) > CACHE_DURATION);
};

export default notificationSlice.reducer;