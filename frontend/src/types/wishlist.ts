export interface WishlistItem {
  id: number;
  product_id: number;
  variant_id?: number;
  created_at: string;
  product: any;
  variant?: any;
}