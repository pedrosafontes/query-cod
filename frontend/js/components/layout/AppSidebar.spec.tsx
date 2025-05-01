import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router";

import { SidebarProvider } from "@/components/ui/sidebar";
import { useAuth } from "contexts/AuthContext";

import AppSidebar from "./AppSidebar";

const mockNavigate = jest.fn();

jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: () => mockNavigate,
  useLocation: jest.fn(),
}));

jest.mock("contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

describe("AppSidebar", () => {
  const logoutMock = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    jest.clearAllMocks();
    (useAuth as jest.Mock).mockReturnValue({ logout: logoutMock });
  });

  const renderComponent = (locationPath = "/projects") => {
    (useLocation as jest.Mock).mockReturnValueOnce({ pathname: "/projects" });

    return render(
      <SidebarProvider>
        <MemoryRouter initialEntries={[locationPath]}>
          <Routes>
            <Route element={<AppSidebar />} path="*" />
          </Routes>
        </MemoryRouter>
      </SidebarProvider>,
    );
  };

  test("renders the sidebar with Projects and Logout buttons", () => {
    renderComponent("/projects");
    expect(screen.getByText(/Projects/i)).toBeInTheDocument();
    expect(screen.getByText(/Logout/i)).toBeInTheDocument();
  });

  test("navigates to '/projects' when the Projects button is clicked", async () => {
    renderComponent("/some-other-path");
    const projectsButton = screen.getByRole("button", { name: /projects/i });
    fireEvent.click(projectsButton);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/projects");
    });
  });

  test("calls logout and navigates to '/login' when Logout button is clicked", async () => {
    renderComponent("/projects");
    const logoutButton = screen.getByRole("button", { name: /logout/i });
    fireEvent.click(logoutButton);
    await waitFor(() => {
      expect(logoutMock).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
  });
});
