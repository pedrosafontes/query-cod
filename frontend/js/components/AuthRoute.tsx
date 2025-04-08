import { Navigate, Outlet } from "react-router";

import { useAuth } from "../contexts/AuthContext";

interface AuthRouteProps {
  redirectPath?: string;
}

const AuthRoute = ({ redirectPath = "/projects" }: AuthRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null;

  return isAuthenticated ? <Navigate to={redirectPath} /> : <Outlet />;
};

export default AuthRoute;
