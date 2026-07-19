import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { login, clearError } from "../store/authSlice";
import {
  Box,
  Button,
  Checkbox,
  Container,
  FormControlLabel,
  Link,
  Paper,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Snackbar,
} from "@mui/material";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  rememberMe: z.boolean().optional(),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const [error, setError] = useState("");
  const [successSnackbarOpen, setSuccessSnackbarOpen] = useState(false);
  
  const { register, handleSubmit, formState } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { rememberMe: true },
  });
  const { errors } = formState;

  // Auto-redirect after successful login
  useEffect(() => {
    if (auth.isAuthenticated) {
      setSuccessSnackbarOpen(true);
      const timer = setTimeout(() => {
        navigate("/");
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [auth.isAuthenticated, navigate]);

  const onSubmit = async (data: LoginForm) => {
    setError("");
    dispatch(clearError());
    try {
      await dispatch(login({ 
        email: data.email, 
        password: data.password, 
        rememberMe: Boolean(data.rememberMe) 
      })).unwrap();
      // Success message will be shown by the useEffect
    } catch (err: any) {
      setError(err || "Login failed. Check your credentials.");
    }
  };

  const handleCloseSuccessSnackbar = () => {
    setSuccessSnackbarOpen(false);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 8 }}>
      <Paper elevation={4} sx={{ p: 4 }}>
        <Typography variant="h5" mb={2}>
          Sign in
        </Typography>
        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <TextField
            label="Email"
            fullWidth
            margin="normal"
            error={!!errors.email}
            helperText={errors.email?.message as string | undefined}
            disabled={auth.loading}
            {...register("email")}
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            margin="normal"
            error={!!errors.password}
            helperText={errors.password?.message as string | undefined}
            disabled={auth.loading}
            {...register("password")}
          />
          <FormControlLabel
            control={<Checkbox {...register("rememberMe")} defaultChecked disabled={auth.loading} />}
            label="Remember me"
          />
          <Button 
            type="submit" 
            variant="contained" 
            fullWidth 
            sx={{ mt: 2 }} 
            disabled={auth.loading}
          >
            {auth.loading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Signing in...
              </>
            ) : (
              "Login"
            )}
          </Button>
          <Box sx={{ mt: 2, display: "flex", justifyContent: "space-between" }}>
            <Link component={RouterLink} to="/forgot-password" underline="hover">
              Forgot password?
            </Link>
            <Link component={RouterLink} to="/register" underline="hover">
              Register
            </Link>
          </Box>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Box>
      </Paper>

      {/* Success Snackbar */}
      <Snackbar
        open={successSnackbarOpen}
        autoHideDuration={null}
        onClose={handleCloseSuccessSnackbar}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert 
          onClose={handleCloseSuccessSnackbar} 
          severity="success" 
          sx={{ width: "100%", minWidth: 300 }}
        >
          Login successful! Welcome back ✓
        </Alert>
      </Snackbar>
    </Container>
  );
}
