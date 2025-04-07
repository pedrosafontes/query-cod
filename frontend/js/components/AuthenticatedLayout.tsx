import { Outlet } from "react-router";

import AppSidebar from "./AppSidebar";
import { SidebarInset, SidebarProvider } from "./ui/sidebar";

const AuthenticatedLayout = () => {
  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>
        <Outlet />
      </SidebarInset>
    </SidebarProvider>
  );
};

export default AuthenticatedLayout;
