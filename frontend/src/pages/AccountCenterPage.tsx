import { useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Container,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import {
  Person,
  ShoppingBag,
  Favorite,
  LocationOn,
  Notifications,
  Settings,
  Security,
} from "@mui/icons-material";
import { Link as RouterLink, Outlet, useLocation } from "react-router-dom";

const menuItems = [
  { to: "/account/profile", icon: <Person />, label: "My Profile" },
  { to: "/account/orders", icon: <ShoppingBag />, label: "My Orders" },
  { to: "/account/wishlist", icon: <Favorite />, label: "My Wishlist" },
  { to: "/account/addresses", icon: <LocationOn />, label: "My Addresses" },
  { to: "/account/notifications", icon: <Notifications />, label: "My Notifications" },
  { to: "/account/settings", icon: <Settings />, label: "Account Settings" },
  { to: "/account/security", icon: <Security />, label: "Security Settings" },
];

export function AccountCenterPage() {
  const location = useLocation();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} mb={3}>Account Center</Typography>
      <Box sx={{ display: "flex", gap: 3 }}>
        <Card sx={{ width: 280, flexShrink: 0 }}>
          <CardContent sx={{ p: 0 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.to} disablePadding>
                  <ListItemButton
                    component={RouterLink}
                    to={item.to}
                    selected={location.pathname === item.to}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
        <Box sx={{ flex: 1 }}>
          <Outlet />
        </Box>
      </Box>
    </Container>
  );
}