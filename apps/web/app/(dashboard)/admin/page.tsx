"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
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

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"users" | "audit" | "system">("users");
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => { loadData(); }, []);

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
    }
  };

  const handleTabChange = (newTab: "users" | "audit" | "system") => {
    setTab(newTab);
    if (newTab === "system") {
      loadSystemHealth();
      loadStats();
    }
  };

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
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${user.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <button
                      onClick={() => handleRoleChange(user.id, user.role)}
                      className="text-blue-600 hover:underline"
                    >
                      Update
                    </button>
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
      ) : (
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
      )}
    </div>
  );
}
