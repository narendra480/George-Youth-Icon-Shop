import { Avatar, Box, Button, Paper, Typography } from "@mui/material";
import { useAppSelector } from "../store/hooks";

export function ProfilePage() {
  const user = useAppSelector((state) => state.auth.user);

  if (!user) {
    return null;
  }

  return (
    <Paper elevation={4} sx={{ p: 4, mt: 4 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Avatar sx={{ width: 80, height: 80 }}>{user.first_name?.[0] || user.email[0]}</Avatar>
        <Box>
          <Typography variant="h5">{`${user.first_name} ${user.last_name}`}</Typography>
          <Typography color="text.secondary">{user.email}</Typography>
        </Box>
      </Box>
      <Typography mb={1}>Phone: {user.phone || "Not provided"}</Typography>
      <Typography mb={1}>Account status: {user.is_active ? "Active" : "Inactive"}</Typography>
      <Typography mb={1}>Email verified: {user.email_verified ? "Yes" : "No"}</Typography>
      <Typography mb={1}>Created: {new Date(user.created_at).toLocaleDateString()}</Typography>
      <Button variant="outlined" sx={{ mt: 3 }}>
        Change password
      </Button>
    </Paper>
  );
}
