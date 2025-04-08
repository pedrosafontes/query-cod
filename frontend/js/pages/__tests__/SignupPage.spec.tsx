import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import SignupPage from "../SignupPage";
import { MemoryRouter } from "react-router";
import { useAuth } from "contexts/AuthContext";
import { AuthService } from "api";

const mockNavigate = jest.fn();
jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: () => mockNavigate,
}));

jest.mock("api", () => ({
  AuthService: {
    authUsersCreate: jest.fn(),
  },
}));

jest.mock("contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

describe("SignupPage", () => {
  const loginMock = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAuth as jest.Mock).mockReturnValue({ login: loginMock });
    // By default, simulate a successful signup
    (AuthService.authUsersCreate as jest.Mock).mockResolvedValue({});
  });

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <SignupPage />
      </MemoryRouter>
    );

  it("renders the sign-up form", () => {
    renderComponent();

    expect(screen.getByRole("heading", { name: /sign up/i })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirm Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign up/i })).toBeInTheDocument();

    const loginLink = screen.getByRole("link", { name: /log in/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute("href", "/login");
  });

  it("shows validation errors when fields are empty", async () => {
    renderComponent();
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/confirmation is required/i)).toBeInTheDocument();
    expect(AuthService.authUsersCreate).not.toHaveBeenCalled();
  });

  it("shows a validation error when passwords do not match", async () => {
    renderComponent();
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByLabelText("Confirm Password"), {
      target: { value: "differentPassword" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
    expect(AuthService.authUsersCreate).not.toHaveBeenCalled();
  });

  it("calls authUsersCreate, logs in and navigates on successful signup", async () => {
    renderComponent();
    // Set valid form values
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByLabelText("Confirm Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    await waitFor(() => {
      expect(AuthService.authUsersCreate).toHaveBeenCalledWith({
        requestBody: { email: "user@example.com", password: "password123" },
      });
      expect(loginMock).toHaveBeenCalledWith("user@example.com", "password123");
      expect(mockNavigate).toHaveBeenCalledWith("/projects");
    });
  });

  it("shows an error when signup fails", async () => {
    (AuthService.authUsersCreate as jest.Mock).mockRejectedValueOnce(new Error("Signup failed"));
    
    renderComponent();
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByLabelText("Confirm Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    expect(await screen.findByText(/signup failed/i)).toBeInTheDocument();
    expect(loginMock).not.toHaveBeenCalled();
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
