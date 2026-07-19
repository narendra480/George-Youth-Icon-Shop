import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchCategories } from "../store/categorySlice";
import { Box, Button, Card, CardContent, Typography } from "@mui/material";

export function CategoryAdminPage() {
  const dispatch = useAppDispatch();
  const categories = useAppSelector((state) => state.categories.items);

  useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" mb={3}>
        Category manager
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 3 }}>
        {categories.map((category) => (
          <Card key={category.id}>
            <CardContent>
              <Typography variant="h6">{category.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {category.slug}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
}
