import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { forgotPassword, clearError, setMessage } from "../store/authSlice";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Snackbar,
  TextField,
  Typography,
} from "@mui/material";

const forgotPasswordSchema = z.object({
  email: z.string().email(),
});

type ForgotPasswordForm = z.infer<typeof forgotPasswordSchema>;

export function ForgotPasswordPage() {
  const dispatch = useAppDispatch();
  const { loading, error, message } = useAppSelector((state) => state.auth);
  const [open, setOpen] = useState(false);
  const { register, handleSubmit } = useForm<ForgotPasswordForm>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordForm) => {
    await dispatch(forgotPassword(data));
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    dispatch(clearError());
    dispatch(setMessage(null));
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Forgot Password
          </Typography>
          <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <TextField
              label="Email"
              fullWidth
              margin="normal"
              {...register("email")}
            />
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "Send reset link"}
            </Button>
          </Box>
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
          {message && (
            <Typography color="success.main" sx={{ mt: 2 }}>
              {message}
            </Typography>
          )}
        </CardContent>
      </Card>
      <Snackbar open={open} autoHideDuration={3000} onClose={handleClose} message={message || error || "Request submitted"} />
    </Container>
  );
}
