"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface TeamMember {
  user_id: string;
  role: string;
  user?: { email: string; full_name: string };
}

interface Team {
  id: string;
  name: string;
  description: string | null;
  members: TeamMember[];
  created_at: string;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTeamName, setNewTeamName] = useState("");
  const [newTeamDesc, setNewTeamDesc] = useState("");
  const [creating, setCreating] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [teamDetail, setTeamDetail] = useState<Team | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [addMemberId, setAddMemberId] = useState("");
  const [addMemberRole, setAddMemberRole] = useState("member");
  const [addingMember, setAddingMember] = useState(false);
  const [success, setSuccess] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiClient.listTeams();
      setTeams(data?.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load teams");
    } finally {
      setLoading(false);
    }
  };

  const loadTeamDetail = async (teamId: string) => {
    setLoadingDetail(true);
    setError("");
    try {
      const data = await apiClient.getTeam(teamId);
      setTeamDetail(data);
      setSelectedTeam(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load team");
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamName.trim()) return;
    setCreating(true);
    setError("");
    try {
      await apiClient.createTeam({ name: newTeamName.trim(), description: newTeamDesc.trim() || undefined });
      setNewTeamName("");
      setNewTeamDesc("");
      setShowCreateForm(false);
      setSuccess("Team created successfully");
      loadTeams();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create team");
    } finally {
      setCreating(false);
    }
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTeam || !addMemberId.trim()) return;
    setAddingMember(true);
    setError("");
    try {
      await apiClient.addTeamMember(selectedTeam.id, {
        user_id: addMemberId.trim(),
        role: addMemberRole,
      });
      setAddMemberId("");
      setAddMemberRole("member");
      setSuccess("Member added successfully");
      loadTeamDetail(selectedTeam.id);
      loadTeams();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add member");
    } finally {
      setAddingMember(false);
    }
  };

  const handleRemoveMember = async (teamId: string, userId: string) => {
    if (!confirm("Remove this member from the team?")) return;
    setError("");
    try {
      await apiClient.removeTeamMember(teamId, userId);
      setSuccess("Member removed");
      loadTeamDetail(teamId);
      loadTeams();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove member");
    }
  };

  const handleDeleteTeam = async (teamId: string) => {
    if (!confirm("Delete this team? This cannot be undone.")) return;
    setDeleting(true);
    setError("");
    try {
      await apiClient.deleteTeam(teamId);
      setSelectedTeam(null);
      setTeamDetail(null);
      setSuccess("Team deleted");
      loadTeams();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete team");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Teams</h1>
          <p className="text-muted-foreground">{teams.length} teams</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
        >
          {showCreateForm ? "Cancel" : "Create Team"}
        </button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      {success && <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">{success}</div>}

      {showCreateForm && (
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Create New Team</h2>
          <form onSubmit={handleCreateTeam} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Team Name</label>
              <input
                type="text"
                value={newTeamName}
                onChange={(e) => setNewTeamName(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                placeholder="e.g. Genomics Lab"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Description (optional)</label>
              <input
                type="text"
                value={newTeamDesc}
                onChange={(e) => setNewTeamDesc(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                placeholder="Team purpose..."
              />
            </div>
            <button
              type="submit"
              disabled={creating || !newTeamName.trim()}
              className="inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              {creating ? "Creating..." : "Create Team"}
            </button>
          </form>
        </div>
      )}

      <div className="flex gap-6">
        <div className="w-1/2 space-y-3">
          <h2 className="text-lg font-semibold">Your Teams</h2>
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
            </div>
          ) : teams.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground rounded-lg border">No teams yet.</div>
          ) : (
            teams.map((team) => (
              <div
                key={team.id}
                onClick={() => loadTeamDetail(team.id)}
                className={`rounded-lg border p-4 cursor-pointer hover:shadow-md transition-shadow ${
                  selectedTeam?.id === team.id ? "border-green-600 bg-green-50" : "bg-card"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">{team.name}</h3>
                    {team.description && <p className="text-sm text-muted-foreground mt-1">{team.description}</p>}
                  </div>
                  <span className="text-sm text-muted-foreground">{team.members?.length ?? 0} members</span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="w-1/2">
          {loadingDetail ? (
            <div className="flex justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
            </div>
          ) : teamDetail ? (
            <div className="space-y-4">
              <div className="rounded-lg border bg-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-bold">{teamDetail.name}</h2>
                    {teamDetail.description && <p className="text-sm text-muted-foreground mt-1">{teamDetail.description}</p>}
                  </div>
                  <button
                    onClick={() => handleDeleteTeam(teamDetail.id)}
                    disabled={deleting}
                    className="inline-flex items-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                  >
                    {deleting ? "Deleting..." : "Delete Team"}
                  </button>
                </div>

                <div className="rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-2 text-left font-medium">User</th>
                        <th className="px-4 py-2 text-left font-medium">Role</th>
                        <th className="px-4 py-2 text-right font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(teamDetail.members ?? []).map((m) => (
                        <tr key={m.user_id} className="border-b last:border-0">
                          <td className="px-4 py-2">{m.user?.full_name || m.user?.email || m.user_id}</td>
                          <td className="px-4 py-2">
                            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800">{m.role}</span>
                          </td>
                          <td className="px-4 py-2 text-right">
                            <button
                              onClick={() => handleRemoveMember(teamDetail.id, m.user_id)}
                              className="text-sm text-red-600 hover:text-red-800"
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                      {(!teamDetail.members || teamDetail.members.length === 0) && (
                        <tr>
                          <td colSpan={3} className="px-4 py-4 text-center text-muted-foreground">No members</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-lg border bg-card p-6">
                <h3 className="font-semibold mb-4">Add Member</h3>
                <form onSubmit={handleAddMember} className="flex gap-3 items-end">
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-1">User ID</label>
                    <input
                      type="text"
                      value={addMemberId}
                      onChange={(e) => setAddMemberId(e.target.value)}
                      className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                      placeholder="Enter user ID"
                      required
                    />
                  </div>
                  <div className="w-36">
                    <label className="block text-sm font-medium mb-1">Role</label>
                    <select
                      value={addMemberRole}
                      onChange={(e) => setAddMemberRole(e.target.value)}
                      className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                    >
                      <option value="member">Member</option>
                      <option value="admin">Admin</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <button
                    type="submit"
                    disabled={addingMember || !addMemberId.trim()}
                    className="inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
                  >
                    {addingMember ? "Adding..." : "Add"}
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground rounded-lg border">Select a team to view details.</div>
          )}
        </div>
      </div>
    </div>
  );
}
