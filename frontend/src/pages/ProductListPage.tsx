import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCategories } from "../store/categorySlice";
import { fetchProducts, fetchBrands } from "../store/productSlice";
import {
  Box, Button, Card, CardActions, CardContent, Chip, Stack, Typography, TextField, MenuItem, Skeleton, Pagination,
} from "@mui/material";
import { formatINR } from "../utils/currency";
import type { Product } from "../types/product";

export function ProductListPage() {
  const dispatch = useAppDispatch();
  const products = useAppSelector((s) => s.products.items);
  const brands = useAppSelector((s) => s.products.brands);
  const categories = useAppSelector((s) => s.categories.items);
  const status = useAppSelector((s) => s.products.status);
  const total = useAppSelector((s) => s.products.total);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [selectedBrand, setSelectedBrand] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const limit = 12;

  useEffect(() => {
    dispatch(fetchCategories());
    dispatch(fetchBrands());
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchProducts({ category_id: selectedCategory ?? undefined, brand_id: selectedBrand ?? undefined, search: search || undefined, sort_by: sortBy, sort_order: sortOrder, skip: (page - 1) * limit, limit, status: "active" }));
  }, [dispatch, selectedCategory, selectedBrand, search, sortBy, sortOrder, page]);

  const imageUrl = (product: Product) => product.images?.[0]?.image_path;

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>Product Catalog</Typography>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} mb={3} alignItems="center">
        <TextField size="small" placeholder="Search by name, SKU, brand, category..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} sx={{ minWidth: 260 }} />
        <TextField select size="small" value={sortBy} onChange={(e) => setSortBy(e.target.value)} sx={{ minWidth: 160 }}>
          <MenuItem value="created_at">Newest</MenuItem>
          <MenuItem value="selling_price">Selling Price</MenuItem>
          <MenuItem value="name">Name</MenuItem>
          <MenuItem value="mrp">MRP</MenuItem>
        </TextField>
        <TextField select size="small" value={sortOrder} onChange={(e) => setSortOrder(e.target.value as "asc" | "desc")} sx={{ minWidth: 110 }}>
          <MenuItem value="asc">Asc</MenuItem>
          <MenuItem value="desc">Desc</MenuItem>
        </TextField>
      </Stack>
      <Stack direction="row" spacing={1} flexWrap="wrap" mb={3} alignItems="center">
        <Chip label="All" clickable color={selectedCategory === null ? "primary" : "default"} onClick={() => { setSelectedCategory(null); setPage(1); }} />
        {categories.map((cat) => (
          <Chip key={cat.id} label={cat.name} clickable color={selectedCategory === cat.id ? "primary" : "default"} onClick={() => { setSelectedCategory(cat.id); setPage(1); }} />
        ))}
      </Stack>
      <Stack direction="row" spacing={1} flexWrap="wrap" mb={3} alignItems="center">
        {brands.map((brand) => (
          <Chip key={brand.id} label={brand.name} clickable color={selectedBrand === brand.id ? "primary" : "default"} onClick={() => { setSelectedBrand(selectedBrand === brand.id ? null : brand.id); setPage(1); }} />
        ))}
      </Stack>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 3 }}>
        {status === "loading" && [1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i}><CardContent><Skeleton variant="rectangular" height={180} sx={{ mb: 2, borderRadius: 2 }} /><Skeleton variant="text" width="80%" /><Skeleton variant="text" width="60%" /></CardContent></Card>
        ))}
        {products.map((product) => (
          <Card key={product.id} sx={{ height: "100%" }}>
            <CardContent>
              <Box sx={{ width: "100%", height: 180, bgcolor: "#F1F5F9", borderRadius: 2, mb: 2, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "3rem", overflow: "hidden" }}>
                {imageUrl(product) ? <Box component="img" src={imageUrl(product)} alt={product.name} sx={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 2 }} /> : "👟"}
              </Box>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" sx={{ fontWeight: 700 }}>{product.name}</Typography>
              </Stack>
              {product.short_description && <Typography variant="body2" color="text.secondary" sx={{ my: 1, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{product.short_description}</Typography>}
              <Stack direction="row" spacing={1} alignItems="center" mt={1}>
                <Typography variant="h6" color="primary" sx={{ fontWeight: 700 }}>{formatINR(product.selling_price)}</Typography>
                {product.mrp > product.selling_price && (
                  <Typography variant="caption" sx={{ textDecoration: "line-through", color: "text.secondary" }}>{formatINR(product.mrp)}</Typography>
                )}
              </Stack>
              {product.you_save ? <Typography variant="caption" color="success.main">You save {formatINR(product.you_save)}</Typography> : null}
              <Stack direction="row" spacing={1} mt={1} flexWrap="wrap">
                <Typography variant="caption" color="text.secondary">{product.category?.name}</Typography>
                {product.is_new_arrival && <Chip label="New" size="small" color="secondary" />}
                {product.is_best_seller && <Chip label="Best Seller" size="small" color="primary" />}
                {product.available_stock !== undefined && product.available_stock <= 0 && <Chip label="Out of Stock" size="small" color="error" />}
              </Stack>
            </CardContent>
            <CardActions>
              <Button size="small">View Details</Button>
            </CardActions>
          </Card>
        ))}
      </Box>
      <Stack alignItems="center" mt={4}>
        <Pagination count={Math.max(1, Math.ceil(total / limit))} page={page} onChange={(_, p) => setPage(p)} />
      </Stack>
    </Box>
  );
}