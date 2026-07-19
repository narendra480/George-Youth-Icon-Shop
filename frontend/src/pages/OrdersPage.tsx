import { useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Container,
  Typography,
  Stack,
  Skeleton,
  Button,
} from "@mui/material";
import { motion } from "framer-motion";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchOrders } from "../store/orderSlice";
import { formatINR } from "../utils/currency";
import { Link as RouterLink } from "react-router-dom";

const statusColors: Record<string, "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"> = {
  pending: "warning",
  confirmed: "info",
  packed: "primary",
  shipped: "secondary",
  delivered: "success",
  cancelled: "error",
  returned: "error",
};

export function OrdersPage() {
  const dispatch = useAppDispatch();
  const orders = useAppSelector((state) => state.orders.items);
  const status = useAppSelector((state) => state.orders.status);

  useEffect(() => {
    dispatch(fetchOrders());
  }, [dispatch]);

  if (status === "loading") {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={120} sx={{ mb: 2 }} />)}
      </Container>
    );
  }

  if (orders.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: "center" }}>
        <Typography variant="h5" mb={2}>No orders found</Typography>
        <Button component={RouterLink} to="/products" variant="contained">Shop Now</Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} mb={3}>My Orders</Typography>
      {orders.map((order) => (
        <motion.div key={order.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6">{order.order_number}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(order.created_at).toLocaleDateString("en-IN")}
                  </Typography>
                </Box>
                <Chip label={order.status} color={statusColors[order.status] || "default"} />
              </Stack>
              <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}>
                <Typography>Total: {formatINR(order.total_amount)}</Typography>
                <Button component={RouterLink} to={`/orders/${order.id}`} size="small">
                  View Details
                </Button>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </Container>
  );
}