import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { resetPassword, clearError, setMessage } from "../store/authSlice";
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

const passwordSchema = z
  .object({
    password: z.string().min(8),
    confirm_password: z.string().min(8),
  })
  .superRefine((data, ctx) => {
    if (data.password !== data.confirm_password) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Passwords do not match",
        path: ["confirm_password"],
      });
    }
  });

type ResetPasswordForm = z.infer<typeof passwordSchema>;

export function ResetPasswordPage() {
  const dispatch = useAppDispatch();
  const { loading, error, message } = useAppSelector((state) => state.auth);
  const [open, setOpen] = useState(false);
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const { register, handleSubmit } = useForm<ResetPasswordForm>({
    resolver: zodResolver(passwordSchema),
  });

  const onSubmit = async (data: ResetPasswordForm) => {
    await dispatch(resetPassword({ token, password: data.password, confirm_password: data.confirm_password }));
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
            Reset Password
          </Typography>
          <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <TextField
              label="New Password"
              type="password"
              fullWidth
              margin="normal"
              {...register("password")}
            />
            <TextField
              label="Confirm Password"
              type="password"
              fullWidth
              margin="normal"
              {...register("confirm_password")}
            />
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={loading || !token}>
              {loading ? <CircularProgress size={24} /> : "Reset password"}
            </Button>
          </Box>
          {!token && (
            <Typography color="error" sx={{ mt: 2 }}>
              Reset token is missing from the URL.
            </Typography>
          )}
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
      <Snackbar open={open} autoHideDuration={3000} onClose={handleClose} message={message || error || "Action complete"} />
    </Container>
  );
}
