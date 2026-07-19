import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1E3A8A",
      light: "#3B5CB8",
      dark: "#142966",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#F59E0B",
      light: "#F7B84A",
      dark: "#B37507",
      contrastText: "#1A1A1A",
    },
    background: {
      default: "#FAFAFA",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1A1A2E",
      secondary: "#6B7280",
    },
    divider: "rgba(0,0,0,0.08)",
  },
  typography: {
    fontFamily: ["Inter", "Roboto", "Helvetica", "Arial", "sans-serif"].join(","),
    h1: {
      fontWeight: 800,
      letterSpacing: "-0.02em",
    },
    h2: {
      fontWeight: 700,
      letterSpacing: "-0.01em",
    },
    h3: {
      fontWeight: 700,
    },
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "10px 24px",
        },
        contained: {
          boxShadow: "0 4px 14px rgba(30, 58, 138, 0.25)",
          "&:hover": {
            boxShadow: "0 6px 20px rgba(30, 58, 138, 0.35)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
          "&:hover": {
            boxShadow: "0 8px 30px rgba(0,0,0,0.1)",
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: "0 2px 20px rgba(0,0,0,0.08)",
        },
      },
    },
  },
});