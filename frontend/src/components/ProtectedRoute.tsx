import { Navigate, useLocation } from "react-router-dom";
import { useSelector } from "react-redux";
import type { ReactNode } from "react";
import type { RootState } from "../store";
import { appRoutes } from "../nav/routes";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={appRoutes.login} state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
}