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
  owner_id?: string;
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
  const [shareEmail, setShareEmail] = useState("");
  const [shareMessage, setShareMessage] = useState("");
  const [sharing, setSharing] = useState(false);
  const [userSearchQuery, setUserSearchQuery] = useState("");
  const [userSearchResults, setUserSearchResults] = useState<{ id: string; email: string; full_name: string }[]>([]);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const [showInviteByEmail, setShowInviteByEmail] = useState(false);

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

  const handleShareTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teamDetail) return;
    setSharing(true);
    setError("");
    try {
      await apiClient.shareItem({
        item_type: "team",
        item_id: teamDetail.id,
        visibility: "link",
        permission: "read",
      });
      setSuccess("Team link generated");
      setShareMessage("");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to share");
    } finally {
      setSharing(false);
    }
  };

  const handleUserSearch = async (query: string) => {
    setUserSearchQuery(query);
    if (query.length < 2) {
      setUserSearchResults([]);
      return;
    }
    setSearchingUsers(true);
    try {
      const data = await apiClient.searchUsers(query);
      setUserSearchResults(data?.items ?? []);
    } catch {
      setUserSearchResults([]);
    } finally {
      setSearchingUsers(false);
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
                    {teamDetail.owner_id && <p className="text-xs text-muted-foreground mt-1">Owner: {teamDetail.owner_id}</p>}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setShowInviteByEmail(!showInviteByEmail)}
                      className="inline-flex items-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                    >
                      Invite by Email
                    </button>
                    <button
                      onClick={() => handleDeleteTeam(teamDetail.id)}
                      disabled={deleting}
                      className="inline-flex items-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                    >
                      {deleting ? "Deleting..." : "Delete Team"}
                    </button>
                  </div>
                </div>

                {showInviteByEmail && (
                  <form onSubmit={handleShareTeam} className="mb-4 rounded-md border bg-muted/50 p-4 space-y-3">
                    <h3 className="text-sm font-medium">Invite via Email</h3>
                    <input
                      type="email"
                      value={shareEmail}
                      onChange={(e) => setShareEmail(e.target.value)}
                      placeholder="colleague@university.edu"
                      className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                    />
                    <input
                      type="text"
                      value={shareMessage}
                      onChange={(e) => setShareMessage(e.target.value)}
                      placeholder="Message (optional)"
                      className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                    />
                    <div className="flex gap-2">
                      <button type="submit" disabled={sharing || !shareEmail} className="text-sm text-green-600 hover:underline disabled:opacity-50">{sharing ? "Sending..." : "Send Invite"}</button>
                      <button type="button" onClick={() => setShowInviteByEmail(false)} className="text-sm text-muted-foreground hover:underline">Cancel</button>
                    </div>
                  </form>
                )}

                <div className="rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-2 text-left font-medium">User</th>
                        <th className="px-4 py-2 text-left font-medium">Email</th>
                        <th className="px-4 py-2 text-left font-medium">Role</th>
                        <th className="px-4 py-2 text-right font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(teamDetail.members ?? []).map((m) => (
                        <tr key={m.user_id} className="border-b last:border-0">
                          <td className="px-4 py-2">{m.user?.full_name || m.user_id}</td>
                          <td className="px-4 py-2 text-muted-foreground">{m.user?.email || "-"}</td>
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
                          <td colSpan={4} className="px-4 py-4 text-center text-muted-foreground">No members</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-lg border bg-card p-6">
                <h3 className="font-semibold mb-4">Add Member</h3>
                <form onSubmit={handleAddMember} className="space-y-3">
                  <div className="relative">
                    <label className="block text-sm font-medium mb-1">Search Users</label>
                    <input
                      type="text"
                      value={userSearchQuery}
                      onChange={(e) => handleUserSearch(e.target.value)}
                      placeholder="Search by email or name..."
                      className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                    />
                    {userSearchResults.length > 0 && (
                      <div className="absolute z-10 mt-1 w-full rounded-md border bg-background shadow-lg max-h-40 overflow-y-auto">
                        {userSearchResults.map((user) => (
                          <button
                            key={user.id}
                            type="button"
                            onClick={() => {
                              setAddMemberId(user.id);
                              setUserSearchQuery(user.full_name + " (" + user.email + ")");
                              setUserSearchResults([]);
                            }}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-muted"
                          >
                            {user.full_name} ({user.email})
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  {addMemberId && (
                    <div className="text-xs text-green-600">Selected user ID: {addMemberId}</div>
                  )}
                  <div className="flex gap-3 items-end">
                    <div className="flex-1">
                      <label className="block text-sm font-medium mb-1">Or enter User ID directly</label>
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
                  </div>
                </form>
              </div>

              <div className="rounded-lg border bg-card p-6">
                <h3 className="font-semibold mb-4">Team Working Environment</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="rounded-md bg-muted/50 p-3">
                    <span className="font-medium">Team Name:</span> {teamDetail.name}
                  </div>
                  <div className="rounded-md bg-muted/50 p-3">
                    <span className="font-medium">Members:</span> {teamDetail.members?.length ?? 0}
                  </div>
                  <div className="rounded-md bg-muted/50 p-3">
                    <span className="font-medium">Created:</span> {new Date(teamDetail.created_at).toLocaleDateString()}
                  </div>
                  <div className="rounded-md bg-muted/50 p-3">
                    <span className="font-medium">Description:</span> {teamDetail.description || "None"}
                  </div>
                </div>
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
