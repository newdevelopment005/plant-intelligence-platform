const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/proxy";

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

  private async tryRefreshToken(): Promise<boolean> {
    if (typeof window === "undefined") return false;
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;
    try {
      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "ngrok-skip-browser-warning": "true" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async request<T = any>(
    endpoint: string,
    options: RequestInit = {},
    _retried = false
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
      ...this.getAuthHeaders(),
      ...(options.headers as Record<string, string> || {}),
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401 && !_retried) {
      const refreshed = await this.tryRefreshToken();
      if (refreshed) {
        return this.request<T>(endpoint, options, true);
      }
    }

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

  // =============================================
  // Projects
  // =============================================
  async listProjects(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/projects${qs}`);
  }

  async createProject(data: { name: string; description?: string; tags?: string[] }) {
    return this.request<any>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProject(id: string) {
    return this.request<any>(`/projects/${id}`);
  }

  async deleteProject(id: string) {
    return this.request<any>(`/projects/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Germplasm
  // =============================================
  async listSpecies(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/germplasm/species${qs}`);
  }

  async createSpecies(data: { common_name: string; scientific_name: string; family?: string }) {
    return this.request<any>("/germplasm/species", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listAccessions(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/germplasm/accessions${qs}`);
  }

  async createAccession(data: any) {
    return this.request<any>("/germplasm/accessions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getAccession(id: string) {
    return this.request<any>(`/germplasm/accessions/${id}`);
  }

  // =============================================
  // Phenotyping
  // =============================================
  async listExperiments(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/phenotyping/experiments${qs}`);
  }

  async createExperiment(data: any) {
    return this.request<any>("/phenotyping/experiments", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getExperiment(id: string) {
    return this.request<any>(`/phenotyping/experiments/${id}`);
  }

  async listTraits(experimentId: string) {
    return this.request<{ items: any[]; total: number }>(`/phenotyping/experiments/${experimentId}/traits`);
  }

  async createTrait(experimentId: string, data: any) {
    return this.request<any>(`/phenotyping/experiments/${experimentId}/traits`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listMeasurements(experimentId: string, params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/phenotyping/experiments/${experimentId}/measurements${qs}`);
  }

  async createMeasurement(experimentId: string, data: any) {
    return this.request<any>(`/phenotyping/experiments/${experimentId}/measurements`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // Genomics
  // =============================================
  async listSequences(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/genomics/sequences${qs}`);
  }

  async createSequence(data: any) {
    return this.request<any>("/genomics/sequences", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSequence(id: string) {
    return this.request<any>(`/genomics/sequences/${id}`);
  }

  async listVariants(sequenceId: string, params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/genomics/sequences/${sequenceId}/variants${qs}`);
  }

  async createVariant(sequenceId: string, data: any) {
    return this.request<any>(`/genomics/sequences/${sequenceId}/variants`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // Molecular
  // =============================================
  async listMolecularExperiments(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/molecular/experiments${qs}`);
  }

  async createMolecularExperiment(data: any) {
    return this.request<any>("/molecular/experiments", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listPrimers(experimentId: string) {
    return this.request<{ items: any[]; total: number }>(`/molecular/experiments/${experimentId}/primers`);
  }

  async createPrimer(experimentId: string, data: any) {
    return this.request<any>(`/molecular/experiments/${experimentId}/primers`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listConstructs(experimentId: string) {
    return this.request<{ items: any[]; total: number }>(`/molecular/experiments/${experimentId}/constructs`);
  }

  async createConstruct(experimentId: string, data: any) {
    return this.request<any>(`/molecular/experiments/${experimentId}/constructs`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // Literature
  // =============================================
  async listPapers(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/literature/papers${qs}`);
  }

  async createPaper(data: any) {
    return this.request<any>("/literature/papers", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async searchPapers(query: string) {
    return this.request<{ items: any[]; total: number }>(`/literature/search?q=${encodeURIComponent(query)}`);
  }

  async listCollections() {
    return this.request<{ items: any[]; total: number }>("/literature/collections");
  }

  async createCollection(data: { name: string; description?: string }) {
    return this.request<any>("/literature/collections", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // Knowledge Graph
  // =============================================
  async listKnowledgeEntities(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/knowledge-graph/entities${qs}`);
  }

  async createKnowledgeEntity(data: any) {
    return this.request<any>("/knowledge-graph/entities", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async exploreEntity(id: string) {
    return this.request<any>(`/knowledge-graph/entities/${id}/explore`);
  }

  async listEdges(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/knowledge-graph/edges${qs}`);
  }

  async createEdge(data: any) {
    return this.request<any>("/knowledge-graph/edges", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // AI Assistant
  // =============================================
  async listConversations() {
    return this.request<{ items: any[]; total: number }>("/ai/conversations");
  }

  async createConversation(data: { title: string; project_id?: string }) {
    return this.request<any>("/ai/conversations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async sendMessage(conversationId: string, data: { content: string }) {
    return this.request<any>(`/ai/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listMessages(conversationId: string) {
    return this.request<{ items: any[]; total: number }>(`/ai/conversations/${conversationId}/messages`);
  }

  // =============================================
  // Notebook
  // =============================================
  async listNotebookEntries(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/notebook/entries${qs}`);
  }

  async createNotebookEntry(data: { title: string; content: string; entry_type?: string; tags?: string[] }) {
    return this.request<any>("/notebook/entries", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getNotebookEntry(id: string) {
    return this.request<any>(`/notebook/entries/${id}`);
  }

  async updateNotebookEntry(id: string, data: any) {
    return this.request<any>(`/notebook/entries/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // Knowledge Graph (Update/Delete)
  // =============================================
  async updateKnowledgeEntity(id: string, data: any) {
    return this.request<any>(`/knowledge-graph/entities/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteKnowledgeEntity(id: string) {
    return this.request<any>(`/knowledge-graph/entities/${id}`, { method: "DELETE" });
  }

  async deleteEdge(id: string) {
    return this.request<any>(`/knowledge-graph/edges/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Images (Update/Delete)
  // =============================================
  async updateImage(id: string, data: { name?: string; image_type?: string; description?: string; species?: string; tissue_type?: string; growth_stage?: string; tags?: string[] }) {
    return this.request<any>(`/images/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteImage(id: string) {
    return this.request<any>(`/images/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Germplasm (Update/Delete)
  // =============================================
  async updateSpecies(id: string, data: { common_name?: string; scientific_name?: string; family?: string; genus?: string }) {
    return this.request<any>(`/germplasm/species/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteSpecies(id: string) {
    return this.request<any>(`/germplasm/species/${id}`, { method: "DELETE" });
  }

  async updateAccession(id: string, data: any) {
    return this.request<any>(`/germplasm/accessions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteAccession(id: string) {
    return this.request<any>(`/germplasm/accessions/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Literature (Update/Delete)
  // =============================================
  async updatePaper(id: string, data: any) {
    return this.request<any>(`/literature/papers/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deletePaper(id: string) {
    return this.request<any>(`/literature/papers/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Molecular (Update/Delete)
  // =============================================
  async updateMolecularExperiment(id: string, data: any) {
    return this.request<any>(`/molecular/experiments/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteMolecularExperiment(id: string) {
    return this.request<any>(`/molecular/experiments/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Phenotyping (Update/Delete)
  // =============================================
  async updateExperiment(id: string, data: any) {
    return this.request<any>(`/phenotyping/experiments/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteExperiment(id: string) {
    return this.request<any>(`/phenotyping/experiments/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Genomics (Update/Delete)
  // =============================================
  async updateSequence(id: string, data: any) {
    return this.request<any>(`/genomics/sequences/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteSequence(id: string) {
    return this.request<any>(`/genomics/sequences/${id}`, { method: "DELETE" });
  }

  // =============================================
  // Notebook (Delete)
  // =============================================
  async deleteNotebookEntry(id: string) {
    return this.request<any>(`/notebook/entries/${id}`, { method: "DELETE" });
  }

  // =============================================
  // LIMS (Update/Delete Sample)
  // =============================================
  async updateSample(id: string, data: any) {
    return this.request<any>(`/lims/samples/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteSample(id: string) {
    return this.request<any>(`/lims/samples/${id}`, { method: "DELETE" });
  }

  async deleteEquipment(id: string) {
    return this.request<any>(`/lims/equipment/${id}`, { method: "DELETE" });
  }

  async updatePrimer(experimentId: string, primerId: string, data: any) {
    return this.request<any>(`/molecular/experiments/${experimentId}/primers/${primerId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deletePrimer(experimentId: string, primerId: string) {
    return this.request<any>(`/molecular/experiments/${experimentId}/primers/${primerId}`, { method: "DELETE" });
  }

  async updateConstruct(experimentId: string, constructId: string, data: any) {
    return this.request<any>(`/molecular/experiments/${experimentId}/constructs/${constructId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteConstruct(experimentId: string, constructId: string) {
    return this.request<any>(`/molecular/experiments/${experimentId}/constructs/${constructId}`, { method: "DELETE" });
  }

  // =============================================
  // LIMS
  // =============================================
  async listSamples(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/lims/samples${qs}`);
  }

  async createSample(data: any) {
    return this.request<any>("/lims/samples", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listEquipment() {
    return this.request<{ items: any[]; total: number }>("/lims/equipment");
  }

  async listReagents(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/lims/reagents${qs}`);
  }

  async listLowStockReagents() {
    return this.request<{ items: any[]; total: number }>("/lims/reagents/low-stock");
  }

  // =============================================
  // Image Analysis
  // =============================================
  async listImages(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/images${qs}`);
  }

  async uploadImage(data: FormData) {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${this.baseUrl}/images/upload`, {
      method: "POST",
      headers: { "ngrok-skip-browser-warning": "true", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: data,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: "Upload failed" } }));
      throw new Error(error.error?.message || `HTTP ${response.status}`);
    }
    return response.json();
  }

  async listAnalysisJobs(imageId: string) {
    return this.request<{ items: any[]; total: number }>(`/images/${imageId}/analyze`);
  }

  async createAnalysisJob(imageId: string, data: { analysis_type: string; parameters?: any }) {
    return this.request<any>(`/images/${imageId}/analyze`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // =============================================
  // Reporting
  // =============================================
  async listReports(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/reports${qs}`);
  }

  async createReport(data: any) {
    return this.request<any>("/reports", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateReport(id: string, data: any) {
    return this.request<any>(`/reports/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteReport(id: string) {
    return this.request<void>(`/reports/${id}`, { method: "DELETE" });
  }

  async downloadReport(id: string) {
    return this.request<{ download_url: string; format: string; name: string }>(`/reports/${id}/download`);
  }

  async listReportTemplates() {
    return this.request<{ items: any[]; total: number }>("/reports/templates");
  }

  // =============================================
  // Admin
  // =============================================
  async adminListUsers(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/admin/users${qs}`);
  }

  async adminUpdateUserRole(userId: string, role: string) {
    return this.request<any>(`/admin/users/${userId}/role`, {
      method: "PUT",
      body: JSON.stringify({ role }),
    });
  }

  async adminGetAuditLog(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
    return this.request<{ items: any[]; total: number }>(`/admin/audit-log${qs}`);
  }

  async adminGetHealth() {
    return this.request<any>("/admin/health");
  }

  async adminGetStats() {
    return this.request<any>("/admin/stats");
  }

  // =============================================
  // User Search
  // =============================================
  async searchUsers(query: string) {
    return this.request<{ items: { id: string; email: string; full_name: string; role: string }[] }>(
      `/auth/users/search?q=${encodeURIComponent(query)}`
    );
  }

  // =============================================
  // Sharing
  // =============================================
  async shareItem(data: { item_type: string; item_id: string; visibility: string; user_ids?: string[]; permission?: string }) {
    return this.request<any>("/sharing/share", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSharedWithMe() {
    return this.request<{ items: any[] }>("/sharing/shared-with-me");
  }

  async getMyShares() {
    return this.request<{ items: any[] }>("/sharing/my-shares");
  }

  async revokeShare(shareId: string) {
    return this.request<void>(`/sharing/${shareId}`, { method: "DELETE" });
  }

  // =============================================
  // Teams
  // =============================================
  async createTeam(data: { name: string; description?: string }) {
    return this.request<any>("/teams", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listTeams() {
    return this.request<{ items: any[] }>("/teams");
  }

  async getTeam(teamId: string) {
    return this.request<any>(`/teams/${teamId}`);
  }

  async addTeamMember(teamId: string, data: { user_id: string; role?: string }) {
    return this.request<any>(`/teams/${teamId}/members`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async removeTeamMember(teamId: string, targetUserId: string) {
    return this.request<void>(`/teams/${teamId}/members/${targetUserId}`, {
      method: "DELETE",
    });
  }

  async deleteTeam(teamId: string) {
    return this.request<void>(`/teams/${teamId}`, { method: "DELETE" });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
