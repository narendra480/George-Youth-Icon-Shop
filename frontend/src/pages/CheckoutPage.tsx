import { useEffect, useState, useCallback } from "react";
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  Typography,
  Stack,
  Radio,
  FormControlLabel,
  TextField,
  Skeleton,
  Stepper,
  Step,
  StepLabel,
  Chip,
  Dialog,
} from "@mui/material";
import { motion } from "framer-motion";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCart, selectCartSubtotal } from "../store/cartSlice";
import { fetchAddresses, createAddress } from "../store/addressSlice";
import { createOrder } from "../store/orderSlice";
import { createRazorpayOrder, verifyPayment } from "../store/paymentSlice";
import { useToasts } from "../components/Toasts";
import { formatINR } from "../utils/currency";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { appRoutes } from "../nav/routes";

export function CheckoutPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const cartItems = useAppSelector((state) => state.cart.items);
  const addresses = useAppSelector((state) => state.addresses.items);
  const cart = useAppSelector((state) => state.cart.cart);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedAddress, setSelectedAddress] = useState<number | null>(null);
  const [couponCode, setCouponCode] = useState("");

  useEffect(() => {
    dispatch(fetchCart());
    dispatch(fetchAddresses());
  }, [dispatch]);

const { addToast } = useToasts();
const cartSubtotal = useAppSelector(selectCartSubtotal);
const razorpayOrder = useAppSelector((state) => state.payments.razorpayOrder);

const subtotal = cartSubtotal;
const gst = subtotal * 0.18;
const shipping = subtotal >= 1000 ? 0 : 50;
const total = subtotal + gst + shipping;

const handlePlaceOrder = useCallback(async () => {
    if (!selectedAddress) return;
    const orderResult: any = await dispatch(createOrder({ 
      address_id: selectedAddress!, 
      items: cartItems.map(i => ({ product_id: i.product_id, variant_id: i.variant_id, quantity: i.quantity }))
    })).unwrap();
    
    if (orderResult?.id) {
      const rzp = new (window as any).Razorpay({
key: (import.meta.env?.VITE_RAZORPAY_KEY_ID as string) || "",
        amount: Math.round(total * 100),
        currency: "INR",
        order_id: orderResult.gateway_order_id,
        name: "George's Youth Icon Shop",
        description: "Order Payment",
        handler: async (response: any) => {
          await dispatch(verifyPayment({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          })).unwrap();
          navigate("/orders/confirmation");
        },
        theme: { color: "#1E3A8A" }
      });
      rzp.open();
    }
  }, [dispatch, selectedAddress, cartItems, total, navigate]);

  const steps = ["Cart Review", "Address Selection", "Order Summary"];

  if (cartItems.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 4, textAlign: "center" }}>
          <Typography variant="h5" mb={2}>Your cart is empty</Typography>
          <Button component={RouterLink} to={appRoutes.products} variant="contained">Continue Shopping</Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          {activeStep === 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" mb={2}>Cart Items</Typography>
              {cartItems.map((item) => (
                <Box key={item.id} sx={{ display: "flex", gap: 2, mb: 2, pb: 2, borderBottom: "1px solid #E5E7EB" }}>
                  <img src={item.product?.images?.[0]?.image_path || "/placeholder-shoe.jpg"} alt={item.product?.name} style={{ width: 60, height: 60, objectFit: "cover", borderRadius: 8 }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography>{item.product?.name}</Typography>
                    <Typography variant="body2" color="text.secondary">Qty: {item.quantity}</Typography>
                  </Box>
                  <Typography>{formatINR((item.product?.offer_price || item.product?.selling_price || 0) * item.quantity)}</Typography>
                </Box>
              ))}
            </Paper>
          )}

          {activeStep === 1 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" mb={2}>Select Address</Typography>
              {addresses.map((address) => (
                <FormControlLabel
                  key={address.id}
                  control={<Radio checked={selectedAddress === address.id} onChange={() => setSelectedAddress(address.id)} />}
                  label={
                    <Box>
                      <Typography fontWeight={600}>{address.name}</Typography>
                      <Typography variant="body2">{address.house_flat}, {address.street}, {address.city}</Typography>
                      <Typography variant="body2">{address.state} - {address.pincode}</Typography>
                    </Box>
                  }
                  sx={{ width: "100%", mb: 1, p: 2, border: "1px solid #E5E7EB", borderRadius: 2 }}
                />
              ))}
              <Button variant="outlined" sx={{ mt: 2 }}>Add New Address</Button>
            </Paper>
          )}

          {activeStep === 2 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" mb={2}>Order Summary</Typography>
              <Stack spacing={1}>
                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                  <Typography>Subtotal</Typography>
                  <Typography>{formatINR(subtotal)}</Typography>
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                  <Typography>GST (18%)</Typography>
                  <Typography>{formatINR(gst)}</Typography>
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                  <Typography>Shipping</Typography>
                  <Chip label="Free" color="success" size="small" />
                </Box>
                <TextField label="Coupon Code" value={couponCode} onChange={(e) => setCouponCode(e.target.value)} size="small" />
              </Stack>
            </Paper>
          )}
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, position: "sticky", top: 20 }}>
            <Typography variant="h6" mb={2}>Grand Total</Typography>
            <Typography variant="h4" color="primary" fontWeight={700}>{formatINR(total)}</Typography>
            <Stack direction="row" spacing={1} mt={3}>
              <Button variant="outlined" onClick={() => setActiveStep(Math.max(0, activeStep - 1))} disabled={activeStep === 0}>
                Back
              </Button>
              {activeStep < steps.length - 1 ? (
                <Button variant="contained" onClick={() => setActiveStep(activeStep + 1)} disabled={activeStep === 1 && !selectedAddress}>
                  Continue
                </Button>
              ) : (
                <Button variant="contained" onClick={handlePlaceOrder} disabled={!selectedAddress}>
                  Place Order
                </Button>
              )}
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}