import { Outlet } from "react-router";

import { SidebarInset, SidebarProvider } from "../ui/sidebar";

import AppSidebar from "./AppSidebar";

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
