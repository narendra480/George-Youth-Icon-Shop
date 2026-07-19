import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import api from "../api/client";
import type { Product, ProductFilters, Brand, ProductVariant, ProductImage } from "../types/product";

interface ProductState {
  items: Product[];
  featured: Product[];
  newArrivals: Product[];
  bestSellers: Product[];
  trending: Product[];
  recommended: Product[];
  brands: Brand[];
  status: "idle" | "loading" | "failed";
  total: number;
}

const initialState: ProductState = {
  items: [],
  featured: [],
  newArrivals: [],
  bestSellers: [],
  trending: [],
  recommended: [],
  brands: [],
  status: "idle",
  total: 0,
};

export const fetchProducts = createAsyncThunk(
  "products/fetchAll",
  async (params?: ProductFilters) => {
    const response = await api.get<Product[]>("/products", { params });
    return response.data;
  }
);

export const fetchProductsCount = createAsyncThunk(
  "products/fetchCount",
  async (params?: Omit<ProductFilters, "skip" | "limit">) => {
    const response = await api.get<{ total: number }>("/products/count", { params });
    return response.data.total;
  }
);

export const fetchFeaturedProducts = createAsyncThunk("products/fetchFeatured", async (limit?: number) => {
  const response = await api.get<Product[]>("/products/featured", { params: { limit } });
  return response.data;
});

export const fetchNewArrivals = createAsyncThunk("products/fetchNewArrivals", async (limit?: number) => {
  const response = await api.get<Product[]>("/products/new-arrivals", { params: { limit } });
  return response.data;
});

export const fetchBestSellers = createAsyncThunk("products/fetchBestSellers", async (limit?: number) => {
  const response = await api.get<Product[]>("/products/best-sellers", { params: { limit } });
  return response.data;
});

export const fetchTrendingProducts = createAsyncThunk("products/fetchTrending", async (limit?: number) => {
  const response = await api.get<Product[]>("/products/trending", { params: { limit } });
  return response.data;
});

export const fetchRecommendedProducts = createAsyncThunk("products/fetchRecommended", async (limit?: number) => {
  const response = await api.get<Product[]>("/products/recommended", { params: { limit } });
  return response.data;
});

export const fetchProductById = createAsyncThunk("products/fetchById", async (productId: number) => {
  const response = await api.get<Product>(`/products/${productId}`);
  return response.data;
});

export const fetchBrands = createAsyncThunk("brands/fetchAll", async () => {
  const response = await api.get<Brand[]>("/brands");
  return response.data;
});

export interface ProductCreatePayload {
  name: string;
  slug: string;
  mrp: number;
  selling_price: number;
  category_id: number;
  description?: string;
  short_description?: string;
  sku?: string;
  barcode?: string;
  brand_id?: number;
  is_featured?: boolean;
  is_new_arrival?: boolean;
  is_best_seller?: boolean;
  discount_percentage?: number;
  status?: string;
}

export const createProduct = createAsyncThunk(
  "products/create",
  async (payload: ProductCreatePayload) => {
    const response = await api.post<Product>("/products", payload);
    return response.data;
  }
);

export const updateProduct = createAsyncThunk(
  "products/update",
  async ({ id, payload }: { id: number; payload: Partial<Omit<Product, "id" | "category" | "brand" | "images" | "variants" | "available_stock">> }) => {
    const response = await api.put<Product>(`/products/${id}`, payload);
    return response.data;
  }
);

export const deleteProduct = createAsyncThunk("products/delete", async (id: number) => {
  await api.delete(`/products/${id}`);
  return id;
});

export const uploadProductImage = createAsyncThunk(
  "products/uploadImage",
  async ({ productId, imagePath, altText, isPrimary }: { productId: number; imagePath: string; altText?: string; isPrimary?: boolean }) => {
    const form = new FormData();
    form.append("image_path", imagePath);
    if (altText) form.append("alt_text", altText);
    form.append("is_primary", String(Boolean(isPrimary)));
    const response = await api.post<ProductImage>(`/products/${productId}/images`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }
);

export const reorderProductImages = createAsyncThunk(
  "products/reorderImages",
  async ({ productId, imageIds }: { productId: number; imageIds: number[] }) => {
    await api.put(`/products/${productId}/images/reorder`, imageIds);
    return { productId, imageIds };
  }
);

export const bulkUpdateProductStatus = createAsyncThunk(
  "products/bulkUpdateStatus",
  async ({ productIds, status }: { productIds: number[]; status: string }) => {
    const response = await api.post<{ updated: number }>("/products/bulk/status", { product_ids: productIds, status });
    return response.data;
  }
);

export const bulkUpdateProductCategory = createAsyncThunk(
  "products/bulkUpdateCategory",
  async ({ productIds, categoryId }: { productIds: number[]; categoryId: number }) => {
    const response = await api.post<{ updated: number }>("/products/bulk/category", { product_ids: productIds, category_id: categoryId });
    return response.data;
  }
);

export const bulkDeleteProducts = createAsyncThunk(
  "products/bulkDelete",
  async (productIds: number[]) => {
    const response = await api.post<{ deleted: number }>("/products/bulk/delete", { product_ids: productIds });
    return response.data;
  }
);

export const productSlice = createSlice({
  name: "products",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.status = "loading"; })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchProducts.rejected, (state) => { state.status = "failed"; })
      .addCase(fetchProductsCount.fulfilled, (state, action) => { state.total = action.payload; })
      .addCase(fetchFeaturedProducts.fulfilled, (state, action) => { state.featured = action.payload; })
      .addCase(fetchNewArrivals.fulfilled, (state, action) => { state.newArrivals = action.payload; })
      .addCase(fetchBestSellers.fulfilled, (state, action) => { state.bestSellers = action.payload; })
      .addCase(fetchTrendingProducts.fulfilled, (state, action) => { state.trending = action.payload; })
      .addCase(fetchRecommendedProducts.fulfilled, (state, action) => { state.recommended = action.payload; })
      .addCase(fetchBrands.fulfilled, (state, action) => { state.brands = action.payload; })
      .addCase(createProduct.fulfilled, (state, action) => { state.items.unshift(action.payload); })
      .addCase(updateProduct.fulfilled, (state, action) => {
        const idx = state.items.findIndex((p) => p.id === action.payload.id);
        if (idx >= 0) state.items[idx] = action.payload;
      })
      .addCase(deleteProduct.fulfilled, (state, action) => {
        state.items = state.items.filter((p) => p.id !== action.payload);
      })
      .addCase(fetchProductById.fulfilled, (state, action) => {
        const idx = state.items.findIndex((p) => p.id === action.payload.id);
        if (idx >= 0) state.items[idx] = action.payload;
        else state.items.unshift(action.payload);
      });
  },
});

export default productSlice.reducer;