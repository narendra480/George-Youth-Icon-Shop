import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { createProduct } from "../store/productSlice";
import { fetchCategories } from "../store/categorySlice";
import {
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  SelectChangeEvent,
  TextField,
  Typography,
} from "@mui/material";

const productSchema = z.object({
  name: z.string().min(3),
  slug: z.string().min(3),
  description: z.string().optional(),
  mrp: z.number().positive(),
  category_id: z.number().int().positive(),
});

type ProductForm = z.infer<typeof productSchema>;

export function AdminProductCreatePage() {
  const dispatch = useAppDispatch();
  const categories = useAppSelector((state) => state.categories.items);
  const { register, handleSubmit, setValue, watch } = useForm<ProductForm>({
    resolver: zodResolver(productSchema),
  });

  useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);

  const onCategoryChange = (event: SelectChangeEvent<string>) => {
    setValue("category_id", Number(event.target.value));
  };

  const onSubmit = async (data: ProductForm) => {
    await dispatch(createProduct({
      ...data,
      selling_price: data.mrp, // Use mrp as selling_price initially
    })).unwrap();
  };

return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={4} sx={{ p: 4 }}>
        <Typography variant="h5" mb={2}>
          Add product
        </Typography>
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <TextField label="Name" fullWidth margin="normal" {...register("name")} />
          <TextField label="Slug" fullWidth margin="normal" {...register("slug")} />
          <TextField label="Description" fullWidth margin="normal" {...register("description")} />
          <TextField label="MRP Price" type="number" fullWidth margin="normal" {...register("mrp", { valueAsNumber: true })} />
          <FormControl fullWidth margin="normal">
            <InputLabel id="category-label">Category</InputLabel>
            <Select labelId="category-label" label="Category" defaultValue="" onChange={onCategoryChange}>
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
            Create
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}
