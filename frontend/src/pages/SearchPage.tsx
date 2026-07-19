import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchProducts } from "../store/productSlice";
import {
  Box, Typography, Stack, TextField, InputAdornment, Skeleton,
} from "@mui/material";
import { Search as SearchIcon } from "@mui/icons-material";
import { formatINR } from "../utils/currency";
import type { Product } from "../types/product";

export function SearchPage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const products = useAppSelector((s) => s.products.items);
  const status = useAppSelector((s) => s.products.status);
  const [query, setQuery] = useState("");

  const doSearch = useCallback((q: string) => {
    dispatch(fetchProducts({ search: q || undefined, sort_by: "created_at", sort_order: "desc", limit: 20 }));
  }, [dispatch]);

  useEffect(() => {
    doSearch(query);
  }, [doSearch, query]);

  const goTo = (id: number) => navigate(`/products/${id}`);

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>Search</Typography>
      <TextField
        size="small"
        placeholder="Search by name, SKU, brand, category, tags..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ minWidth: 320, mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      {status === "loading" && <Skeleton variant="rectangular" height={300} />}
      <Stack spacing={2}>
        {products.map((product: Product) => (
          <Box key={product.id} sx={{ p: 2, border: "1px solid rgba(0,0,0,0.06)", borderRadius: 2, cursor: "pointer", background: "#FFFFFF" }} onClick={() => goTo(product.id)}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Box sx={{ width: 64, height: 64, borderRadius: 2, bgcolor: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden", flexShrink: 0 }}>
                {product.images?.[0]?.image_path ? <Box component="img" src={product.images[0].image_path} alt={product.name} sx={{ width: "100%", height: "100%", objectFit: "cover" }} /> : "👟"}
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{product.name}</Typography>
                <Typography variant="body2" color="text.secondary">{product.category?.name} {product.brand?.name ? `• ${product.brand.name}` : ""}</Typography>
              </Box>
              <Typography variant="subtitle1" color="primary" sx={{ fontWeight: 700 }}>{formatINR(product.selling_price)}</Typography>
            </Stack>
          </Box>
        ))}
        {products.length === 0 && status !== "loading" && (
          <Typography color="text.secondary">No results found</Typography>
        )}
      </Stack>
    </Box>
  );
}