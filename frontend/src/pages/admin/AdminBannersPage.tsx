import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { useToasts } from "../../components/Toasts";
import {
  Box, Typography, Stack, Button, IconButton, Card, CardContent, Dialog, DialogTitle, DialogContent, DialogActions, TextField, FormControl, InputLabel, Select, MenuItem, Skeleton,
} from "@mui/material";
import { Edit as EditIcon, Delete as DeleteIcon } from "@mui/icons-material";

export function AdminBannersPage() {
  const dispatch = useAppDispatch();
  const { addToast } = useToasts();
  const [banners, setBanners] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState({ title: "", subtitle: "", image_url: "", link_url: "", position: "home", sort_order: 0, is_active: true });

  useEffect(() => {
    fetchBanners();
  }, []);

  const fetchBanners = async () => {
    const res = await fetch("http://localhost:8000/api/v1/banners");
    const data = await res.json();
    setBanners(data);
  };

  const handleSubmit = async () => {
    if (editing) {
      await fetch(`http://localhost:8000/api/v1/banners/${editing.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        body: JSON.stringify(form),
      });
      addToast("Banner updated");
    } else {
      await fetch("http://localhost:8000/api/v1/banners", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        body: JSON.stringify(form),
      });
      addToast("Banner created");
    }
    setOpen(false);
    setEditing(null);
    fetchBanners();
  };

  const handleDelete = async (id: number) => {
    await fetch(`http://localhost:8000/api/v1/banners/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });
    addToast("Banner deleted");
    fetchBanners();
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Banners</Typography>
        <Button variant="contained" onClick={() => { setEditing(null); setForm({ title: "", subtitle: "", image_url: "", link_url: "", position: "home", sort_order: 0, is_active: true }); setOpen(true); }}>Create Banner</Button>
      </Stack>
      <Stack spacing={2}>
        {banners.map((b) => (
          <Card key={b.id} sx={{ border: "1px solid rgba(0,0,0,0.06)" }}>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center">
                <Box sx={{ width: 120, height: 60, borderRadius: 2, overflow: "hidden", bgcolor: "#F1F5F9", flexShrink: 0 }}>
                  {b.image_url && <Box component="img" src={b.image_url} alt="" sx={{ width: "100%", height: "100%", objectFit: "cover" }} />}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{b.title || "Untitled"}</Typography>
                  <Typography variant="body2" color="text.secondary">{b.subtitle} • {b.position}</Typography>
                </Box>
                <Stack direction="row" spacing={1}>
                  <IconButton size="small" onClick={() => { setEditing(b); setOpen(true); }}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => handleDelete(b.id)}><DeleteIcon /></IconButton>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        ))}
      </Stack>
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>{editing ? "Edit" : "Create"} Banner</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1, minWidth: 320 }}>
            <TextField label="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <TextField label="Subtitle" value={form.subtitle} onChange={(e) => setForm({ ...form, subtitle: e.target.value })} />
            <TextField label="Image URL" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} />
            <TextField label="Link URL" value={form.link_url} onChange={(e) => setForm({ ...form, link_url: e.target.value })} />
            <FormControl fullWidth size="small">
              <InputLabel>Position</InputLabel>
              <Select value={form.position} label="Position" onChange={(e) => setForm({ ...form, position: e.target.value })}>
                <MenuItem value="home">Home</MenuItem>
                <MenuItem value="category">Category</MenuItem>
                <MenuItem value="product">Product</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}