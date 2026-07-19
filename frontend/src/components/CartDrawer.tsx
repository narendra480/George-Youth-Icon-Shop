import { useEffect, useMemo, useCallback, useState } from "react";
import {
  Box,
  Drawer,
  Typography,
  IconButton,
  Button,
  Divider,
  Stack,
  Chip,
} from "@mui/material";
import { Close, Delete, ShoppingCart, Add, Remove } from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCart, updateCartItem, deleteCartItem } from "../store/cartSlice";
import { formatINR } from "../utils/currency";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { appRoutes } from "../nav/routes";

export function CartDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const cartItems = useAppSelector((state) => state.cart.items);
  const cartLocalItems = useAppSelector((state) => state.cart.localItems);
  const [products, setProducts] = useState<Record<number, any>>({});

  useEffect(() => {
    if (open && isAuthenticated) {
      dispatch(fetchCart());
    }
  }, [dispatch, open, isAuthenticated]);

  const displayItems = useMemo(() => {
    if (isAuthenticated) {
      return cartItems;
    }
    return cartLocalItems.map((item: any, idx: number) => ({
      id: idx,
      product_id: item.product_id,
      variant_id: item.variant_id,
      quantity: item.quantity,
      product: products[item.product_id] || {
        id: item.product_id,
        name: `Product ${item.product_id}`,
        selling_price: 0,
        mrp: 0,
        images: [],
      },
      variant: item.variant_id ? undefined : undefined,
    }));
  }, [isAuthenticated, cartItems, cartLocalItems, products]);

  const handleQuantityChange = useCallback(
    (itemId: number, newQuantity: number, product_id?: number) => {
      if (isAuthenticated) {
        if (newQuantity > 0) {
          dispatch(updateCartItem({ itemId, quantity: newQuantity }));
        }
      } else if (product_id !== undefined) {
        dispatch({ type: "cart/updateLocalCartItem", payload: { product_id, quantity: newQuantity } });
      }
    },
    [dispatch, isAuthenticated]
  );

  const handleRemove = useCallback(
    (itemId: number, product_id?: number) => {
      if (isAuthenticated) {
        dispatch(deleteCartItem(itemId));
      } else if (product_id !== undefined) {
        dispatch({ type: "cart/removeLocalCartItem", payload: { product_id } });
      }
    },
    [dispatch, isAuthenticated]
  );

const subtotal = useMemo(() => {
    if (isAuthenticated) {
      return cartItems.reduce((sum, item) => {
        const price = item.product?.selling_price || item.product?.mrp || 0;
        return sum + price * item.quantity;
      }, 0);
    }
    return cartLocalItems.reduce((sum, item: any) => {
      return sum + (item.price || 0) * item.quantity;
    }, 0);
  }, [isAuthenticated, cartItems, cartLocalItems]);

  const handleViewCart = () => {
    onClose();
    if (!isAuthenticated) {
      navigate(appRoutes.login);
      return;
    }
    navigate(appRoutes.cart);
  };

  const handleCheckout = () => {
    onClose();
    if (!isAuthenticated) {
      navigate(appRoutes.login);
      return;
    }
    navigate(appRoutes.checkout);
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: "100%", sm: 400 },
          bgcolor: "#ffffff",
        },
      }}
    >
      <Box sx={{ p: 3, height: "100%", display: "flex", flexDirection: "column" }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Shopping Cart ({displayItems.length} items)
          </Typography>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Stack>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ flex: 1, overflow: "auto" }}>
          <AnimatePresence>
            {displayItems.map((item: any) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Box sx={{ display: "flex", gap: 2, mb: 2, pb: 2, borderBottom: "1px solid #E5E7EB" }}>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      borderRadius: 2,
                      overflow: "hidden",
                      bgcolor: "#F8FAFC",
                    }}
                  >
                    <img
                      src={item.product?.images?.[0]?.image_path || "/placeholder-shoe.jpg"}
                      alt={item.product?.name}
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {item.product?.name}
                    </Typography>
                    {item.variant && (
                      <Typography variant="caption" sx={{ color: "#6B7280" }}>
                        {item.variant.name}
                      </Typography>
                    )}
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleQuantityChange(item.id, item.quantity - 1, item.product_id)}
                        disabled={item.quantity <= 1}
                      >
                        <Remove fontSize="small" />
                      </IconButton>
                      <Typography>{item.quantity}</Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleQuantityChange(item.id, item.quantity + 1, item.product_id)}
                      >
                        <Add fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleRemove(item.id, item.product_id)}
                        sx={{ ml: "auto" }}
                      >
                        <Delete fontSize="small" color="error" />
                      </IconButton>
                    </Stack>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: "#1E3A8A", mt: 1 }}>
                      {formatINR((item.product?.selling_price || item.product?.mrp || 0) * item.quantity)}
                    </Typography>
                  </Box>
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>

          {displayItems.length === 0 && (
            <Box sx={{ textAlign: "center", py: 4 }}>
              <ShoppingCart sx={{ fontSize: 48, color: "#9CA3AF", mb: 2 }} />
              <Typography variant="h6" sx={{ color: "#6B7280" }}>
                Your cart is empty
              </Typography>
            </Box>
          )}
        </Box>

        {displayItems.length > 0 && isAuthenticated && (
          <Box sx={{ mt: 2 }}>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography>Subtotal</Typography>
                <Typography>{formatINR(subtotal)}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography>GST (18%)</Typography>
                <Typography>{formatINR(subtotal * 0.18)}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography>Shipping</Typography>
                <Chip label="Free" color="success" size="small" />
              </Stack>
              <Divider />
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Grand Total
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700, color: "#1E3A8A" }}>
                  {formatINR(subtotal * 1.18)}
                </Typography>
              </Stack>
            </Stack>

            <Stack direction="column" spacing={1} sx={{ mt: 2 }}>
              <Button
                component={RouterLink}
                to={appRoutes.cart}
                variant="outlined"
                fullWidth
                onClick={onClose}
              >
                View Cart
              </Button>
              <Button
                component={RouterLink}
                to={appRoutes.checkout}
                variant="contained"
                fullWidth
                onClick={onClose}
              >
                Checkout
              </Button>
            </Stack>
          </Box>
        )}

        {displayItems.length > 0 && !isAuthenticated && (
          <Box sx={{ mt: 2 }}>
            <Button variant="contained" fullWidth onClick={handleViewCart}>
              Login to View Cart
            </Button>
          </Box>
        )}
      </Box>
    </Drawer>
  );
}