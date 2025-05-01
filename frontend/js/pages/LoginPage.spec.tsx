import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";

import { useAuth } from "contexts/AuthContext";

import LoginPage from "./LoginPage";

const mockNavigate = jest.fn();
jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: () => mockNavigate,
}));

jest.mock("contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

describe("LoginPage", () => {
  const loginMock = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAuth as jest.Mock).mockReturnValue({ login: loginMock });
  });

  const renderComponent = () => {
    return render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );
  };

  test("renders the login form", () => {
    renderComponent();
    expect(
      screen.getByRole("heading", { name: /log in/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument();
  });

  test("shows validation errors when fields are empty or invalid", async () => {
    renderComponent();
    const loginButton = screen.getByRole("button", { name: /log in/i });
    fireEvent.click(loginButton);

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
    expect(
      await screen.findByText(/password is required/i),
    ).toBeInTheDocument();

    expect(loginMock).not.toHaveBeenCalled();
  });

  test("logs in successfully and redirects to /projects", async () => {
    loginMock.mockResolvedValueOnce({}); // Simulate successful login

    renderComponent();

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");
    const loginButton = screen.getByRole("button", { name: /log in/i });

    fireEvent.change(emailInput, { target: { value: "user@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith("user@example.com", "password123");
      expect(mockNavigate).toHaveBeenCalledWith("/projects");
    });
  });

  test("displays an error message when login fails", async () => {
    loginMock.mockRejectedValueOnce(new Error("Invalid credentials"));

    renderComponent();

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");
    const loginButton = screen.getByRole("button", { name: /log in/i });

    fireEvent.change(emailInput, { target: { value: "user@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "wrongpass" } });
    fireEvent.click(loginButton);

    expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test("contains a sign up link that navigates to /signup", () => {
    renderComponent();
    const signUpLink = screen.getByRole("link", { name: /sign up/i });
    expect(signUpLink).toBeInTheDocument();
    expect(signUpLink).toHaveAttribute("href", "/signup");
  });
});
