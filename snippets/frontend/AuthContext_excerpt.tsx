/**
 * AuthContext — estado global de autenticación.
 *
 * El token se persiste en localStorage y se re-valida contra /auth/me
 * en cada montaje. `isSuperAdmin` se deriva del campo `role` del usuario,
 * por lo que no requiere un segundo fetch ni lógica adicional.
 */
import {
  createContext,
  useState,
  useEffect,
  type ReactNode,
  type FC,
} from "react";
import type {
  User,
  LoginPayload,
  RegisterPayload,
  UpdateProfilePayload,
  ChangePasswordPayload,
  AuthResponse,
} from "../types/auth";
import { authService } from "../services/authService";

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isSuperAdmin: boolean;
  isLoading: boolean;
  login: (credentials: LoginPayload) => Promise<AuthResponse>;
  register: (data: RegisterPayload) => Promise<AuthResponse>;
  logout: () => void;
  updateProfile: (data: UpdateProfilePayload) => Promise<void>;
  updatePassword: (data: ChangePasswordPayload) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [isLoading, setIsLoading] = useState(true);

  // Derivados: sin estado extra, sin sincronización manual.
  const isAuthenticated = !!token;
  const isSuperAdmin = user?.role === "superadmin";

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  const login = async (credentials: LoginPayload): Promise<AuthResponse> => {
    const response = await authService.login(credentials);
    localStorage.setItem("token", response.access_token);
    setToken(response.access_token);
    setUser(response.user);
    return response;
  };

  const register = async (data: RegisterPayload): Promise<AuthResponse> => {
    const response = await authService.register(data);
    localStorage.setItem("token", response.access_token);
    setToken(response.access_token);
    setUser(response.user);
    return response;
  };

  // Re-valida la sesión al montar (o cuando cambia el token).
  // Si el backend devuelve 401, hace logout automático.
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authService.getMe();
          setUser(userData);
        } catch {
          logout();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, [token]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        isSuperAdmin,
        isLoading,
        login,
        register,
        logout,
        updateProfile: async (data: UpdateProfilePayload) => {
          const updated = await authService.updateProfile(data);
          setUser(updated);
        },
        updatePassword: async (data: ChangePasswordPayload) => {
          await authService.changePassword(data);
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
