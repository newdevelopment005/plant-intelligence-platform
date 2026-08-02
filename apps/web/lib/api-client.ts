const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface UserInfo {
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

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeaders(): Record<string, string> {
    if (typeof window === "undefined") return {};
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...this.getAuthHeaders(),
      ...(options.headers as Record<string, string> || {}),
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: { code: "UNKNOWN", message: "Request failed" },
      }));
      throw new Error(error.error?.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async register(data: {
    email: string;
    password: string;
    full_name: string;
    institution?: string;
    department?: string;
  }): Promise<{ message: string; user: UserInfo }> {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(email: string, password: string): Promise<TokenPair & { user: UserInfo }> {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async refreshToken(refreshToken: string): Promise<TokenPair> {
    return this.request("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async logout(refreshToken?: string): Promise<{ message: string }> {
    return this.request("/auth/logout", {
      method: "POST",
      body: refreshToken ? JSON.stringify({ refresh_token: refreshToken }) : undefined,
    });
  }

  async getProfile(): Promise<UserInfo> {
    return this.request("/auth/me");
  }

  async updateProfile(data: {
    full_name?: string;
    institution?: string;
    department?: string;
    bio?: string;
    orcid_id?: string;
  }): Promise<UserInfo> {
    return this.request("/auth/me", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async forgotPassword(email: string): Promise<{ message: string }> {
    return this.request("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    return this.request("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  }

  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> {
    return this.request("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
