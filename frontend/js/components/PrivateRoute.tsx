import { Loader2 } from "lucide-react";
import React, { useEffect, useState } from "react";
import { Navigate, useLocation, Outlet } from "react-router";

import { AuthService } from "../api";

interface PrivateRouteProps {
  redirectPath?: string;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({
  redirectPath = "/login",
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await AuthService.authUsersMeRetrieve();
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to={redirectPath} />;
  }

  return <Outlet />;
};

export default PrivateRoute;
