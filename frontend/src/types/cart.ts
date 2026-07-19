export interface CartProduct {
  id: number;
  name: string;
  slug: string;
  selling_price: number;
  mrp: number;
  discount_percentage?: number;
  offer_price?: number;
  images?: Array<{ image_path: string; alt_text?: string }>;
  category?: { id: number; name: string; slug: string };
  brand?: { id: number; name: string; slug: string };
}

export interface CartItem {
  id: number;
  product_id: number;
  variant_id?: number;
  quantity: number;
  is_saved_for_later: boolean;
  created_at: string;
  updated_at: string;
  product: CartProduct;
  variant?: CartVariant;
}

export interface CartVariant {
  id: number;
  name: string;
  price?: number;
  mrp?: number;
  attributes?: Record<string, any>;
}

export interface Cart {
  id: number;
  user_id?: number;
  session_id?: string;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  gst_amount?: number;
  shipping_amount?: number;
  total_amount?: number;
  created_at: string;
  updated_at: string;
}

export interface LocalCartItem {
  product_id: number;
  variant_id?: number;
  quantity: number;
  added_at: string;
  price?: number;
}
