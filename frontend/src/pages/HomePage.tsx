import { useEffect, useState, useCallback, memo } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchFeaturedProducts, fetchBestSellers, fetchNewArrivals, fetchBrands, fetchTrendingProducts, fetchRecommendedProducts } from "../store/productSlice";
import { fetchCategoriesWithCounts } from "../store/categorySlice";
import { fetchShopSettings } from "../store/shopSettingsSlice";
import { fetchHeroBanners } from "../store/bannerSlice";
import { fetchReviews } from "../store/reviewSlice";
import { motion, AnimatePresence } from "framer-motion";
import { Box, Typography, Chip, IconButton, Button, Container, Skeleton, Stack } from "@mui/material";
import { Favorite, FavoriteBorder, ShoppingCart, ArrowBack, ArrowForward, Star, StarBorder } from "@mui/icons-material";
import { Link as RouterLink } from "react-router-dom";
import { formatINR } from "../utils/currency";
import type { Product, Brand } from "../types/product";
import type { Category } from "../types/category";
import type { Banner } from "../store/bannerSlice";
import type { Review } from "../store/reviewSlice";

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

// ProductCard Component
const ProductCard = memo(({ product, onAddToCart, onWishlist }: { 
  product: Product; 
  onAddToCart: (id: number) => void;
  onWishlist: (id: number) => void;
}) => {
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  
  const imageUrl = product.images?.[0]?.image_path || "/placeholder-shoe.jpg";
  const hasDiscount = product.mrp > product.selling_price;
  const discountPercent = hasDiscount ? Math.round((1 - product.selling_price / product.mrp) * 100) : 0;
  const averageRating = product.average_rating || 4.5;
  
  const getStockStatus = () => {
    const stock = product.available_stock || 0;
    if (stock === 0) return { label: "Out of Stock", color: "error" as const };
    if (stock < 10) return { label: "Limited Stock", color: "warning" as const };
    return { label: "In Stock", color: "success" as const };
  };
  
  const stockStatus = getStockStatus();

  return (
    <Box
      component={RouterLink}
      to={`/products/${product.id}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        textDecoration: "none",
        color: "inherit",
        display: "block",
        borderRadius: 4,
        overflow: "hidden",
        bgcolor: "#fff",
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        transition: "all 0.3s ease",
        position: "relative",
        height: "100%",
        "&:hover": { boxShadow: "0 8px 30px rgba(0,0,0,0.15)" },
      }}
    >
      {/* Badges */}
      <Box sx={{ position: "absolute", top: 12, left: 12, zIndex: 2, display: "flex", gap: 1 }}>
        {hasDiscount && (
          <Chip label={`-${discountPercent}%`} size="small" sx={{ bgcolor: "#EF4444", color: "#fff", fontWeight: 700 }} />
        )}
        {product.is_new_arrival && <Chip label="New" size="small" sx={{ bgcolor: "#10B981", color: "#fff", fontWeight: 700 }} />}
        {product.is_best_seller && <Chip label="Best Seller" size="small" sx={{ bgcolor: "#F59E0B", color: "#fff", fontWeight: 700 }} />}
        {product.is_trending && <Chip label="Trending" size="small" sx={{ bgcolor: "#8B5CF6", color: "#fff", fontWeight: 700 }} />}
      </Box>

      {/* Action Buttons */}
      <Box sx={{ position: "absolute", top: 12, right: 12, zIndex: 2, display: "flex", flexDirection: "column", gap: 1 }}>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: isHovered ? 1 : 0 }}>
          <IconButton
            onClick={(e) => { e.preventDefault(); setIsWishlisted(!isWishlisted); onWishlist(product.id); }}
            sx={{ 
              bgcolor: "rgba(255,255,255,0.9)", 
              "&:hover": { bgcolor: "#fff" },
              transition: "all 0.3s ease"
            }}
          >
            {isWishlisted ? <Favorite color="error" /> : <FavoriteBorder />}
          </IconButton>
        </motion.div>
      </Box>

      {/* Product Image */}
      <Box sx={{ position: "relative", height: 240, overflow: "hidden", bgcolor: "#f8fafc" }}>
        <img
          src={imageUrl}
          alt={product.name}
          style={{ 
            width: "100%", 
            height: "100%", 
            objectFit: "cover",
            transition: "transform 0.5s ease",
            transform: isHovered ? "scale(1.1)" : "scale(1)",
          }}
        />
      </Box>

      {/* Content */}
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ color: "#6B7280", textTransform: "uppercase", letterSpacing: 1 }}>
          {product.brand?.name || "Brand"}
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 700, mt: 0.5, mb: 1, minHeight: 48, lineHeight: 1.3 }}>
          {product.name}
        </Typography>
        
        {/* Rating */}
        <Stack direction="row" spacing={0.5} sx={{ mb: 1 }}>
          {[1, 2, 3, 4, 5].map((star) => (
            <Box key={star} sx={{ color: star <= averageRating ? "#F59E0B" : "#E5E7EB" }}>
              {star <= averageRating ? <Star fontSize="small" /> : <StarBorder fontSize="small" />}
            </Box>
          ))}
          <Typography variant="caption" sx={{ color: "#6B7280", ml: 1 }}>({product.review_count || 128})</Typography>
        </Stack>

        {/* Price */}
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h5" sx={{ fontWeight: 800, color: "#1E3A8A" }}>
            {formatINR(product.offer_price || product.selling_price)}
          </Typography>
          {hasDiscount && (
            <Typography variant="body2" sx={{ color: "#9CA3AF", textDecoration: "line-through" }}>
              {formatINR(product.mrp)}
            </Typography>
          )}
        </Stack>

        {/* Stock Badge */}
        <Chip label={stockStatus.label} size="small" color={stockStatus.color} variant="outlined" sx={{ mb: 1.5 }} />

        {/* Add to Cart Button */}
        <Button
          fullWidth
          variant="contained"
          disabled={product.available_stock === 0}
          onClick={(e) => { e.preventDefault(); onAddToCart(product.id); }}
          startIcon={<ShoppingCart />}
          sx={{ borderRadius: 2, py: 1 }}
        >
          Add to Cart
        </Button>
      </Box>
    </Box>
  );
});

// CategoryCard Component
const CategoryCard = memo(({ category }: { category: Category }) => (
  <Box
    component={RouterLink}
    to={`/categories/${category.slug || category.id}`}
    sx={{
      textDecoration: "none",
      color: "inherit",
      borderRadius: 4,
      overflow: "hidden",
      position: "relative",
      height: 180,
      bgcolor: "#fff",
      boxShadow: "0 4px 15px rgba(0,0,0,0.08)",
      transition: "transform 0.3s ease",
      "&:hover": { transform: "scale(1.05)" },
    }}
  >
    <Box
      sx={{
        position: "absolute",
        inset: 0,
        background: `url(${category.banner_url || "/placeholder-category.jpg"}) center/cover`,
      }}
    >
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.7) 100%)",
        }}
      />
      <Box sx={{ position: "relative", p: 3, height: "100%", display: "flex", flexDirection: "column", justifyContent: "flex-end" }}>
        <Typography variant="h5" sx={{ color: "#fff", fontWeight: 700, mb: 0.5 }}>
          {category.name}
        </Typography>
        <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)" }}>
          {category.product_count || 0} Products
        </Typography>
      </Box>
    </Box>
  </Box>
));

// BrandLogo Component
const BrandLogo = memo(({ brand }: { brand: Brand }) => (
  <Box
    sx={{
      minWidth: 120,
      height: 80,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      p: 2,
      opacity: brand.is_featured ? 1 : 0.6,
      filter: brand.is_featured ? "none" : "grayscale(1)",
      transition: "all 0.3s ease",
      "&:hover": { opacity: 1, filter: "none", transform: "scale(1.05)" },
    }}
  >
    <img
      src={brand.logo_url || "/placeholder-brand.png"}
      alt={brand.name}
      style={{ maxHeight: 50, maxWidth: "100%", objectFit: "contain" }}
    />
  </Box>
));

// TestimonialCard Component
const TestimonialCard = memo(({ review }: { review: Review }) => (
  <Box sx={{ p: 3, bgcolor: "#fff", borderRadius: 4, boxShadow: "0 4px 20px rgba(0,0,0,0.06)", maxWidth: 400 }}>
    <Stack direction="row" spacing={0.5} sx={{ mb: 2 }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <Box key={star} sx={{ color: star <= (review.rating || 5) ? "#F59E0B" : "#E5E7EB" }}>
          {star <= (review.rating || 5) ? <Star /> : <StarBorder />}
        </Box>
      ))}
    </Stack>
    <Typography variant="body1" sx={{ mb: 2, fontStyle: "italic", color: "#374151" }}>
      "{review.comment || review.title}"
    </Typography>
    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#1E3A8A" }}>
      {review.user?.first_name || "Customer"} {review.user?.last_name || ""}
    </Typography>
  </Box>
));

export function HomePage() {
  const dispatch = useAppDispatch();
  const featured = useAppSelector((s) => s.products.featured);
  const bestSellers = useAppSelector((s) => s.products.bestSellers);
  const newArrivals = useAppSelector((s) => s.products.newArrivals);
  const brands = useAppSelector((s) => s.products.brands);
  const categories = useAppSelector((s) => s.categories.items);
  const heroBanners = useAppSelector((s) => s.banners.heroBanners);
  const banners = heroBanners.length > 0 ? heroBanners : useAppSelector((s) => s.banners.items);
  const testimonials = useAppSelector((s) => s.reviews.items);
  const status = useAppSelector((s) => s.products.status);
  const settings = useAppSelector((s) => s.shopSettings.data);

  const [currentBanner, setCurrentBanner] = useState(0);

  useEffect(() => {
    dispatch(fetchShopSettings());
    dispatch(fetchCategoriesWithCounts());
    dispatch(fetchFeaturedProducts(12));
    dispatch(fetchBestSellers(12));
    dispatch(fetchNewArrivals(12));
    dispatch(fetchBrands());
    dispatch(fetchHeroBanners());
    dispatch(fetchReviews({ is_active: true, limit: 5 }));
  }, [dispatch]);

  // Auto-rotate banners
  useEffect(() => {
    if (banners.length <= 1) return;
    const timer = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % banners.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [banners.length]);

  const handleAddToCart = useCallback((productId: number) => {
    // Add to cart logic
  }, []);

  const handleWishlist = useCallback((productId: number) => {
    // Add to wishlist logic
  }, []);

  const currentBannerData = banners[currentBanner];

  return (
    <Box sx={{ bgcolor: "#ffffff", minHeight: "100vh" }}>
      {/* Hero Section */}
      <Box
        sx={{
          position: "relative",
          height: { xs: 500, md: 650 },
          overflow: "hidden",
          bgcolor: "#0F172A",
        }}
      >
        <AnimatePresence mode="wait">
          {currentBannerData && (
            <motion.div
              key={currentBanner}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1 }}
              style={{ position: "absolute", inset: 0 }}
            >
              <Box
                component="img"
                src={currentBannerData.image_url}
                alt={currentBannerData.title || "Banner"}
                sx={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.7 }}
              />
              <Box
                sx={{
                  position: "absolute",
                  inset: 0,
                  background: "linear-gradient(135deg, rgba(30,58,138,0.8) 0%, rgba(15,23,42,0.6) 100%)",
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <Container maxWidth="lg" sx={{ position: "relative", height: "100%", display: "flex", alignItems: "center" }}>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Box sx={{ maxWidth: 500 }}>
              <Typography variant="h1" sx={{ color: "#fff", fontWeight: 800, mb: 2 }}>
                {settings?.shop_name || "Premium Footwear"}
              </Typography>
              <Typography variant="h5" sx={{ color: "rgba(255,255,255,0.9)", mb: 4, fontWeight: 400 }}>
                {settings?.tagline || "Step into style and comfort with our premium collection"}
              </Typography>
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <Button
                  component={RouterLink}
                  to="/products"
                  variant="contained"
                  size="large"
                  sx={{ px: 4, py: 1.5, borderRadius: 3, fontSize: "1.1rem" }}
                >
                  Shop Now
                </Button>
                <Button
                  component={RouterLink}
                  to="/categories"
                  variant="outlined"
                  size="large"
                  sx={{ px: 4, py: 1.5, borderRadius: 3, fontSize: "1.1rem", color: "#fff", borderColor: "rgba(255,255,255,0.5)" }}
                >
                  Explore Collection
                </Button>
              </Stack>
            </Box>
          </motion.div>
        </Container>

        {/* Banner Navigation */}
        {banners.length > 1 && (
          <>
            <IconButton
              onClick={() => setCurrentBanner((p) => (p - 1 + banners.length) % banners.length)}
              sx={{ position: "absolute", left: 20, top: "50%", transform: "translateY(-50%)", bgcolor: "rgba(255,255,255,0.2)", color: "#fff", "&:hover": { bgcolor: "rgba(255,255,255,0.3)" } }}
            >
              <ArrowBack />
            </IconButton>
            <IconButton
              onClick={() => setCurrentBanner((p) => (p + 1) % banners.length)}
              sx={{ position: "absolute", right: 20, top: "50%", transform: "translateY(-50%)", bgcolor: "rgba(255,255,255,0.2)", color: "#fff", "&:hover": { bgcolor: "rgba(255,255,255,0.3)" } }}
            >
              <ArrowForward />
            </IconButton>
          </>
        )}
      </Box>

      {/* Quick Categories */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 4, color: "#1A1A2E" }}>
          Shop by Category
        </Typography>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "repeat(2, 1fr)", sm: "repeat(3, 1fr)", md: "repeat(4, 1fr)" },
            gap: 3,
          }}
        >
          {status === "loading" && categories.length === 0
            ? [1, 2, 3, 4, 5, 6, 7, 8].map((i) => (<Skeleton key={i} variant="rounded" height={180} animation="wave" />))
            : categories.map((cat) => <CategoryCard key={cat.id} category={cat} />)
          }
        </Box>
      </Container>

      {/* Featured Products */}
      <Box sx={{ py: 6, bgcolor: "#F8FAFC" }}>
        <Container maxWidth="lg">
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 4, color: "#1A1A2E" }}>
            Featured Products
          </Typography>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", md: "repeat(4, 1fr)" },
              gap: 3,
            }}
          >
            {status === "loading" && featured.length === 0
              ? [1, 2, 3, 4].map((i) => (<Skeleton key={i} variant="rounded" height={400} animation="wave" />))
              : featured.map((product) => <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} onWishlist={handleWishlist} />)
            }
          </Box>
        </Container>
      </Box>

      {/* Best Sellers */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Box sx={{ display: "flex", alignItems: "center", mb: 4 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, color: "#1A1A2E", flex: 1 }}>
            Best Sellers
          </Typography>
          <Chip label="Trending" color="primary" size="medium" />
        </Box>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", md: "repeat(4, 1fr)" },
            gap: 3,
          }}
        >
          {status === "loading" && bestSellers.length === 0
            ? [1, 2, 3, 4].map((i) => <Skeleton key={i} variant="rounded" height={400} animation="wave" />)
            : bestSellers.map((product) => <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} onWishlist={handleWishlist} />)
          }
        </Box>
      </Container>

      {/* New Arrivals */}
      <Box sx={{ py: 6, bgcolor: "#F8FAFC" }}>
        <Container maxWidth="lg">
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 4, color: "#1A1A2E" }}>
            New Arrivals
          </Typography>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", md: "repeat(4, 1fr)" },
              gap: 3,
            }}
          >
            {status === "loading" && newArrivals.length === 0
              ? [1, 2, 3, 4].map((i) => <Skeleton key={i} variant="rounded" height={400} animation="wave" />)
              : newArrivals.map((product) => <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} onWishlist={handleWishlist} />)
            }
          </Box>
        </Container>
      </Box>

      {/* Brands Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 4, color: "#1A1A2E" }}>
          Featured Brands
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 2 }}>
          {brands.map((brand) => <BrandLogo key={brand.id} brand={brand} />)}
        </Box>
      </Container>

      {/* Testimonials */}
      <Box sx={{ py: 6, bgcolor: "#F8FAFC" }}>
        <Container maxWidth="lg">
          <Typography variant="h3" sx={{ textAlign: "center", fontWeight: 700, mb: 4, color: "#1A1A2E" }}>
            Customer Reviews
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 3 }}>
            {testimonials.map((review) => <TestimonialCard key={review.id} review={review} />)}
          </Box>
        </Container>
      </Box>

      {/* Newsletter */}
      <Box sx={{ py: 8, bgcolor: "#1E3A8A" }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: "center", color: "#fff" }}>
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
              Stay Updated
            </Typography>
            <Typography variant="body1" sx={{ mb: 4, opacity: 0.9 }}>
              Subscribe to our newsletter for exclusive offers and new arrivals
            </Typography>
            <Box
              component="form"
              onSubmit={(e) => e.preventDefault()}
              sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                gap: 2,
                maxWidth: 500,
                mx: "auto",
              }}
            >
              <Box
                component="input"
                type="email"
                placeholder="Enter your email"
                sx={{
                  flex: 1,
                  px: 3,
                  py: 2,
                  borderRadius: 3,
                  border: "none",
                  fontSize: "1rem",
                }}
              />
              <Button variant="contained" size="large" sx={{ px: 4, borderRadius: 3 }}>
                Subscribe
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}