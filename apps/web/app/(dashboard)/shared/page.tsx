"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface SharedItem {
  id: string;
  item_type: string;
  item_id: string;
  permission: string;
  visibility: string;
  shared_by?: { id: string; email: string; full_name: string };
  shared_with?: { id: string; email: string; full_name: string };
  created_at: string;
}

export default function SharedPage() {
  const [sharedWithMe, setSharedWithMe] = useState<SharedItem[]>([]);
  const [myShares, setMyShares] = useState<SharedItem[]>([]);
  const [loadingShared, setLoadingShared] = useState(true);
  const [loadingMine, setLoadingMine] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    loadSharedWithMe();
    loadMyShares();
  }, []);

  const loadSharedWithMe = async () => {
    setLoadingShared(true);
    try {
      const data = await apiClient.getSharedWithMe();
      setSharedWithMe(data?.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoadingShared(false);
    }
  };

  const loadMyShares = async () => {
    setLoadingMine(true);
    try {
      const data = await apiClient.getMyShares();
      setMyShares(data?.items ?? []);
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
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground">{new Date(item.created_at).toLocaleDateString()}</span>
        {showRevoke && (
          <button
            onClick={() => handleRevoke(item.id)}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Revoke
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Shared</h1>
        <p className="text-muted-foreground">Items shared with you and by you</p>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      {success && <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">{success}</div>}

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
    </div>
  );
}
