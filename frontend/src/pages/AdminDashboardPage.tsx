import { useEffect, useState } from "react";
import api from "../api/client";
import { Box, Card, CardContent, Typography } from "@mui/material";

interface Metrics {
  total_users: number;
  total_products: number;
  total_categories: number;
  active_categories: number;
}

export function AdminDashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  useEffect(() => {
    api.get<Metrics>("/admin/metrics").then((response) => setMetrics(response.data));
  }, []);

  if (!metrics) {
    return <Typography>Loading dashboard...</Typography>;
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" mb={3}>
        Admin dashboard
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 3 }}>
        {[
          { label: "Total users", value: metrics.total_users },
          { label: "Total products", value: metrics.total_products },
          { label: "Total categories", value: metrics.total_categories },
          { label: "Active categories", value: metrics.active_categories },
        ].map((card) => (
          <Card key={card.label}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                {card.label}
              </Typography>
              <Typography variant="h4">{card.value}</Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
}
