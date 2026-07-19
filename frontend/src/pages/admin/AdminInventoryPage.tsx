import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { fetchProducts } from "../../store/productSlice";
import {
  Box, Typography, Stack, TextField, MenuItem, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Skeleton, Dialog, DialogTitle, DialogContent, DialogActions, Button, FormControl, InputLabel, Select, IconButton,
} from "@mui/material";
import { Edit as EditIcon } from "@mui/icons-material";
import { formatINR } from "../../utils/currency";

export function AdminInventoryPage() {
  const dispatch = useAppDispatch();
  const products = useAppSelector((s) => s.products.items);
  const status = useAppSelector((s) => s.products.status);
  const [search, setSearch] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const [adjustment, setAdjustment] = useState<{ type: "stock_in" | "stock_out" | "adjustment"; quantity: number; notes: string }>({ type: "stock_in", quantity: 0, notes: "" });

  useEffect(() => {
    dispatch(fetchProducts({ search: search || undefined, sort_by: "created_at", sort_order: "desc", limit: 100 }));
  }, [dispatch, search]);

  const openAdjust = (product: any) => {
    setSelectedProduct(product);
    setAdjustment({ type: "stock_in", quantity: 0, notes: "" });
    setOpen(true);
  };

  const handleSubmit = async () => {
    if (!selectedProduct || adjustment.quantity <= 0) return;
    const url = `/inventory/${adjustment.type === "adjustment" ? "adjustment" : adjustment.type}`;
    const body: any = { product_id: selectedProduct.id, notes: adjustment.notes };
    if (adjustment.type === "adjustment") {
      body.new_stock = adjustment.quantity;
    } else {
      body.quantity = adjustment.quantity;
      if (selectedProduct.variants?.length) body.variant_id = selectedProduct.variants[0].id;
    }
    // await api.post(url, body)
    setOpen(false);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>Inventory</Typography>
      <Stack direction="row" spacing={2} mb={3} alignItems="center">
        <TextField size="small" placeholder="Search products..." value={search} onChange={(e) => setSearch(e.target.value)} sx={{ minWidth: 260 }} />
      </Stack>
      {status === "loading" ? (
        <Skeleton variant="rectangular" height={400} />
      ) : (
        <TableContainer component={Paper} elevation={0} sx={{ border: "1px solid rgba(0,0,0,0.06)" }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>SKU</TableCell>
                <TableCell>Available</TableCell>
                <TableCell>Reserved</TableCell>
                <TableCell>Reorder</TableCell>
                <TableCell>Alert</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.sku || "-"}</TableCell>
                  <TableCell>{product.available_stock ?? 0}</TableCell>
                  <TableCell>0</TableCell>
                  <TableCell>0</TableCell>
                  <TableCell><Chip label={product.available_stock !== undefined && product.available_stock <= 0 ? "Low" : "OK"} size="small" color={product.available_stock !== undefined && product.available_stock <= 0 ? "error" : "success"} /></TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => openAdjust(product)}><EditIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {products.length === 0 && (
                <TableRow><TableCell colSpan={7} align="center"><Typography color="text.secondary">No products found</Typography></TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Adjust Inventory</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1, minWidth: 320 }}>
            <TextField label="Product" value={selectedProduct?.name || ""} InputProps={{ readOnly: true }} />
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select value={adjustment.type} label="Type" onChange={(e) => setAdjustment({ ...adjustment, type: e.target.value as any })}>
                <MenuItem value="stock_in">Stock In</MenuItem>
                <MenuItem value="stock_out">Stock Out</MenuItem>
                <MenuItem value="adjustment">Adjustment</MenuItem>
              </Select>
            </FormControl>
            <TextField label={adjustment.type === "adjustment" ? "New Stock" : "Quantity"} type="number" value={adjustment.quantity} onChange={(e) => setAdjustment({ ...adjustment, quantity: Number(e.target.value) })} />
            <TextField label="Notes" multiline rows={3} value={adjustment.notes} onChange={(e) => setAdjustment({ ...adjustment, notes: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={adjustment.quantity <= 0}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}