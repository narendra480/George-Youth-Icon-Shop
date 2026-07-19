import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { verifyEmail, clearError, setMessage } from "../store/authSlice";
import { Button, Card, CardContent, Container, CircularProgress, Snackbar, Typography } from "@mui/material";

export function VerifyEmailPage() {
  const dispatch = useAppDispatch();
  const { loading, error, message } = useAppSelector((state) => state.auth);
  const [searchParams] = useSearchParams();
  const [submitted, setSubmitted] = useState(false);
  const [open, setOpen] = useState(false);
  const token = searchParams.get("token") || "";

  useEffect(() => {
    if (token && !submitted) {
      dispatch(verifyEmail({ token }));
      setSubmitted(true);
      setOpen(true);
    }
  }, [dispatch, submitted, token]);

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
            Verify Email
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : token ? (
            <Typography>{message || "Verifying your email..."}</Typography>
          ) : (
            <Typography color="error">Verification token is missing.</Typography>
          )}
        </CardContent>
      </Card>
      <Snackbar open={open} autoHideDuration={3000} onClose={handleClose} message={message || error || "Verification in progress"} />
    </Container>
  );
}
