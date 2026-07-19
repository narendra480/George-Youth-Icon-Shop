import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { register } from "../store/authSlice";
import {
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  Container,
  FormControlLabel,
  Link,
  TextField,
  Typography,
  Alert,
  Snackbar,
} from "@mui/material";

const passwordRegex = /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])/;

const registerSchema = z
  .object({
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
    email: z.string().email("Invalid email"),
    phone: z
      .string()
      .optional()
      .refine((val) => !val || /^[0-9]{10,15}$/.test(val), {
        message: "Phone must be 10-15 digits",
      }),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .refine((val) => passwordRegex.test(val), {
        message: "Password must include upper, lower, number and special character",
      }),
    confirm_password: z.string().min(8),
    acceptTerms: z.boolean().refine((value) => value === true, {
      message: "You must accept the terms and conditions",
    }),
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

type RegisterForm = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const [error, setError] = useState("");
  const [successSnackbarOpen, setSuccessSnackbarOpen] = useState(false);
  const [redirectCountdown, setRedirectCountdown] = useState<number | null>(null);
  
  const { register: formRegister, handleSubmit, formState } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: { acceptTerms: false },
  });
  const { errors } = formState;

  // Handle auto-redirect after successful registration
  useEffect(() => {
    if (redirectCountdown === null) return;
    
    if (redirectCountdown === 0) {
      navigate("/login");
      return;
    }

    const timer = setTimeout(() => {
      setRedirectCountdown(redirectCountdown - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [redirectCountdown, navigate]);

  const onSubmit = async (data: RegisterForm) => {
    setError("");
    try {
      await dispatch(
        register({
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email,
          phone: data.phone,
          password: data.password,
          confirm_password: data.confirm_password,
          acceptTerms: data.acceptTerms,
        }),
      ).unwrap();
      
      setSuccessSnackbarOpen(true);
      setRedirectCountdown(2); // 2 seconds before redirect
    } catch (err: any) {
      setError(err || "Unable to register. Please verify your input.");
    }
  };

  const handleCloseSuccessSnackbar = () => {
    setSuccessSnackbarOpen(false);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 8 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" mb={2}>
            Create account
          </Typography>
          <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <TextField
              label="First Name"
              fullWidth
              margin="normal"
              error={!!errors.first_name}
              helperText={errors.first_name?.message as string | undefined}
              disabled={auth.loading}
              {...formRegister("first_name")}
            />
            <TextField
              label="Last Name"
              fullWidth
              margin="normal"
              error={!!errors.last_name}
              helperText={errors.last_name?.message as string | undefined}
              disabled={auth.loading}
              {...formRegister("last_name")}
            />
            <TextField
              label="Email"
              fullWidth
              margin="normal"
              error={!!errors.email}
              helperText={errors.email?.message as string | undefined}
              disabled={auth.loading}
              {...formRegister("email")}
            />
            <TextField
              label="Phone"
              fullWidth
              margin="normal"
              error={!!errors.phone}
              helperText={errors.phone?.message as string | undefined}
              disabled={auth.loading}
              {...formRegister("phone")}
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              error={!!errors.password}
              helperText={errors.password?.message as string | undefined}
              disabled={auth.loading}
              {...formRegister("password")}
            />
            <TextField
              label="Confirm Password"
              type="password"
              fullWidth
              margin="normal"
              error={!!errors.confirm_password}
              helperText={errors.confirm_password?.message as string | undefined}
              disabled={auth.loading}
              {...formRegister("confirm_password")}
            />
            <FormControlLabel
              control={<Checkbox {...formRegister("acceptTerms")} disabled={auth.loading} />}
              label="I accept the terms and conditions"
            />
            <Button 
              type="submit" 
              variant="contained" 
              fullWidth 
              sx={{ mt: 2 }} 
              disabled={auth.loading}
            >
              {auth.loading ? <CircularProgress size={20} /> : "Register"}
            </Button>
          </Box>
          <Box sx={{ mt: 2 }}>
            <Link component={RouterLink} to="/login" underline="hover">
              Already have an account? Login
            </Link>
          </Box>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

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
          <Typography variant="body2" sx={{ mb: 1 }}>
            Account created successfully! ✓
          </Typography>
          <Typography variant="caption">
            Redirecting to login in {redirectCountdown}s...
          </Typography>
        </Alert>
      </Snackbar>
    </Container>
  );
}
