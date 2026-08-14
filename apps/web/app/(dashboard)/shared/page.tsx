"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface SharedItem {
  id: string;
  item_type: string;
  item_id: string;
  permission: string;
  visibility: string;
  owner?: { id: string; email: string; full_name: string } | null;
  shared_by?: { id: string; email: string; full_name: string };
  shared_with?: { id: string; email: string; full_name: string };
  recipients?: { user_id: string; permission: string; user?: { full_name?: string; email?: string } | null }[];
  created_at: string;
}

export default function SharedPage() {
  const [sharedWithMe, setSharedWithMe] = useState<SharedItem[]>([]);
  const [myShares, setMyShares] = useState<SharedItem[]>([]);
  const [loadingShared, setLoadingShared] = useState(true);
  const [loadingMine, setLoadingMine] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showShareForm, setShowShareForm] = useState(false);
  const [shareItemType, setShareItemType] = useState("image");
  const [shareItemId, setShareItemId] = useState("");
  const [shareVisibility, setShareVisibility] = useState("private");
  const [sharePermission, setSharePermission] = useState("read");
  const [shareUserId, setShareUserId] = useState("");
  const [shareEmails, setShareEmails] = useState("");
  const [shareTeamId, setShareTeamId] = useState("");
  const [shareDeptId, setShareDeptId] = useState("");
  const [teams, setTeams] = useState<{ id: string; name: string }[]>([]);
  const [departments, setDepartments] = useState<{ id: string; name: string }[]>([]);
  const [userSearchQuery, setUserSearchQuery] = useState("");
  const [userSearchResults, setUserSearchResults] = useState<{ id: string; email: string; full_name: string }[]>([]);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [viewingItem, setViewingItem] = useState<SharedItem | null>(null);

  useEffect(() => {
    loadSharedWithMe();
    loadMyShares();
    loadTeamsAndDepartments();
  }, []);

  const loadTeamsAndDepartments = async () => {
    try {
      const [teamData, deptData] = await Promise.all([
        apiClient.listTeams(),
        apiClient.listDepartments(),
      ]);
      setTeams((teamData?.items ?? []).map((t: any) => ({ id: t.id, name: t.name })));
      setDepartments((deptData?.items ?? []).map((d: any) => ({ id: d.id, name: d.name })));
    } catch {
      setTeams([]);
      setDepartments([]);
    }
  };

  const loadSharedWithMe = async () => {
    setLoadingShared(true);
    try {
      const data: any = await apiClient.getSharedWithMe();
      const list = Array.isArray(data) ? data : (data?.items ?? []);
      setSharedWithMe(list.map((entry: any) => {
        const share = entry.share || {};
        const recipient = entry.recipient || {};
        return {
          id: share.id,
          item_type: share.item_type,
          item_id: share.item_id,
          permission: recipient.permission || share.permission || "read",
          visibility: share.visibility,
          created_at: share.created_at,
          owner: share.owner || null,
          shared_by: share.owner || null,
          shared_with: recipient.user || null,
          recipients: [recipient],
        };
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoadingShared(false);
    }
  };

  const loadMyShares = async () => {
    setLoadingMine(true);
    try {
      const data: any = await apiClient.getMyShares();
      const list = Array.isArray(data) ? data : (data?.items ?? []);
      setMyShares(list.map((entry: any) => {
        const share = entry.share || {};
        const recipients = entry.recipients || [];
        return {
          id: share.id,
          item_type: share.item_type,
          item_id: share.item_id,
          permission: "read",
          visibility: share.visibility,
          created_at: share.created_at,
          owner: share.owner || null,
          recipients,
        };
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoadingMine(false);
    }
  };

  const handleRevoke = async (shareId: string) => {
    if (!confirm("Revoke this share?")) return;
    setError("");
    try {
      await apiClient.revokeShare(shareId);
      setSuccess("Share revoked");
      loadMyShares();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to revoke share");
    }
  };

  const handleRemoveAccess = async (shareId: string) => {
    if (!confirm("Remove this share from your list? You will lose access to the item.")) return;
    setError("");
    try {
      await apiClient.removeMyShareAccess(shareId);
      setSuccess("Share access removed");
      loadSharedWithMe();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove access");
    }
  };

  const ITEM_ROUTES: Record<string, string> = {
    image: "/images",
    report: "/reports",
    notebook_entry: "/notebook",
    paper: "/literature",
    sample: "/lims",
    team: "/teams",
    entity: "/knowledge-graph",
    experiment: "/phenotyping",
  };

  const itemRoute = (item: SharedItem): string | null => {
    if (item.item_type === "project") return `/projects/${item.item_id}`;
    if (item.item_type === "accession" || item.item_type === "germplasm") {
      return `/germplasm/accessions/${item.item_id}`;
    }
    return ITEM_ROUTES[item.item_type] ?? null;
  };

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!shareItemId.trim()) return;
    setSharing(true);
    setError("");
    try {
      const payload: any = {
        item_type: shareItemType,
        item_id: shareItemId.trim(),
        visibility: shareVisibility,
        permission: sharePermission,
      };
      if (shareUserId.trim()) {
        payload.user_ids = [shareUserId.trim()];
      }
      if (shareEmails.trim()) {
        payload.emails = shareEmails
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
      }
      if (shareTeamId) {
        payload.team_ids = [shareTeamId];
      }
      if (shareDeptId) {
        payload.department_ids = [shareDeptId];
      }
      await apiClient.shareItem(payload);
      setSuccess("Item shared successfully");
      setShowShareForm(false);
      setShareItemId("");
      setShareUserId("");
      setShareEmails("");
      setShareTeamId("");
      setShareDeptId("");
      setUserSearchQuery("");
      setUserSearchResults([]);
      loadMyShares();
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

  const renderSharedItem = (item: SharedItem, showRevoke = false) => (
    <div key={item.id} className="rounded-lg border bg-card p-4 flex items-center justify-between">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800">{item.item_type}</span>
          <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-800">{item.permission}</span>
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-800">{item.visibility}</span>
        </div>
        <p className="text-sm text-muted-foreground">
          ID: <span className="font-mono text-foreground">{item.item_id}</span>
        </p>
        {item.shared_by && (
          <p className="text-xs text-muted-foreground">
            Shared by: {item.shared_by.full_name || item.shared_by.email}
          </p>
        )}
        {item.shared_with && (
          <p className="text-xs text-muted-foreground">
            Shared with: {item.shared_with.full_name || item.shared_with.email}
          </p>
        )}
        {item.recipients && item.recipients.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Recipients:{" "}
            {item.recipients
              .map((r) => r.user?.full_name || r.user?.email || r.user_id.slice(0, 8))
              .join(", ")}
          </p>
        )}
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground">{new Date(item.created_at).toLocaleDateString()}</span>
        <button
          onClick={() => setViewingItem(item)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          View
        </button>
        {(showRevoke || item.permission === "write") && itemRoute(item) && (
          <a href={itemRoute(item)!} className="text-sm text-green-600 hover:text-green-800">
            Edit
          </a>
        )}
        {showRevoke ? (
          <button
            onClick={() => handleRevoke(item.id)}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Revoke
          </button>
        ) : item.shared_with ? (
          <button
            onClick={() => handleRemoveAccess(item.id)}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Delete
          </button>
        ) : null}
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Shared</h1>
          <p className="text-muted-foreground">Items shared with you and by you</p>
        </div>
        <button
          onClick={() => setShowShareForm(!showShareForm)}
          className="inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
        >
          {showShareForm ? "Cancel" : "Share Item"}
        </button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      {success && <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">{success}</div>}

      {showShareForm && (
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Share an Item</h2>
          <form onSubmit={handleShare} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Item Type</label>
                <select value={shareItemType} onChange={(e) => setShareItemType(e.target.value)} className="w-full rounded-md border bg-background px-3 py-2 text-sm">
                  <option value="image">Image</option>
                  <option value="report">Report</option>
                  <option value="notebook_entry">Notebook Entry</option>
                  <option value="paper">Paper</option>
                  <option value="project">Project</option>
                  <option value="sample">Sample</option>
                  <option value="team">Team</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Item ID *</label>
                <input
                  type="text"
                  value={shareItemId}
                  onChange={(e) => setShareItemId(e.target.value)}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  placeholder="Enter item ID"
                  required
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Visibility</label>
                <select value={shareVisibility} onChange={(e) => setShareVisibility(e.target.value)} className="w-full rounded-md border bg-background px-3 py-2 text-sm">
                  <option value="private">Private</option>
                  <option value="link">Link</option>
                  <option value="public">Public</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Permission</label>
                <select value={sharePermission} onChange={(e) => setSharePermission(e.target.value)} className="w-full rounded-md border bg-background px-3 py-2 text-sm">
                  <option value="read">Read</option>
                  <option value="write">Write</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Share with User (optional)</label>
              <div className="relative">
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
                          setShareUserId(user.id);
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
              {shareUserId && (
                <div className="text-xs text-green-600 mt-1">Selected user: {userSearchQuery || shareUserId}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Or share by email (optional)</label>
              <input
                type="text"
                value={shareEmails}
                onChange={(e) => setShareEmails(e.target.value)}
                placeholder="colleague@lab.edu, another@institute.org"
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Invites are emailed to registered addresses; unregistered ones receive a sign-up notice.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Share with Team (optional)</label>
                <select value={shareTeamId} onChange={(e) => setShareTeamId(e.target.value)} className="w-full rounded-md border bg-background px-3 py-2 text-sm">
                  <option value="">No team</option>
                  {teams.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-muted-foreground">All team members get access.</p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Share with Department (optional)</label>
                <select value={shareDeptId} onChange={(e) => setShareDeptId(e.target.value)} className="w-full rounded-md border bg-background px-3 py-2 text-sm">
                  <option value="">No department</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-muted-foreground">All department members get access.</p>
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowShareForm(false)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
              <button type="submit" disabled={sharing || !shareItemId.trim()} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50">
                {sharing ? "Sharing..." : "Share"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold mb-4">Shared With Me</h2>
        {loadingShared ? (
          <div className="flex justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
          </div>
        ) : sharedWithMe.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground rounded-lg border">No items shared with you.</div>
        ) : (
          <div className="space-y-3">
            {sharedWithMe.map((item) => renderSharedItem(item, false))}
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">My Shares</h2>
        {loadingMine ? (
          <div className="flex justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
          </div>
        ) : myShares.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground rounded-lg border">You haven&apos;t shared any items.</div>
        ) : (
          <div className="space-y-3">
            {myShares.map((item) => renderSharedItem(item, true))}
          </div>
        )}
      </div>

      {viewingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setViewingItem(null)}>
          <div className="w-full max-w-lg rounded-lg border bg-card p-6" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold">Shared Item Details</h3>
              <button onClick={() => setViewingItem(null)} className="text-sm text-muted-foreground hover:text-foreground">
                Close
              </button>
            </div>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Type</dt>
                <dd>{viewingItem.item_type}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Item ID</dt>
                <dd className="font-mono">{viewingItem.item_id}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Permission</dt>
                <dd>{viewingItem.permission}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Visibility</dt>
                <dd>{viewingItem.visibility}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Shared on</dt>
                <dd>{new Date(viewingItem.created_at).toLocaleString()}</dd>
              </div>
              {viewingItem.owner && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Owner</dt>
                  <dd>{viewingItem.owner.full_name || viewingItem.owner.email}</dd>
                </div>
              )}
            </dl>
            {itemRoute(viewingItem) && (
              <a
                href={itemRoute(viewingItem)!}
                className="mt-4 inline-block rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Open item
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
