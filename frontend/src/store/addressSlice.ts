import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";

export interface Address {
  id: number;
  user_id: number;
  name: string;
  mobile: string;
  alternate_mobile?: string;
  house_flat: string;
  street: string;
  landmark?: string;
  area?: string;
  city: string;
  state: string;
  pincode: string;
  address_type: string;
  is_default: boolean;
}

interface AddressState {
  items: Address[];
  status: "idle" | "loading" | "failed";
}

const initialState: AddressState = {
  items: [],
  status: "idle",
};

export const fetchAddresses = createAsyncThunk("addresses/fetchAll", async () => {
  const response = await api.get<Address[]>("/addresses");
  return response.data;
});

export const createAddress = createAsyncThunk("addresses/create", async (payload: Omit<Address, "id" | "user_id">) => {
  const response = await api.post<Address>("/addresses", payload);
  return response.data;
});

export const updateAddress = createAsyncThunk(
  "addresses/update",
  async ({ id, ...payload }: Partial<Omit<Address, "user_id">> & { id: number }) => {
    const response = await api.put<Address>(`/addresses/${id}`, payload);
    return response.data;
  }
);

export const deleteAddress = createAsyncThunk("addresses/delete", async (id: number) => {
  await api.delete(`/addresses/${id}`);
  return id;
});

export const addressSlice = createSlice({
  name: "addresses",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAddresses.pending, (state) => { state.status = "loading"; })
      .addCase(fetchAddresses.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchAddresses.rejected, (state) => { state.status = "failed"; })
      .addCase(createAddress.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(updateAddress.fulfilled, (state, action) => {
        const idx = state.items.findIndex((a) => a.id === action.payload.id);
        if (idx >= 0) state.items[idx] = action.payload;
      })
      .addCase(deleteAddress.fulfilled, (state, action) => {
        state.items = state.items.filter((a) => a.id !== action.payload);
      });
  },
});

export default addressSlice.reducer;