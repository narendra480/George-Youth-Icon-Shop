import { createContext, useContext, useState, useCallback } from "react";
import { Snackbar, Alert, type AlertColor } from "@mui/material";

type Message = { id: number; text: string; severity: AlertColor };

const ToastsContext = createContext<{ addToast: (text: string, severity?: AlertColor) => void }>({ addToast: () => {} });

export function ToastsProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const addToast = useCallback((text: string, severity: AlertColor = "success") => {
    const id = Date.now();
    setMessages((prev) => [...prev, { id, text, severity }]);
    setTimeout(() => setMessages((prev) => prev.filter((m) => m.id !== id)), 3000);
  }, []);
  return (
    <ToastsContext.Provider value={{ addToast }}>
      {children}
      <Snackbar anchorOrigin={{ vertical: "bottom", horizontal: "right" }} open={messages.length > 0} autoHideDuration={3000}>
        <Alert severity={messages[0]?.severity} variant="filled">{messages[0]?.text}</Alert>
      </Snackbar>
    </ToastsContext.Provider>
  );
}

export const useToasts = () => useContext(ToastsContext);