"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  institution?: string | null;
  department?: string | null;
  is_active: boolean;
  created_at: string;
}

interface AuditEntry {
  id: number;
  user_id: string;
  action: string;
  resource_type: string | null;
  ip_address: string | null;
  created_at: string;
}

interface SystemHealth {
  status: string;
  database: string;
  uptime: string;
}

interface Department {
  id: string;
  name: string;
  code: string | null;
  description: string | null;
  head_user_id: string | null;
  head_user?: { full_name?: string; email?: string } | null;
  is_active: boolean;
  member_count: number;
  created_at: string;
  updated_at: string;
}

interface DepartmentMember {
  id: string;
  user_id: string;
  role: string;
  joined_at: string;
  user?: { full_name?: string; email?: string } | null;
}

export default function AdminPage() {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"users" | "audit" | "system" | "departments" | "teams">("users");
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [stats, setStats] = useState<any>(null);

  const [departments, setDepartments] = useState<Department[]>([]);
  const [deptTotal, setDeptTotal] = useState(0);
  const [depLoading, setDepLoading] = useState(false);
  const [showDeptForm, setShowDeptForm] = useState(false);
  const [deptForm, setDeptForm] = useState({ name: "", code: "", description: "", head_user_id: "" });
  const [selectedDept, setSelectedDept] = useState<string | null>(null);
  const [deptMembers, setDeptMembers] = useState<DepartmentMember[]>([]);
  const [deptMemberUsers, setDeptMemberUsers] = useState<Record<string, string>>({});
  const [deptSearch, setDeptSearch] = useState("");

  const [adminTeams, setAdminTeams] = useState<any[]>([]);
  const [adminTeamsTotal, setAdminTeamsTotal] = useState(0);
  const [adminTeamsLoading, setAdminTeamsLoading] = useState(false);

  useEffect(() => {
    let currentUser: { role?: string } | null = null;
    if (typeof window !== "undefined") {
      try {
        const raw = localStorage.getItem("user");
        if (raw) currentUser = JSON.parse(raw);
      } catch { currentUser = null; }
    }
    setIsAdmin(currentUser?.role === "admin");
    if (currentUser?.role === "admin") {
      loadData();
    }
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [userData, auditData] = await Promise.all([
        apiClient.adminListUsers(),
        apiClient.adminGetAuditLog(),
      ]);
      setUsers(userData?.items ?? []);
      setTotal(userData?.total ?? 0);
      setAuditLog(auditData?.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const loadSystemHealth = async () => {
    try {
      const health = await apiClient.adminGetHealth();
      setSystemHealth(health);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load health");
    }
  };

  const loadStats = async () => {
    try {
      const s = await apiClient.adminGetStats();
      setStats(s);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load stats");
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await apiClient.adminUpdateUserRole(userId, newRole);
      setUsers(users.map((u) => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleStatusChange = async (userId: string, isActive: boolean) => {
    try {
      await apiClient.adminUpdateUserStatus(userId, isActive);
      setUsers(users.map((u) => u.id === userId ? { ...u, is_active: isActive } : u));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleTabChange = (newTab: "users" | "audit" | "system" | "departments" | "teams") => {
    setTab(newTab);
    if (newTab === "system") {
      loadSystemHealth();
      loadStats();
    }
    if (newTab === "departments") {
      loadDepartments();
    }
    if (newTab === "teams") {
      loadAdminTeams();
    }
  };

  const loadAdminTeams = async () => {
    setAdminTeamsLoading(true);
    try {
      const data = await apiClient.adminListTeams({ limit: "500" });
      setAdminTeams(data?.items ?? []);
      setAdminTeamsTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load teams");
      setTimeout(() => setError(""), 4000);
    } finally {
      setAdminTeamsLoading(false);
    }
  };

  const handleAdminDeleteTeam = async (teamId: string, teamName: string) => {
    if (!confirm(`Delete team "${teamName}"? This cannot be undone.`)) return;
    try {
      await apiClient.adminDeleteTeam(teamId);
      setError("");
      loadAdminTeams();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete team");
      setTimeout(() => setError(""), 4000);
    }
  };

  const loadDepartments = async () => {
    setDepLoading(true);
    try {
      const data = await apiClient.listDepartments({ limit: 500 });
      setDepartments(data?.items ?? []);
      setDeptTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load departments");
      setTimeout(() => setError(""), 4000);
    } finally { setDepLoading(false); }
  };

  const loadDeptMembers = async (deptId: string) => {
    try {
      const data = await apiClient.getDepartment(deptId);
      setSelectedDept(deptId);
      setDeptMembers(data?.members ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load department");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleDeptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createDepartment({
        name: deptForm.name,
        code: deptForm.code || undefined,
        description: deptForm.description || undefined,
        head_user_id: deptForm.head_user_id || undefined,
      });
      setShowDeptForm(false);
      setDeptForm({ name: "", code: "", description: "", head_user_id: "" });
      await loadDepartments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create department");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleDeptDelete = async (deptId: string) => {
    if (!window.confirm("Delete this department? This removes all memberships.")) return;
    try {
      await apiClient.deleteDepartment(deptId);
      if (selectedDept === deptId) { setSelectedDept(null); setDeptMembers([]); }
      await loadDepartments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete department");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleAddDeptMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDept) return;
    const userId = (e.target as any).userId.value?.trim();
    const role = (e.target as any).role.value ?? "member";
    if (!userId) { setError("Select a user to add"); setTimeout(() => setError(""), 4000); return; }
    try {
      await apiClient.addDepartmentMember(selectedDept, { user_id: userId, role });
      await loadDeptMembers(selectedDept);
      await loadDepartments();
      (e.target as HTMLFormElement).reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add member");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleDeptMemberRole = async (deptId: string, memberUserId: string, role: string) => {
    try {
      await apiClient.updateDepartmentMemberRole(deptId, memberUserId, role);
      await loadDeptMembers(deptId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleDeptMemberRemove = async (deptId: string, memberUserId: string) => {
    if (!window.confirm("Remove this member from the department?")) return;
    try {
      await apiClient.removeDepartmentMember(deptId, memberUserId);
      await loadDeptMembers(deptId);
      await loadDepartments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove member");
      setTimeout(() => setError(""), 4000);
    }
  };

  const handleDeptToggleActive = async (dept: Department) => {
    try {
      await apiClient.updateDepartment(dept.id, { is_active: !dept.is_active });
      await loadDepartments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update department");
      setTimeout(() => setError(""), 4000);
    }
  };

  const resolveMemberName = (userId: string, user?: DepartmentMember["user"]) =>
    user?.full_name ||
    deptMemberUsers[userId] ||
    users.find((u) => u.id === userId)?.full_name ||
    users.find((u) => u.id === userId)?.email ||
    userId.slice(0, 8);

  if (isAdmin === false) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Admin</h1>
        <div className="rounded-lg border bg-card p-8 text-center">
          <p className="text-lg font-semibold text-red-600">Access Denied</p>
          <p className="text-sm text-muted-foreground mt-2">
            Only platform administrators can view this page.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin</h1>
        <p className="text-muted-foreground">{total} users</p>
      </div>

      <div className="flex gap-4 border-b">
        <button onClick={() => handleTabChange("users")} className={`pb-2 px-4 text-sm font-medium ${tab === "users" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Users</button>
        <button onClick={() => handleTabChange("audit")} className={`pb-2 px-4 text-sm font-medium ${tab === "audit" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Audit Log</button>
        <button onClick={() => handleTabChange("system")} className={`pb-2 px-4 text-sm font-medium ${tab === "system" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>System</button>
        <button onClick={() => handleTabChange("departments")} className={`pb-2 px-4 text-sm font-medium ${tab === "departments" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Departments</button>
        <button onClick={() => handleTabChange("teams")} className={`pb-2 px-4 text-sm font-medium ${tab === "teams" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Teams</button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {loading ? (
        <div className="flex justify-center py-12"><div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" /></div>
      ) : tab === "users" ? (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Email</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Role</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Institution</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Created</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-t hover:bg-muted/20">
                  <td className="px-4 py-3 text-sm font-medium">{user.full_name}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{user.email}</td>
                  <td className="px-4 py-3">
                    <select value={user.role} onChange={(e) => handleRoleChange(user.id, e.target.value)} className="rounded border px-2 py-1 text-sm">
                      <option value="researcher">Researcher</option>
                      <option value="technician">Technician</option>
                      <option value="principal_investigator">PI</option>
                      <option value="admin">Admin</option>
                      <option value="readonly">Read Only</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    <div>{user.institution || "-"}</div>
                    {user.department && <div className="text-xs">{user.department}</div>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${user.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleStatusChange(user.id, !user.is_active)}
                        className={user.is_active ? "text-red-600 hover:underline" : "text-green-600 hover:underline"}
                      >
                        {user.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : tab === "audit" ? (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Action</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Resource</th>
                <th className="px-4 py-3 text-left text-sm font-medium">IP</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {auditLog.map((entry) => (
                <tr key={entry.id} className="border-t hover:bg-muted/20">
                  <td className="px-4 py-3 text-sm font-medium">{entry.action}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{entry.resource_type || "-"}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground font-mono">{entry.ip_address || "-"}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{new Date(entry.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {auditLog.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">No audit log entries</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : tab === "system" ? (
        <div className="space-y-6">
          <div className="rounded-lg border bg-card p-6">
            <h2 className="text-lg font-semibold mb-4">System Health</h2>
            {systemHealth ? (
              <div className="grid grid-cols-3 gap-4">
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Status</div>
                  <div className="text-lg font-semibold">{systemHealth.status || "Unknown"}</div>
                </div>
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Database</div>
                  <div className="text-lg font-semibold">{systemHealth.database || "Unknown"}</div>
                </div>
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Uptime</div>
                  <div className="text-lg font-semibold">{systemHealth.uptime || "Unknown"}</div>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground">Loading system health...</div>
            )}
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h2 className="text-lg font-semibold mb-4">Usage Statistics</h2>
            {stats ? (
              <div className="grid grid-cols-4 gap-4">
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Total Users</div>
                  <div className="text-lg font-semibold">{stats.total_users ?? total}</div>
                </div>
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Total Projects</div>
                  <div className="text-lg font-semibold">{stats.total_projects ?? "-"}</div>
                </div>
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Total Samples</div>
                  <div className="text-lg font-semibold">{stats.total_samples ?? "-"}</div>
                </div>
                <div className="rounded-md bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground">Active Experiments</div>
                  <div className="text-lg font-semibold">{stats.active_experiments ?? "-"}</div>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground">Loading statistics...</div>
            )}
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
            <div className="flex gap-3">
              <button onClick={() => { loadSystemHealth(); loadStats(); }} className="rounded-md border px-4 py-2 hover:bg-gray-50">Refresh</button>
              <button onClick={loadData} className="rounded-md border px-4 py-2 hover:bg-gray-50">Reload Users</button>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">Departments</h2>
              <p className="text-sm text-muted-foreground">{deptTotal} department{deptTotal === 1 ? "" : "s"}</p>
            </div>
            <div className="flex gap-3">
              <input
                value={deptSearch}
                onChange={(e) => setDeptSearch(e.target.value)}
                placeholder="Search departments..."
                className="rounded-md border px-3 py-2 text-sm"
              />
              <button onClick={() => setShowDeptForm(!showDeptForm)} className="rounded-md bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700">
                {showDeptForm ? "Cancel" : "+ New Department"}
              </button>
            </div>
          </div>

          {showDeptForm && (
            <form onSubmit={handleDeptSubmit} className="rounded-lg border bg-card p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name *</label>
                  <input required value={deptForm.name} onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })} className="w-full rounded-md border px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Code</label>
                  <input value={deptForm.code} onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value })} placeholder="e.g. MOLBIO" className="w-full rounded-md border px-3 py-2" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea value={deptForm.description} onChange={(e) => setDeptForm({ ...deptForm, description: e.target.value })} rows={2} className="w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                  <label className="block text-sm font-medium mb-1">Department Head</label>
                  <select
                    value={deptForm.head_user_id}
                    onChange={(e) => setDeptForm({ ...deptForm, head_user_id: e.target.value })}
                    className="w-full rounded-md border px-3 py-2"
                  >
                    <option value="">No head</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.full_name} ({u.email})
                      </option>
                    ))}
                  </select>
                </div>
              <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700">Create Department</button>
            </form>
          )}

          <div className="grid grid-cols-3 gap-6">
            <div className="col-span-1 rounded-lg border overflow-hidden">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium">Department</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Members</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {depLoading ? (
                    <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
                  ) : departments.filter((d) => d.name.toLowerCase().includes(deptSearch.toLowerCase())).map((dep) => (
                    <tr key={dep.id} className="border-t hover:bg-muted/20">
                      <td className="px-4 py-3">
                        <button onClick={() => loadDeptMembers(dep.id)} className="text-left">
                          <div className="text-sm font-medium hover:underline">{dep.name}</div>
                          <div className="text-xs text-muted-foreground">{dep.code || "-"}</div>
                        </button>
                      </td>
                      <td className="px-4 py-3 text-sm">{dep.member_count}</td>
                      <td className="px-4 py-3">
                        <span className={`rounded-full px-2 py-1 text-xs font-medium ${dep.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                          {dep.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2 text-sm">
                          <button onClick={() => handleDeptToggleActive(dep)} className="text-blue-600 hover:underline">{dep.is_active ? "Deactivate" : "Activate"}</button>
                          <button onClick={() => handleDeptDelete(dep.id)} className="text-red-600 hover:underline">Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {departments.length === 0 && !depLoading && (
                    <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">No departments. Create one to get started.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="col-span-2 rounded-lg border bg-card p-6">
              {selectedDept ? (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold">{departments.find((d) => d.id === selectedDept)?.name} {departments.find((d) => d.id === selectedDept)?.code && <span className="text-sm text-muted-foreground">({departments.find((d) => d.id === selectedDept)?.code})</span>}</h3>
                      <p className="text-sm text-muted-foreground">{deptMembers.length} members</p>
                      {departments.find((d) => d.id === selectedDept)?.head_user?.full_name && (
                        <p className="text-sm text-muted-foreground">
                          Head: <span className="text-foreground">{departments.find((d) => d.id === selectedDept)?.head_user?.full_name}</span>
                        </p>
                      )}
                    </div>
                    <button onClick={() => { setSelectedDept(null); setDeptMembers([]); }} className="text-sm text-muted-foreground hover:text-gray-900">Back to list</button>
                  </div>

                  <form onSubmit={handleAddDeptMember} className="mb-4 flex flex-wrap gap-2">
                    <select name="userId" required className="flex-1 rounded-md border px-3 py-2 text-sm" defaultValue="">
                      <option value="" disabled>Select a user...</option>
                      {users.map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.full_name} ({u.email})
                        </option>
                      ))}
                    </select>
                    <select name="role" className="rounded-md border px-3 py-2 text-sm">
                      <option value="member">Member</option>
                      <option value="head">Head</option>
                    </select>
                    <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700">Add Member</button>
                  </form>

                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-medium">User</th>
                        <th className="px-4 py-3 text-left text-sm font-medium">Role</th>
                        <th className="px-4 py-3 text-left text-sm font-medium">Joined</th>
                        <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {deptMembers.map((m) => (
                        <tr key={m.id} className="border-t hover:bg-muted/20">
                          <td className="px-4 py-3 text-sm font-medium">
                            {resolveMemberName(m.user_id, m.user)}
                            {m.user?.email && (
                              <div className="text-xs font-normal text-muted-foreground">{m.user.email}</div>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <select
                              value={m.role}
                              onChange={(e) => handleDeptMemberRole(selectedDept, m.user_id, e.target.value)}
                              className="rounded border px-2 py-1 text-sm"
                            >
                              <option value="member">Member</option>
                              <option value="head">Head</option>
                            </select>
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">{new Date(m.joined_at).toLocaleDateString()}</td>
                          <td className="px-4 py-3 text-sm">
                            <button onClick={() => handleDeptMemberRemove(selectedDept, m.user_id)} className="text-red-600 hover:underline">Remove</button>
                          </td>
                        </tr>
                      ))}
                      {deptMembers.length === 0 && (
                        <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">No members yet</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex h-full min-h-[300px] items-center justify-center text-muted-foreground">
                  Select a department to manage its members
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      {tab === "teams" && (
        <div>
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Team</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Department</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Parent</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Members</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Created</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {adminTeamsLoading ? (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
                ) : adminTeams.map((t) => (
                  <tr key={t.id} className="border-t hover:bg-muted/20">
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium">{t.name}</div>
                      {t.description && <div className="text-xs text-muted-foreground">{t.description}</div>}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {t.department_id ? departments.find((d) => d.id === t.department_id)?.name || "Linked" : "-"}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {t.parent_id ? adminTeams.find((p) => p.id === t.parent_id)?.name || "Yes" : "-"}
                    </td>
                    <td className="px-4 py-3 text-sm">{t.member_count ?? 0}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">{new Date(t.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-sm text-right">
                      <button onClick={() => handleAdminDeleteTeam(t.id, t.name)} className="text-red-600 hover:underline">Delete</button>
                    </td>
                  </tr>
                ))}
                {adminTeams.length === 0 && !adminTeamsLoading && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">No teams found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">{adminTeamsTotal} total teams</p>
        </div>
      )}
    </div>
  );
}
