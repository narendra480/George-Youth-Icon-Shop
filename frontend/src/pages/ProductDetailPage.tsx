import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchProductById } from "../store/productSlice";
import { fetchCategories } from "../store/categorySlice";
import { addCartItem } from "../store/cartSlice";
import { addToWishlist, removeFromWishlist, fetchWishlist, selectWishlistItems, selectIsProductInWishlist } from "../store/wishlistSlice";
import { useToasts } from "../components/Toasts";
import {
  Box, Typography, Stack, Button, Chip, Skeleton, TextField, MenuItem, FormControl, InputLabel, Select, IconButton, Tabs, Tab, Paper,
} from "@mui/material";
import { Add as AddIcon, Remove as RemoveIcon, FavoriteBorder as FavoriteIcon, Share as ShareIcon, ArrowBack as ArrowBackIcon, ShoppingCart as CartIcon } from "@mui/icons-material";
import { formatINR } from "../utils/currency";
import type { Product } from "../types/product";

export function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { addToast } = useToasts();
  const product = useAppSelector((s) => s.products.items.find((p) => String(p.id) === id));
  const status = useAppSelector((s) => s.products.status);
  const wishlist = useAppSelector(selectWishlistItems);
  const isWishlisted = useAppSelector(selectIsProductInWishlist(Number(id) || 0));
  const [qty, setQty] = useState(1);
  const [selectedVariant, setSelectedVariant] = useState<any>(null);
  const [tab, setTab] = useState(0);

  useEffect(() => {
    if (id) {
      dispatch(fetchProductById(Number(id)));
    }
  }, [dispatch, id]);

  const handleAddToCart = async () => {
    if (!product) return;
    try {
      await dispatch(addCartItem({ product_id: product.id, quantity: qty, variant_id: selectedVariant })).unwrap();
      addToast("Added to cart");
      navigate("/cart");
    } catch (e) {
      addToast("Failed to add to cart", "error");
    }
  };

  const handleToggleWishlist = async () => {
    if (!product) return;
    if (isWishlisted) {
      await dispatch(removeFromWishlist(product.id));
      addToast("Removed from wishlist");
    } else {
      await dispatch(addToWishlist({ product_id: product.id, variant_id: selectedVariant }));
      addToast("Added to wishlist");
    }
  };

  if (status === "loading" || !product) {
    return (
      <Box sx={{ mt: 4 }}>
        <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 3, mb: 3 }} />
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="40%" />
      </Box>
    );
  }

  const imageUrl = product.images?.[0]?.image_path;
  const youSave = product.you_save || 0;
  const available = product.available_stock ?? 0;

  return (
    <Box sx={{ mt: 4 }}>
      <Stack direction="row" spacing={2} alignItems="center" mb={3}>
        <IconButton onClick={() => navigate(-1)}><ArrowBackIcon /></IconButton>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>{product.name}</Typography>
      </Stack>
      <Stack direction={{ xs: "column", md: "row" }} spacing={4}>
        <Box sx={{ flex: 1 }}>
          <Paper sx={{ borderRadius: 3, overflow: "hidden", bgcolor: "#F8FAFC", height: 400, display: "flex", alignItems: "center", justifyContent: "center" }}>
            {imageUrl ? <Box component="img" src={imageUrl} alt={product.name} sx={{ width: "100%", height: "100%", objectFit: "cover" }} /> : <Typography variant="h1">👟</Typography>}
          </Paper>
          <Stack direction="row" spacing={1} mt={2}>
            {product.images?.slice(0, 5).map((img, idx) => (
              <Paper key={idx} sx={{ width: 64, height: 64, borderRadius: 2, overflow: "hidden", cursor: "pointer" }}>
                <Box component="img" src={img.image_path} alt="" sx={{ width: "100%", height: "100%", objectFit: "cover" }} />
              </Paper>
            ))}
          </Stack>
        </Box>
        <Box sx={{ flex: 1 }}>
          <Stack direction="row" spacing={1} mb={2}>
            {product.is_new_arrival && <Chip label="New" size="small" color="secondary" />}
            {product.is_best_seller && <Chip label="Best Seller" size="small" color="primary" />}
            {available <= 0 && <Chip label="Out of Stock" size="small" color="error" />}
          </Stack>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>{product.name}</Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>{product.short_description || product.description}</Typography>
          <Stack direction="row" spacing={2} alignItems="center" mb={2}>
            <Typography variant="h4" color="primary" sx={{ fontWeight: 700 }}>{formatINR(product.selling_price)}</Typography>
            {product.mrp > product.selling_price && (
              <Typography variant="h6" sx={{ textDecoration: "line-through", color: "text.secondary" }}>{formatINR(product.mrp)}</Typography>
            )}
          </Stack>
          {youSave > 0 && <Typography variant="body2" color="success.main" sx={{ mb: 2 }}>You save {formatINR(youSave)}</Typography>}
          {product.variants && product.variants.length > 0 && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Variant</InputLabel>
              <Select value={selectedVariant || ""} label="Variant" onChange={(e) => setSelectedVariant(e.target.value)}>
                {product.variants.map((v) => (
                  <MenuItem key={v.id} value={v.id}>{v.name || v.sku} - {formatINR(v.price || product.selling_price)}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
          <Stack direction="row" spacing={2} alignItems="center" mb={3}>
            <Stack direction="row" alignItems="center" sx={{ border: "1px solid rgba(0,0,0,0.1)", borderRadius: 2 }}>
              <IconButton size="small" onClick={() => setQty((q) => Math.max(1, q - 1))}><RemoveIcon /></IconButton>
              <Typography sx={{ minWidth: 40, textAlign: "center" }}>{qty}</Typography>
              <IconButton size="small" onClick={() => setQty((q) => Math.min(available, q + 1))}><AddIcon /></IconButton>
            </Stack>
            <Button variant="contained" size="large" startIcon={<CartIcon />} disabled={available <= 0} onClick={handleAddToCart}>Add to Cart</Button>
            <IconButton onClick={handleToggleWishlist} color={isWishlisted ? "error" : "default"}><FavoriteIcon /></IconButton>
            <IconButton onClick={() => addToast("Shared", "info")}><ShareIcon /></IconButton>
          </Stack>
          <Typography variant="caption" color="text.secondary">SKU: {product.sku || "-"}</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>HSN: {product.hsn_code || "-"}</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>GST: {product.gst_percentage ?? "-"}%</Typography>
          <Box sx={{ mt: 2 }}>
            <Tabs value={tab} onChange={(_, v) => setTab(v)}>
              <Tab label="Description" />
              <Tab label="Specifications" />
              <Tab label="Shipping" />
            </Tabs>
            <Box sx={{ mt: 2 }}>
              {tab === 0 && <Typography variant="body2" color="text.secondary">{product.description || product.short_description || "No description"}</Typography>}
              {tab === 1 && <Typography variant="body2" color="text.secondary">{product.specifications ? JSON.stringify(product.specifications) : "No specifications"}</Typography>}
              {tab === 2 && <Typography variant="body2" color="text.secondary">Standard delivery in 5-7 business days. Free shipping on orders above ₹1000.</Typography>}
            </Box>
          </Box>
        </Box>
      </Stack>
    </Box>
  );
}