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

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"users" | "audit">("users");

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

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await apiClient.adminUpdateUserRole(userId, newRole);
      setUsers(users.map((u) => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin</h1>
        <p className="text-muted-foreground">{total} users</p>
      </div>

      <div className="flex gap-4 border-b">
        <button onClick={() => setTab("users")} className={`pb-2 px-4 text-sm font-medium ${tab === "users" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Users</button>
        <button onClick={() => setTab("audit")} className={`pb-2 px-4 text-sm font-medium ${tab === "audit" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Audit Log</button>
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
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
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
