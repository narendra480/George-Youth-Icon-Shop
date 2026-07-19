export interface ProductImage {
  id: number;
  image_path: string;
  alt_text?: string;
  sort_order: number;
  is_primary: boolean;
  created_at: string;
}

export interface ProductVariant {
  id: number;
  sku: string;
  name?: string;
  attributes?: Record<string, any>;
  images?: string[];
  price?: number;
  mrp?: number;
  inventory_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  sku?: string;
  barcode?: string;
  short_description?: string;
  description?: string;
  specifications?: Record<string, any>;
  search_keywords?: string;
  tags?: string[];
  dimensions?: Record<string, any>;
  weight?: number;
  weight_unit?: string;
  gst_percentage?: number;
  hsn_code?: string;
  country_of_origin?: string;
  manufacturer?: string;

  cost_price?: number;
  mrp: number;
  selling_price: number;
  discount_percentage: number;
  offer_price?: number;
  offer_start_date?: string;
  offer_end_date?: string;

  you_save?: number;

  is_featured: boolean;
  is_new_arrival: boolean;
  is_best_seller: boolean;
  is_trending?: boolean;
  status: string;

  category_id: number;
  brand_id?: number;

  images: ProductImage[];
  variants: ProductVariant[];

  category?: { id: number; name: string; slug: string };
  brand?: Brand;

  available_stock?: number;
  average_rating?: number;
  review_count?: number;

  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  is_featured?: boolean;
  is_active?: boolean;
}

export interface ProductRating {
  average_rating?: number;
  review_count?: number;
}

export interface ProductFilters {
  category_id?: number;
  brand_id?: number;
  status?: string;
  search?: string;
  tags?: string[];
  min_price?: number;
  max_price?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  skip?: number;
  limit?: number;
}