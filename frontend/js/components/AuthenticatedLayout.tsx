import { Outlet } from "react-router";

import AppSidebar from "./AppSidebar";

const AuthenticatedLayout = () => {
  return (
    <div className="flex h-screen w-screen bg-background">
      <AppSidebar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
};

export default AuthenticatedLayout;
