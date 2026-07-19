import { useEffect } from "react";
import {
  Box, Container, Typography, Stack, Link as MuiLink, Divider, Grid, IconButton,
} from "@mui/material";
import { Facebook, Instagram, Twitter, LinkedIn, YouTube, Pinterest } from "@mui/icons-material";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchShopSettings } from "../store/shopSettingsSlice";
import { shopConfig } from "../config/shopConfig";

export function Footer() {
  const dispatch = useAppDispatch();
  const settings = useAppSelector((s) => s.shopSettings.data);
  const currentYear = new Date().getFullYear();

  useEffect(() => {
    if (!settings) dispatch(fetchShopSettings());
  }, [dispatch, settings]);

  const s = settings || shopConfig as any;
  const shopName = s.shop_name || shopConfig.shop.name;
  const description = s.description || shopConfig.shop.description;
  const address = s.address || shopConfig.contact.address;
  const phoneNumbers = s.phone_numbers || shopConfig.contact.phone;
  const email = s.email || shopConfig.contact.email;
  const googleMapsEmbed = s.google_maps_embed;
  const facebookUrl = s.facebook_url || shopConfig.social.facebook;
  const instagramUrl = s.instagram_url || shopConfig.social.instagram;
  const twitterUrl = s.twitter_url || shopConfig.social.twitter;
  const linkedinUrl = s.linkedin_url || shopConfig.social.linkedin || "#";
  const youtubeUrl = s.youtube_url || shopConfig.social.youtube || "#";
  const pinterestUrl = s.pinterest_url || "#";
  const copyrightText = s.copyright_text || shopConfig.footer.copyright;
  const footerText = s.footer_text || shopConfig.footer.aboutUs;
  const privacyUrl = s.privacy_policy_url || shopConfig.links.privacy;
  const termsUrl = s.terms_url || shopConfig.links.terms;
  const faqUrl = s.faq_url || shopConfig.links.faq;

  const socialLinks = [
    { href: facebookUrl, icon: <Facebook />, label: "Facebook" },
    { href: instagramUrl, icon: <Instagram />, label: "Instagram" },
    { href: twitterUrl, icon: <Twitter />, label: "Twitter" },
    { href: linkedinUrl, icon: <LinkedIn />, label: "LinkedIn" },
    { href: youtubeUrl, icon: <YouTube />, label: "YouTube" },
    { href: pinterestUrl, icon: <Pinterest />, label: "Pinterest" },
  ];

  return (
    <Box component="footer" sx={{ bgcolor: "#0F172A", color: "#FFFFFF" }}>
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Grid container spacing={4} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 2, color: "#F59E0B" }}>
              {shopName}
            </Typography>
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", mb: 2, lineHeight: 1.7 }}>
              {footerText}
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {socialLinks.map((social) => (
                <IconButton
                  key={social.label}
                  size="small"
                  component="a"
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ 
                    color: "rgba(255,255,255,0.6)", 
                    "&:hover": { color: "#F59E0B", bgcolor: "rgba(245,158,11,0.1)" },
                    transition: "all 0.3s ease" 
                  }}
                  aria-label={social.label}
                >
                  {social.icon}
                </IconButton>
              ))}
            </Stack>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2, color: "#F59E0B" }}>
              Quick Links
            </Typography>
            <Stack spacing={1.5}>
              <MuiLink href="/" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Home
              </MuiLink>
              <MuiLink href="/products" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Products
              </MuiLink>
              <MuiLink href="/categories" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Categories
              </MuiLink>
              <MuiLink href="/cart" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Cart
              </MuiLink>
              <MuiLink href="/wishlist" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Wishlist
              </MuiLink>
              <MuiLink href="/profile" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                My Account
              </MuiLink>
            </Stack>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2, color: "#F59E0B" }}>
              Customer Service
            </Typography>
            <Stack spacing={1.5}>
              <MuiLink href="/contact" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Contact Us
              </MuiLink>
              <MuiLink href={faqUrl} underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                FAQs
              </MuiLink>
              <MuiLink href="#shipping" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Shipping Policy
              </MuiLink>
              <MuiLink href="#returns" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Returns & Exchanges
              </MuiLink>
              <MuiLink href="#track" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Track Order
              </MuiLink>
            </Stack>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2, color: "#F59E0B" }}>
              Policies
            </Typography>
            <Stack spacing={1.5}>
              <MuiLink href={privacyUrl} underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Privacy Policy
              </MuiLink>
              <MuiLink href={termsUrl} underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Terms & Conditions
              </MuiLink>
              <MuiLink href="#refund" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Refund Policy
              </MuiLink>
              <MuiLink href="#terms" underline="hover" sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#F59E0B" }, fontSize: "0.9rem" }}>
                Terms of Service
              </MuiLink>
            </Stack>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2, color: "#F59E0B" }}>
              Contact Info
            </Typography>
            <Stack spacing={1.5}>
              <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", fontSize: "0.9rem" }}>
                {address}
              </Typography>
              {(Array.isArray(phoneNumbers) ? phoneNumbers : [phoneNumbers]).filter(Boolean).map((p: string, i: number) => (
                <Typography key={i} variant="body2" sx={{ color: "rgba(255,255,255,0.7)", fontSize: "0.9rem" }}>
                  📞 {p}
                </Typography>
              ))}
              <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", fontSize: "0.9rem" }}>
                ✉️ {email}
              </Typography>
            </Stack>
          </Grid>

          {googleMapsEmbed && (
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2, color: "#F59E0B" }}>
                Store Location
              </Typography>
              <Box
                sx={{
                  height: 120,
                  borderRadius: 2,
                  overflow: "hidden",
                  bgcolor: "rgba(255,255,255,0.05)",
                }}
                dangerouslySetInnerHTML={{ __html: googleMapsEmbed }}
              />
            </Grid>
          )}
        </Grid>

        <Divider sx={{ my: 3, borderColor: "rgba(255,255,255,0.1)" }} />

        <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ xs: "flex-start", md: "center" }} spacing={2}>
          <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.5)", fontSize: "0.85rem" }}>
            &copy; {currentYear} {copyrightText}
          </Typography>
          <Stack direction="row" spacing={2}>
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.4)" }}>
              Designed & Built with ❤️ for Premium Footwear
            </Typography>
          </Stack>
        </Stack>
      </Container>
    </Box>
  );
}