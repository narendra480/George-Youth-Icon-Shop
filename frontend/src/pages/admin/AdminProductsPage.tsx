import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { fetchProducts, fetchBrands, bulkUpdateProductStatus, bulkUpdateProductCategory, bulkDeleteProducts } from "../../store/productSlice";
import { fetchCategories } from "../../store/categorySlice";
import {
  Box, Typography, Stack, Button, IconButton, TextField, MenuItem, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Checkbox, Dialog, DialogTitle, DialogContent, DialogActions, Select, FormControl, InputLabel, Skeleton,
} from "@mui/material";
import { Delete as DeleteIcon, Edit as EditIcon } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

export function AdminProductsPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const products = useAppSelector((s) => s.products.items);
  const brands = useAppSelector((s) => s.products.brands);
  const categories = useAppSelector((s) => s.categories.items);
  const status = useAppSelector((s) => s.products.status);
  const [selected, setSelected] = useState<number[]>([]);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [brandFilter, setBrandFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [bulkStatusOpen, setBulkStatusOpen] = useState(false);
  const [bulkCategoryOpen, setBulkCategoryOpen] = useState(false);
  const [newStatus, setNewStatus] = useState("active");
  const [newCategoryId, setNewCategoryId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    dispatch(fetchCategories());
    dispatch(fetchBrands());
    dispatch(fetchProducts({ search: search || undefined, category_id: categoryFilter ? Number(categoryFilter) : undefined, brand_id: brandFilter ? Number(brandFilter) : undefined, status: statusFilter || undefined, sort_by: "created_at", sort_order: "desc", limit: 50 }));
  }, [dispatch, search, categoryFilter, brandFilter, statusFilter]);

  const toggleSelect = (id: number) => setSelected((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  const toggleSelectAll = () => setSelected((prev) => prev.length === products.length ? [] : products.map((p) => p.id));

  const handleBulkStatus = async () => {
    if (!selected.length) return;
    setSubmitting(true);
    await dispatch(bulkUpdateProductStatus({ productIds: selected, status: newStatus }));
    setSubmitting(false);
    setBulkStatusOpen(false);
    setSelected([]);
  };

  const handleBulkCategory = async () => {
    if (!selected.length || !newCategoryId) return;
    setSubmitting(true);
    await dispatch(bulkUpdateProductCategory({ productIds: selected, categoryId: Number(newCategoryId) }));
    setSubmitting(false);
    setBulkCategoryOpen(false);
    setSelected([]);
  };

  const handleBulkDelete = async () => {
    if (!selected.length) return;
    if (!confirm(`Delete ${selected.length} products?`)) return;
    await dispatch(bulkDeleteProducts(selected));
    setSelected([]);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Products</Typography>
        <Button variant="contained" onClick={() => navigate("/admin/products/new")}>Create Product</Button>
      </Stack>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} mb={3} alignItems="center">
        <TextField size="small" placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} sx={{ minWidth: 220 }} />
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Category</InputLabel>
          <Select value={categoryFilter} label="Category" onChange={(e) => setCategoryFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            {categories.map((cat) => (<MenuItem key={cat.id} value={String(cat.id)}>{cat.name}</MenuItem>))}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Brand</InputLabel>
          <Select value={brandFilter} label="Brand" onChange={(e) => setBrandFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            {brands.map((b) => (<MenuItem key={b.id} value={String(b.id)}>{b.name}</MenuItem>))}
          </Select>
        </FormControl>
        <TextField select size="small" label="Status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} sx={{ minWidth: 140 }}>
          <MenuItem value="">All</MenuItem>
          <MenuItem value="draft">Draft</MenuItem>
          <MenuItem value="active">Active</MenuItem>
          <MenuItem value="out_of_stock">Out of Stock</MenuItem>
          <MenuItem value="archived">Archived</MenuItem>
        </TextField>
      </Stack>
      {selected.length > 0 && (
        <Stack direction="row" spacing={1} mb={2}>
          <Button variant="outlined" size="small" onClick={() => setBulkStatusOpen(true)}>Change Status</Button>
          <Button variant="outlined" size="small" onClick={() => setBulkCategoryOpen(true)}>Change Category</Button>
          <Button variant="outlined" color="error" size="small" startIcon={<DeleteIcon />} onClick={handleBulkDelete}>Delete</Button>
          <Button variant="text" size="small" onClick={() => setSelected([])}>Clear</Button>
        </Stack>
      )}
      {status === "loading" ? (
        <Skeleton variant="rectangular" height={400} />
      ) : (
        <TableContainer component={Paper} elevation={0} sx={{ border: "1px solid rgba(0,0,0,0.06)" }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox"><Checkbox checked={selected.length === products.length && products.length > 0} onChange={toggleSelectAll} /></TableCell>
                <TableCell>Name</TableCell>
                <TableCell>SKU</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Brand</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Stock</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell padding="checkbox"><Checkbox checked={selected.includes(product.id)} onChange={() => toggleSelect(product.id)} /></TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.sku || "-"}</TableCell>
                  <TableCell>{product.category?.name || "-"}</TableCell>
                  <TableCell>{product.brand?.name || "-"}</TableCell>
                  <TableCell>{product.selling_price}</TableCell>
                  <TableCell>{product.available_stock ?? "-"}</TableCell>
                  <TableCell><Chip label={product.status} size="small" color={product.status === "active" ? "success" : product.status === "out_of_stock" ? "error" : "default"} /></TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => navigate(`/admin/products/${product.id}`)}><EditIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {products.length === 0 && (
                <TableRow><TableCell colSpan={9} align="center"><Typography color="text.secondary">No products found</Typography></TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      <Dialog open={bulkStatusOpen} onClose={() => setBulkStatusOpen(false)}>
        <DialogTitle>Update Status</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel>Status</InputLabel>
            <Select value={newStatus} label="Status" onChange={(e) => setNewStatus(e.target.value)}>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="out_of_stock">Out of Stock</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkStatusOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleBulkStatus} disabled={submitting || !selected.length}>Update</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={bulkCategoryOpen} onClose={() => setBulkCategoryOpen(false)}>
        <DialogTitle>Update Category</DialogTitle>
        <DialogContent>
        <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel>Category</InputLabel>
            <Select value={newCategoryId} label="Category" onChange={(e) => setNewCategoryId(e.target.value)}>
              {categories.map((cat) => (<MenuItem key={cat.id} value={String(cat.id)}>{cat.name}</MenuItem>))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkCategoryOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleBulkCategory} disabled={submitting || !selected.length || !newCategoryId}>Update</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}