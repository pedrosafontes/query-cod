import { render, screen, waitFor, act } from "@testing-library/react";
import React from "react";

import { AuthService, User } from "api";

import { AuthProvider, useAuth } from "../AuthContext";

function AuthConsumer() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();

  return (
    <div>
      <div data-testid="loading">{isLoading ? "loading" : "not loading"}</div>
      <div data-testid="isAuthenticated">
        {isAuthenticated ? "authenticated" : "not authenticated"}
      </div>
      <div data-testid="user">{user ? user.email : "no user"}</div>
      <button
        type="submit"
        onClick={() => login("user@example.com", "password123")}
      >
        Login
      </button>
      <button type="submit" onClick={() => logout()}>
        Logout
      </button>
    </div>
  );
}

const renderWithAuth = (ui: React.ReactElement) => {
  return render(<AuthProvider>{ui}</AuthProvider>);
};

jest.mock("api", () => ({
  AuthService: {
    authUsersMeRetrieve: jest.fn(),
    authLoginCreate: jest.fn(),
    authLogoutCreate: jest.fn(),
  },
}));

describe("AuthProvider and useAuth", () => {
  const mockUser: User = {
    email: "user@example.com",
    id: 1,
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("should fetch auth status on mount and set user when successful", async () => {
    (AuthService.authUsersMeRetrieve as jest.Mock).mockResolvedValue(mockUser);

    renderWithAuth(<AuthConsumer />);

    expect(screen.getByTestId("loading")).toHaveTextContent("loading");

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("not loading"),
    );
    expect(screen.getByTestId("user")).toHaveTextContent("user@example.com");
    expect(screen.getByTestId("isAuthenticated")).toHaveTextContent(
      "authenticated",
    );
  });

  test("should fetch auth status on mount and set user to null if it fails", async () => {
    (AuthService.authUsersMeRetrieve as jest.Mock).mockRejectedValueOnce(
      new Error("Not authenticated"),
    );

    renderWithAuth(<AuthConsumer />);

    expect(screen.getByTestId("loading")).toHaveTextContent("loading");

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("not loading"),
    );

    expect(screen.getByTestId("user")).toHaveTextContent("no user");
    expect(screen.getByTestId("isAuthenticated")).toHaveTextContent(
      "not authenticated",
    );
  });

  test("should update user on login", async () => {
    (AuthService.authUsersMeRetrieve as jest.Mock).mockRejectedValueOnce(
      new Error("Not authenticated"),
    );

    // Simulate a successful login
    (AuthService.authLoginCreate as jest.Mock).mockResolvedValue({});
    (AuthService.authUsersMeRetrieve as jest.Mock).mockResolvedValueOnce(
      mockUser,
    );

    renderWithAuth(<AuthConsumer />);

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("not loading"),
    );

    expect(screen.getByTestId("user")).toHaveTextContent("no user");

    await act(async () => {
      screen.getByText("Login").click();
    });

    await waitFor(() => {
      expect(screen.getByTestId("user")).toHaveTextContent("user@example.com");
      expect(screen.getByTestId("isAuthenticated")).toHaveTextContent(
        "authenticated",
      );
    });
  });

  test("should clear user on logout", async () => {
    // Start with a logged in user
    (AuthService.authUsersMeRetrieve as jest.Mock).mockResolvedValue(mockUser);
    (AuthService.authLogoutCreate as jest.Mock).mockResolvedValue({});

    renderWithAuth(<AuthConsumer />);

    await waitFor(() =>
      expect(screen.getByTestId("user")).toHaveTextContent("user@example.com"),
    );

    await act(async () => {
      screen.getByText("Logout").click();
    });

    await waitFor(() => {
      expect(screen.getByTestId("user")).toHaveTextContent("no user");
      expect(screen.getByTestId("isAuthenticated")).toHaveTextContent(
        "not authenticated",
      );
    });
  });
});
