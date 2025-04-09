import { Navigate, Outlet } from "react-router";

import { useAuth } from "../contexts/AuthContext";

interface PrivateRouteProps {
  redirectPath?: string;
}

const PrivateRoute = ({ redirectPath = "/login" }: PrivateRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null;

  return isAuthenticated ? <Outlet /> : <Navigate to={redirectPath} />;
};

export default PrivateRoute;
