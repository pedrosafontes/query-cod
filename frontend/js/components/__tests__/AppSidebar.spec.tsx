import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import AppSidebar from "../AppSidebar";
import { MemoryRouter, Routes, Route } from "react-router";
import { useAuth } from "contexts/AuthContext";
import { SidebarProvider } from "@/components/ui/sidebar";

const mockNavigate = jest.fn();
const mockLocation = jest.fn();

jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: () => mockNavigate,
  useLocation: () => mockLocation,
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
    jest.spyOn(require("react-router"), "useLocation").mockReturnValue({ pathname: locationPath });

    return render(
      <SidebarProvider>
        <MemoryRouter initialEntries={[locationPath]}>
          <Routes>
            <Route path="*" element={<AppSidebar />} />
          </Routes>
        </MemoryRouter>
      </SidebarProvider>
    );
  };

  it("renders the sidebar with Projects and Logout buttons", () => {
    renderComponent("/projects");
    expect(screen.getByText(/Projects/i)).toBeInTheDocument();
    expect(screen.getByText(/Logout/i)).toBeInTheDocument();
  });

  it("navigates to '/projects' when the Projects button is clicked", async () => {
    renderComponent("/some-other-path");
    const projectsButton = screen.getByRole("button", { name: /projects/i });
    fireEvent.click(projectsButton);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/projects");
    });
  });

  it("calls logout and navigates to '/login' when Logout button is clicked", async () => {
    renderComponent("/projects");
    const logoutButton = screen.getByRole("button", { name: /logout/i });
    fireEvent.click(logoutButton);
    await waitFor(() => {
      expect(logoutMock).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
  });
});
