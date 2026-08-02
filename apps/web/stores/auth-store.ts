import { create } from "zustand";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  institution?: string;
  department?: string;
  is_active: boolean;
  is_verified: boolean;
  orcid_id?: string;
  bio?: string;
  avatar_url?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  loadFromStorage: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,

  login: (user, accessToken, refreshToken) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    localStorage.setItem("user", JSON.stringify(user));
    set({ user, accessToken, refreshToken, isAuthenticated: true, isLoading: false });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, isLoading: false });
  },

  updateUser: (updates) => {
    set((state) => {
      if (!state.user) return state;
      const updatedUser = { ...state.user, ...updates };
      localStorage.setItem("user", JSON.stringify(updatedUser));
      return { user: updatedUser };
    });
  },

  loadFromStorage: () => {
    if (typeof window === "undefined") {
      set({ isLoading: false });
      return;
    }

    const accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");
    const userStr = localStorage.getItem("user");

    if (accessToken && refreshToken && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ user, accessToken, refreshToken, isAuthenticated: true, isLoading: false });
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        set({ isLoading: false });
      }
    } else {
      set({ isLoading: false });
    }
  },
}));
