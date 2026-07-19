export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent_id?: number | null;
  banner_url?: string;
  thumbnail_url?: string;
  icon_url?: string;
  is_featured?: boolean;
  display_order?: number;
  product_count?: number;
  children?: Category[];
}