import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";
import type { Category } from "../types/category";

interface CategoryState {
  items: Category[];
  status: "idle" | "loading" | "failed";
  lastFetched: number | null;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const initialState: CategoryState = {
  items: [],
  status: "idle",
  lastFetched: null,
};

export const fetchCategories = createAsyncThunk("categories/fetchAll", async () => {
  const response = await api.get<Category[]>("/categories");
  return response.data;
});

export const fetchCategoriesWithHierarchy = createAsyncThunk("categories/fetchHierarchy", async () => {
  const response = await api.get<Category[]>("/categories/hierarchy");
  return response.data;
});

export const fetchCategoriesWithCounts = createAsyncThunk("categories/fetchWithCounts", async () => {
  const response = await api.get<Category[]>("/categories/with-counts");
  return response.data;
});

const buildCategoryTree = (categories: Category[]): Category[] => {
  const map = new Map<number, Category>();
  const roots: Category[] = [];

  categories.forEach((cat) => {
    map.set(cat.id, { ...cat, children: [] });
  });

  categories.forEach((cat) => {
    const node = map.get(cat.id)!;
    if (cat.parent_id && map.has(cat.parent_id)) {
      const parent = map.get(cat.parent_id)!;
      parent.children = parent.children || [];
      parent.children.push(node);
    } else {
      roots.push(node);
    }
  });

  return roots;
};

export const categorySlice = createSlice({
  name: "categories",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchCategories.pending, (state) => { state.status = "loading"; })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = buildCategoryTree(action.payload);
        state.lastFetched = Date.now();
      })
      .addCase(fetchCategories.rejected, (state) => { state.status = "failed"; })
      .addCase(fetchCategoriesWithHierarchy.fulfilled, (state, action) => {
        state.items = action.payload;
        state.lastFetched = Date.now();
      })
      .addCase(fetchCategoriesWithCounts.fulfilled, (state, action) => {
        state.items = buildCategoryTree(action.payload);
        state.lastFetched = Date.now();
      });
  },
});

export const selectCategories = (state: { categories: CategoryState }) => state.categories.items;
export const selectCategoriesStatus = (state: { categories: CategoryState }) => state.categories.status;
export const selectShouldFetchCategories = (state: { categories: CategoryState }) => {
  const now = Date.now();
  return !state.categories.items.length || 
    (state.categories.lastFetched && (now - state.categories.lastFetched) > CACHE_DURATION);
};

export default categorySlice.reducer;