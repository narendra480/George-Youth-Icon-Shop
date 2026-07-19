import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import {
  AppBar,
  Box,
  Button,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  InputBase,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Stack,
  Chip,
  Tooltip,
} from "@mui/material";
import {
  Search as SearchIcon,
  FavoriteBorder,
  ShoppingCart,
  Person,
  Notifications,
  ArrowDropDown,
  Close,
  Delete,
  Add,
  Remove,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { Link as RouterLink, useNavigate, useLocation } from "react-router-dom";
import { appRoutes } from "../nav/routes";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCategories, selectCategoriesStatus } from "../store/categorySlice";
import { fetchNotifications } from "../store/notificationSlice";
import { formatINR } from "../utils/currency";
import { fetchCart } from "../store/cartSlice";
import { fetchWishlist } from "../store/wishlistSlice";
import type { Category } from "../types/category";
import type { Notification } from "../store/notificationSlice";

export function Header() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const user = useAppSelector((state) => state.auth.user);
  const cartItems = useAppSelector((state) => state.cart.items);
  const cartLocalItems = useAppSelector((state) => state.cart.localItems);
  const wishlistItems = useAppSelector((state) => state.wishlist.items);
  const wishlistLocalItems = useAppSelector((state) => state.wishlist.localItems);
  const categories = useAppSelector((state) => state.categories.items);
  const categoriesStatus = useAppSelector(selectCategoriesStatus);
  const notifications = useAppSelector((state) => state.notifications.items);
  const unreadCount = useAppSelector((state) => state.notifications.unreadCount);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoriesAnchor, setCategoriesAnchor] = useState<null | HTMLElement>(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null);
  const [subcategoryAnchors, setSubcategoryAnchors] = useState<Record<number, HTMLElement | null>>({});

  useEffect(() => {
    if (categoriesStatus === "idle" && !categories.length) {
      dispatch(fetchCategories());
    }
  }, [dispatch, categoriesStatus, categories.length]);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchCart());
      dispatch(fetchWishlist());
      dispatch(fetchNotifications());
    }
  }, [dispatch, isAuthenticated]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleCategoryClick = (categoryId: number, slug: string) => {
    setCategoriesAnchor(null);
    navigate(`/categories/${slug || categoryId}`);
  };

  const cartItemCount = useMemo(() => {
    return isAuthenticated
      ? cartItems.reduce((sum, item) => sum + item.quantity, 0)
      : cartLocalItems.reduce((sum, item) => sum + item.quantity, 0);
  }, [isAuthenticated, cartItems, cartLocalItems]);

  const wishlistCount = useMemo(() => {
    return isAuthenticated ? wishlistItems.length : wishlistLocalItems.length;
  }, [isAuthenticated, wishlistItems, wishlistLocalItems]);

  const handleSubcategoryMouseEnter = useCallback((catId: number, e: React.MouseEvent<HTMLElement>) => {
    setSubcategoryAnchors((prev) => ({ ...prev, [catId]: e.currentTarget }));
  }, []);

  const handleSubcategoryMouseLeave = useCallback((catId: number) => {
    setSubcategoryAnchors((prev) => ({ ...prev, [catId]: null }));
  }, []);

  const renderCategoryMenu = useCallback(
    (category: Category, level = 0) => {
      const hasChildren = category.children && category.children.length > 0;
      return (
        <Box key={category.id}>
          <MenuItem
            onClick={() => handleCategoryClick(category.id, category.slug)}
            onMouseEnter={hasChildren ? (e) => handleSubcategoryMouseEnter(category.id, e) : undefined}
            sx={{
              py: 1.5,
              pl: level * 2 + 1.5,
              bgcolor: level === 0 ? "#ffffff" : "#F8FAFC",
              "&:hover": { bgcolor: "#F1F5F9" },
              position: "relative",
            }}
          >
            <ListItemText primary={category.name} />
            {hasChildren && <ArrowDropDown sx={{ ml: "auto", transform: "rotate(-90deg)" }} />}
          </MenuItem>
          {hasChildren && subcategoryAnchors[category.id] && (
            <Menu
              open={Boolean(subcategoryAnchors[category.id])}
              anchorEl={subcategoryAnchors[category.id]}
              onClose={() => handleSubcategoryMouseLeave(category.id)}
              MenuListProps={{ sx: { py: 0 }, style: { left: "100%", top: 0 } }}
            >
              {category.children!.map((child) => renderCategoryMenu(child, level + 1))}
            </Menu>
          )}
        </Box>
      );
    },
    [subcategoryAnchors, handleSubcategoryMouseEnter, handleSubcategoryMouseLeave]
  );

  const cartSubtotal = useMemo(() => {
    return cartItems.reduce((sum, item) => {
      const price = item.product?.selling_price || item.product?.mrp || 0;
      return sum + price * item.quantity;
    }, 0);
  }, [cartItems]);

  const handleCartAction = (action: string) => {
    if (!isAuthenticated) {
      navigate(appRoutes.login);
      return;
    }
    if (action === "view") {
      navigate(appRoutes.cart);
    } else if (action === "checkout") {
      navigate(appRoutes.checkout);
    }
  };

  return (
    <AppBar
      position="sticky"
      color="default"
      elevation={0}
      sx={{
        bgcolor: "#ffffff",
        boxShadow: "0 2px 20px rgba(0,0,0,0.08)",
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between", py: 1 }}>
        {/* Logo */}
        <Typography
          component={RouterLink}
          to={appRoutes.home}
          sx={{
            color: "#1E3A8A",
            textDecoration: "none",
            fontWeight: 800,
            fontSize: "1.5rem",
          }}
        >
          George's Youth Icon Shop
        </Typography>

        {/* Search Bar */}
        <Box
          component="form"
          onSubmit={handleSearch}
          sx={{
            flex: 1,
            maxWidth: 500,
            mx: 4,
            display: { xs: "none", md: "block" },
          }}
        >
          <Box sx={{
            display: "flex",
            alignItems: "center",
            bgcolor: "#F8FAFC",
            borderRadius: 3,
            px: 2,
          }}>
            <SearchIcon sx={{ color: "#6B7280", mr: 1 }} />
            <InputBase
              placeholder="Search footwear, brands..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              sx={{ flex: 1, py: 1 }}
            />
          </Box>
        </Box>

        {/* Navigation */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {/* Categories Dropdown */}
          <Button
            color="inherit"
            endIcon={<ArrowDropDown />}
            onClick={(e) => setCategoriesAnchor(e.currentTarget)}
            sx={{
              color: "#374151",
              textTransform: "none",
              fontWeight: 500,
              display: { xs: "none", md: "flex" },
            }}
          >
            Categories
          </Button>

          <Menu
            anchorEl={categoriesAnchor}
            open={Boolean(categoriesAnchor)}
            onClose={() => setCategoriesAnchor(null)}
            MenuListProps={{ sx: { py: 0, minWidth: 200 } }}
            PaperProps={{ sx: { maxHeight: 400 } }}
          >
            {categoriesStatus === "loading" && (
              <MenuItem disabled>Loading...</MenuItem>
            )}
            {categories.length === 0 && categoriesStatus === "idle" && (
              <MenuItem disabled>
                <Box sx={{ textAlign: "center", py: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Loading categories...
                  </Typography>
                </Box>
              </MenuItem>
            )}
            {categories.map((category) => renderCategoryMenu(category))}
          </Menu>

          {/* Wishlist */}
          <IconButton
            component={RouterLink}
            to={appRoutes.wishlist}
            sx={{ color: "#374151" }}
          >
            <Badge badgeContent={wishlistCount} color="error">
              <FavoriteBorder />
            </Badge>
          </IconButton>

          {/* Cart */}
          <IconButton
            component={RouterLink}
            to={appRoutes.cart}
            sx={{ color: "#374151", position: "relative" }}
          >
            <Badge badgeContent={cartItemCount} color="error">
              <ShoppingCart />
            </Badge>
          </IconButton>

          {/* Notifications - never redirect, just show drawer */}
          <IconButton
            onClick={(e) => setNotificationsAnchor(e.currentTarget)}
            sx={{ color: "#374151" }}
          >
            <Badge badgeContent={isAuthenticated ? unreadCount : 0} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          <Menu
            anchorEl={notificationsAnchor}
            open={Boolean(notificationsAnchor)}
            onClose={() => setNotificationsAnchor(null)}
            PaperProps={{ sx: { width: 320, maxHeight: 500 } }}
          >
            {isAuthenticated ? (
              <>
                <Box sx={{ p: 2, pb: 1 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Notifications ({unreadCount})
                  </Typography>
                </Box>
                <Divider />
                {notifications.length === 0 ? (
                  <Box sx={{ p: 3, textAlign: "center" }}>
                    <Notifications sx={{ fontSize: 48, color: "#9CA3AF", mb: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      No notifications yet
                    </Typography>
                  </Box>
                ) : (
                  notifications.slice(0, 5).map((notification: Notification) => (
                    <MenuItem
                      key={notification.id}
                      onClick={() => {
                        if (!notification.is_read) {
                          dispatch({ type: "notifications/markRead", payload: notification.id });
                        }
                        setNotificationsAnchor(null);
                      }}
                      sx={{
                        bgcolor: notification.is_read ? "inherit" : "#F8FAFC",
                        borderLeft: notification.is_read ? "none" : "3px solid #1E3A8A",
                      }}
                    >
                      <ListItemText
                        primary={notification.title}
                        secondary={notification.message}
                        primaryTypographyProps={{ fontWeight: notification.is_read ? 400 : 600 }}
                      />
                    </MenuItem>
                  ))
                )}
              </>
            ) : (
              <Box sx={{ p: 3, textAlign: "center" }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Sign in to receive order updates, offers and alerts.
                </Typography>
                <Button variant="contained" onClick={() => {
                  setNotificationsAnchor(null);
                  navigate(appRoutes.login);
                }}>Login</Button>
              </Box>
            )}
          </Menu>

          {/* Profile/Logout */}
          {isAuthenticated ? (
            <Button
              component={RouterLink}
              to={appRoutes.profile}
              startIcon={<Person />}
              color="inherit"
              sx={{ color: "#374151", textTransform: "none", fontWeight: 500 }}
            >
              {user?.first_name || "Profile"}
            </Button>
          ) : (
            <>
              <Button component={RouterLink} to={appRoutes.login} color="inherit" sx={{ color: "#374151", textTransform: "none", fontWeight: 500 }}>
                Login
              </Button>
              <Button component={RouterLink} to={appRoutes.register} variant="contained" sx={{ borderRadius: 2 }}>
                Register
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}