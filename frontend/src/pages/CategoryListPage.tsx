import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCategories } from "../store/categorySlice";
import { fetchProducts } from "../store/productSlice";
import {
  Box, Typography, Stack, Chip, Skeleton, TextField, MenuItem, Pagination, FormControl, InputLabel, Select, Slider, Checkbox, FormControlLabel, Button,
} from "@mui/material";
import { Search as SearchIcon, FilterList as FilterIcon } from "@mui/icons-material";
import { formatINR } from "../utils/currency";
import type { Product } from "../types/product";

export function CategoryListPage() {
  const dispatch = useAppDispatch();
  const categories = useAppSelector((s) => s.categories.items);
  const products = useAppSelector((s) => s.products.items);
  const status = useAppSelector((s) => s.products.status);
  const total = useAppSelector((s) => s.products.total);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [priceRange, setPriceRange] = useState<number[]>([0, 20000]);
  const [availability, setAvailability] = useState<string>("all");
  const [showFilters, setShowFilters] = useState(false);
  const limit = 12;

  useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchProducts({ category_id: selectedCategory ?? undefined, search: search || undefined, sort_by: sortBy, sort_order: sortOrder, skip: (page - 1) * limit, limit, status: "active" }));
  }, [dispatch, selectedCategory, search, sortBy, sortOrder, page]);

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>Browse by Category</Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" mb={3} alignItems="center">
        <Chip label="All" clickable color={selectedCategory === null ? "primary" : "default"} onClick={() => { setSelectedCategory(null); setPage(1); }} />
        {categories.map((cat) => (
          <Chip key={cat.id} label={cat.name} clickable color={selectedCategory === cat.id ? "primary" : "default"} onClick={() => { setSelectedCategory(cat.id); setPage(1); }} />
        ))}
      </Stack>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} mb={3} alignItems="center">
        <TextField size="small" placeholder="Search products..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} sx={{ minWidth: 260 }} InputProps={{ startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1 }} /> }} />
        <TextField select size="small" label="Sort By" value={sortBy} onChange={(e) => setSortBy(e.target.value)} sx={{ minWidth: 160 }}>
          <MenuItem value="created_at">Newest</MenuItem>
          <MenuItem value="selling_price">Price</MenuItem>
          <MenuItem value="name">Name</MenuItem>
        </TextField>
        <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters((v) => !v)}>Filters</Button>
      </Stack>
      {showFilters && (
        <Stack direction={{ xs: "column", md: "row" }} spacing={3} mb={3} p={2} sx={{ border: "1px solid rgba(0,0,0,0.06)", borderRadius: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" gutterBottom>Price Range</Typography>
            <Slider value={priceRange} onChange={(_, v) => setPriceRange(v as number[])} min={0} max={20000} step={100} valueLabelDisplay="auto" />
            <Stack direction="row" justifyContent="space-between"><Typography variant="caption">{formatINR(priceRange[0])}</Typography><Typography variant="caption">{formatINR(priceRange[1])}</Typography></Stack>
          </Box>
          <Box sx={{ minWidth: 200 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Availability</InputLabel>
              <Select value={availability} label="Availability" onChange={(e) => setAvailability(e.target.value)}>
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="instock">In Stock</MenuItem>
                <MenuItem value="outofstock">Out of Stock</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Stack>
      )}
      {status === "loading" && (
        <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 2 }}>
          {[1, 2, 3, 4, 5, 6].map((i) => (<Box key={i}><Skeleton variant="rectangular" height={160} sx={{ borderRadius: 2 }} /></Box>))}
        </Box>
      )}
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 2 }}>
        {products.map((product: Product) => (
          <Box key={product.id} sx={{ border: "1px solid rgba(0,0,0,0.06)", borderRadius: 2, p: 2, background: "#FFFFFF" }}>
            <Box sx={{ width: "100%", height: 160, borderRadius: 2, bgcolor: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden", mb: 1 }}>
              {product.images?.[0]?.image_path ? <Box component="img" src={product.images[0].image_path} alt={product.name} sx={{ width: "100%", height: "100%", objectFit: "cover" }} /> : "👟"}
            </Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{product.name}</Typography>
            <Typography variant="body2" color="text.secondary">{product.category?.name}</Typography>
            <Typography variant="h6" color="primary" sx={{ fontWeight: 700 }}>{formatINR(product.selling_price)}</Typography>
            {product.available_stock !== undefined && product.available_stock <= 0 && <Typography variant="caption" color="error">Out of Stock</Typography>}
          </Box>
        ))}
      </Box>
      <Stack alignItems="center" mt={4}>
        <Pagination count={Math.max(1, Math.ceil(total / limit))} page={page} onChange={(_, p) => setPage(p)} />
      </Stack>
    </Box>
  );
}