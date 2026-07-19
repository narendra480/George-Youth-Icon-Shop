import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchWishlist, removeFromWishlist, selectWishlistItems, selectWishlistCount } from "../store/wishlistSlice";
import { useToasts } from "../components/Toasts";
import {
  Box, Typography, Stack, Button, IconButton, Card, CardContent, Skeleton,
} from "@mui/material";
import { Delete as DeleteIcon, ShoppingCart as CartIcon, FavoriteBorder } from "@mui/icons-material";
import { formatINR } from "../utils/currency";
import { addCartItem } from "../store/cartSlice";

export function WishlistPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { addToast } = useToasts();
  const isAuthenticated = useAppSelector((s) => s.auth.isAuthenticated);
  const items = useAppSelector(selectWishlistItems);
  const status = useAppSelector((s) => s.wishlist.status);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchWishlist());
    }
  }, [dispatch, isAuthenticated]);

  const handleRemove = async (productId: number) => {
    await dispatch(removeFromWishlist(productId));
    addToast("Removed from wishlist");
  };

  const handleAddToCart = (productId: number) => {
    dispatch(addCartItem({ product_id: productId, quantity: 1 }));
    addToast("Added to cart");
  };

  const handleLoginRedirect = () => {
    navigate("/login");
  };

  if (status === "loading") return <Skeleton variant="rectangular" height={400} />;

  return (
    <Box sx={{ mt: 4 }}>
      {!isAuthenticated && (
        <Box sx={{ textAlign: "center", py: 4, mb: 2, border: "1px dashed #E5E7EB", borderRadius: 2 }}>
          <FavoriteBorder sx={{ fontSize: 48, color: "#9CA3AF", mb: 2 }} />
          <Typography variant="h6" sx={{ color: "#6B7280", mb: 1 }}>
            Sign in to sync your wishlist across devices
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Your local wishlist ({items.length} items) will be merged after login
          </Typography>
        </Box>
      )}
      
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>My Wishlist</Typography>
      <Stack spacing={2}>
        {items.map((item: any) => (
          <Card key={item.id || item.product_id} sx={{ border: "1px solid rgba(0,0,0,0.06)" }}>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center">
                <Box sx={{ width: 80, height: 80, borderRadius: 2, bgcolor: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden", flexShrink: 0 }}>
                  {item.product?.images?.[0]?.image_path ? (
                    <Box component="img" src={item.product.images[0].image_path} alt={item.product.name} sx={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    "👟"
                  )}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                    {item.product?.name || `Product ${item.product_id}`}
                  </Typography>
                  {item.product?.category && (
                    <Typography variant="body2" color="text.secondary">
                      {item.product?.category?.name}
                    </Typography>
                  )}
                  <Typography variant="subtitle1" color="primary" sx={{ fontWeight: 700 }}>
                    {formatINR(item.product?.selling_price || 0)}
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1}>
                  <Button variant="contained" size="small" startIcon={<CartIcon />} onClick={() => handleAddToCart(item.product_id)}>
                    Add to Cart
                  </Button>
                  <IconButton color="error" onClick={() => handleRemove(item.product_id)}>
                    <DeleteIcon />
                  </IconButton>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        ))}
        {items.length === 0 && (
          <Box sx={{ textAlign: "center", py: 4 }}>
            <FavoriteBorder sx={{ fontSize: 48, color: "#9CA3AF", mb: 2 }} />
            <Typography variant="h6" sx={{ color: "#6B7280" }}>
              Your wishlist is empty
            </Typography>
          </Box>
        )}
      </Stack>
    </Box>
  );
}