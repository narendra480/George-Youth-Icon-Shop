import { Button, Box } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { appRoutes } from "../nav/routes";

export function AdminMenu() {
  return (
    <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 3 }}>
      <Button component={RouterLink} to={appRoutes.newProduct} variant="outlined">
        New product
      </Button>
      <Button component={RouterLink} to={appRoutes.adminDashboard} variant="outlined">
        Dashboard
      </Button>
    </Box>
  );
}
