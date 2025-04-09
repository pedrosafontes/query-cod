import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { AuthService, User } from "../api";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function checkAuthStatus() {
      try {
        const response = await AuthService.authUsersMeRetrieve();
        setUser(response);
      } catch (error) {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    checkAuthStatus();
  }, []);

  const login = async (username: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      await AuthService.authLoginCreate({
        requestBody: { username, password },
      });
      const userResponse = await AuthService.authUsersMeRetrieve();
      setUser(userResponse);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    setIsLoading(true);
    try {
      await AuthService.authLogoutCreate();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
