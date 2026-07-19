import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCart, addCartItem, updateCartItem, deleteCartItem, clearCart, fetchCartTotals, selectCartItems } from "../store/cartSlice";
import { useToasts } from "../components/Toasts";
import {
  Box, Typography, Stack, Button, IconButton, TextField, Card, CardContent, Divider, Chip, Skeleton, InputAdornment,
} from "@mui/material";
import { Add as AddIcon, Remove as RemoveIcon, Delete as DeleteIcon, Save as SaveIcon, ArrowBack as ArrowBackIcon, ShoppingCart as CartIcon } from "@mui/icons-material";
import { formatINR } from "../utils/currency";

export function CartPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { addToast } = useToasts();
  const isAuthenticated = useAppSelector((s) => s.auth.isAuthenticated);
  const items = useAppSelector(selectCartItems);
  const status = useAppSelector((s) => s.cart.status);
  const [coupon, setCoupon] = useState("");
  const [couponMsg, setCouponMsg] = useState("");
  const [totals, setTotals] = useState<any>(null);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchCart());
    }
  }, [dispatch, isAuthenticated]);

  const refresh = () => {
    if (isAuthenticated) {
      dispatch(fetchCart());
    }
  };

  const handleQty = async (id: number, qty: number) => {
    if (qty < 1) return;
    await dispatch(updateCartItem({ itemId: id, quantity: qty }));
    addToast("Quantity updated");
    refresh();
  };

  const handleToggleSave = async (id: number, val: boolean) => {
    await dispatch(updateCartItem({ itemId: id, quantity: 1, is_saved_for_later: val }));
    addToast(val ? "Saved for later" : "Moved to cart");
    refresh();
  };

  const handleRemove = async (id: number) => {
    await dispatch(deleteCartItem(id));
    addToast("Item removed");
    refresh();
  };

  const handleClear = async () => {
    await dispatch(clearCart());
    addToast("Cart cleared");
    refresh();
  };

  const handleApplyCoupon = async () => {
    if (!isAuthenticated) return;
    const res: any = await dispatch(fetchCartTotals(coupon));
    setTotals(res.payload || res.meta?.arg);
    setCouponMsg(res.payload?.message || (res.payload?.coupon ? "Coupon applied" : "Invalid coupon"));
  };

  const subtotal = useMemo(() => {
    return isAuthenticated
      ? items.reduce((s, i) => s + (i.product?.selling_price || 0) * i.quantity, 0)
      : 0;
  }, [isAuthenticated, items]);

  const grandTotal = useMemo(() => {
    const shipping = subtotal >= 1000 ? 0 : 50;
    const gst = Math.round(subtotal * 0.18);
    const discount = totals?.discount || 0;
    return subtotal + gst + shipping - discount;
  }, [subtotal, totals]);

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    navigate("/checkout");
  };

  if (status === "loading") return <Skeleton variant="rectangular" height={400} />;

  if (!isAuthenticated) {
    return (
      <Box sx={{ mt: 4, textAlign: "center", py: 4 }}>
        <CartIcon sx={{ fontSize: 64, color: "#9CA3AF", mb: 2 }} />
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>Sign in to view your cart</Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>Your local cart items ({items.length}) will be synced after login</Typography>
        <Button variant="contained" onClick={() => navigate("/login")}>Login / Register</Button>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <IconButton onClick={() => navigate(-1)}><ArrowBackIcon /></IconButton>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Shopping Cart</Typography>
        <Chip icon={<CartIcon />} label={`${items.length} items`} />
      </Stack>
      <Stack direction={{ xs: "column", md: "row" }} spacing={3}>
        <Box sx={{ flex: 2 }}>
          <Stack spacing={2}>
            {items.map((item) => (
              <Card key={item.id} sx={{ border: "1px solid rgba(0,0,0,0.06)" }}>
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
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{item.product?.name}</Typography>
                      <Typography variant="body2" color="text.secondary">{formatINR(item.product?.selling_price || 0)}</Typography>
                    </Box>
                    <Stack direction="row" alignItems="center" sx={{ border: "1px solid rgba(0,0,0,0.1)", borderRadius: 2 }}>
                      <IconButton size="small" onClick={() => handleQty(item.id, item.quantity - 1)}><RemoveIcon /></IconButton>
                      <Typography sx={{ minWidth: 32, textAlign: "center" }}>{item.quantity}</Typography>
                      <IconButton size="small" onClick={() => handleQty(item.id, item.quantity + 1)}><AddIcon /></IconButton>
                    </Stack>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{formatINR((item.product?.selling_price || 0) * item.quantity)}</Typography>
                    <IconButton color={item.is_saved_for_later ? "primary" : "default"} onClick={() => handleToggleSave(item.id, !item.is_saved_for_later)}><SaveIcon /></IconButton>
                    <IconButton color="error" onClick={() => handleRemove(item.id)}><DeleteIcon /></IconButton>
                  </Stack>
                </CardContent>
              </Card>
            ))}
            {items.length === 0 && (
              <Box sx={{ textAlign: "center", py: 4 }}>
                <CartIcon sx={{ fontSize: 48, color: "#9CA3AF", mb: 2 }} />
                <Typography variant="h6" sx={{ color: "#6B7280" }}>Your cart is empty</Typography>
              </Box>
            )}
          </Stack>
          {items.length > 0 && <Button variant="outlined" color="error" sx={{ mt: 2 }} onClick={handleClear}>Clear Cart</Button>}
        </Box>
        <Box sx={{ flex: 1 }}>
          <Card sx={{ border: "1px solid rgba(0,0,0,0.06)" }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>Summary</Typography>
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between"><Typography>Subtotal</Typography><Typography>{formatINR(subtotal)}</Typography></Stack>
                <Stack direction="row" justifyContent="space-between"><Typography>GST (18%)</Typography><Typography>{formatINR(Math.round(subtotal * 0.18))}</Typography></Stack>
                <Stack direction="row" justifyContent="space-between"><Typography>Shipping</Typography><Typography>{subtotal >= 1000 ? "FREE" : formatINR(50)}</Typography></Stack>
                {totals?.discount > 0 && (
                  <Stack direction="row" justifyContent="space-between"><Typography color="success.main">Discount</Typography><Typography>- {formatINR(totals.discount)}</Typography></Stack>
                )}
                <Divider />
                <Stack direction="row" justifyContent="space-between"><Typography variant="h6">Grand Total</Typography><Typography variant="h6" color="primary">{formatINR(grandTotal)}</Typography></Stack>
              </Stack>
              <Stack direction="row" spacing={1} mt={2}>
                <TextField size="small" fullWidth placeholder="Coupon code" value={coupon} onChange={(e) => setCoupon(e.target.value)} InputProps={{ startAdornment: <InputAdornment position="start">#</InputAdornment> }} />
                <Button variant="outlined" onClick={handleApplyCoupon}>Apply</Button>
              </Stack>
              {couponMsg && (
                <Typography variant="caption" color={couponMsg.toLowerCase().includes("invalid") ? "error" : "success.main"}>{couponMsg}</Typography>
              )}
              <Button variant="contained" fullWidth size="large" sx={{ mt: 3 }} onClick={handleCheckout}>Proceed to Checkout</Button>
            </CardContent>
          </Card>
        </Box>
      </Stack>
    </Box>
  );
}