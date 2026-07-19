import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import type { ReactNode } from "react";
import type { RootState } from "../store";

export function PublicRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = Boolean(useSelector((state: RootState) => state.auth.isAuthenticated));
  return isAuthenticated ? <Navigate to="/" replace /> : <>{children}</>;
}
