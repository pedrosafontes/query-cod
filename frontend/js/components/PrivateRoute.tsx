import { Navigate, Outlet } from "react-router";

import { useAuth } from "../contexts/AuthContext";

interface PrivateRouteProps {
  redirectPath?: string;
}

const PrivateRoute = ({ redirectPath = "/login" }: PrivateRouteProps) => {
  const { isAuthenticated } = useAuth();

  return isAuthenticated ? <Outlet /> : <Navigate to={redirectPath} />;
};

export default PrivateRoute;
