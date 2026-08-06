"use client";

import { useEffect, useState, useRef } from "react";
import { apiClient } from "@/lib/api-client";

interface PlantImage {
  id: string;
  name: string;
  file_url: string;
  thumbnail_url: string | null;
  image_type: string;
  species: string | null;
  width: number | null;
  height: number | null;
  created_at: string;
}

export default function ImagesPage() {
  const [images, setImages] = useState<PlantImage[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [shareImageId, setShareImageId] = useState<string | null>(null);
  const [shareVisibility, setShareVisibility] = useState("private");
  const [shareUserId, setShareUserId] = useState("");
  const [sharePermission, setSharePermission] = useState("read");
  const [sharing, setSharing] = useState(false);
  const [userSearchQuery, setUserSearchQuery] = useState("");
  const [userSearchResults, setUserSearchResults] = useState<{ id: string; email: string; full_name: string }[]>([]);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", image_type: "" });

  useEffect(() => { loadImages(); }, []);

  const loadImages = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listImages();
      setImages(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", file.name);
      await apiClient.uploadImage(formData);
      loadImages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const startEdit = (img: PlantImage) => {
    setEditingId(img.id);
    setEditForm({ name: img.name, image_type: img.image_type });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateImage(editingId, editForm);
      setEditingId(null);
      loadImages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this image?")) return;
    try {
      await apiClient.deleteImage(id);
      loadImages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!shareImageId) return;
    setSharing(true);
    setError("");
    try {
      const payload: any = {
        item_type: "image",
        item_id: shareImageId,
        visibility: shareVisibility,
        permission: sharePermission,
      };
      if (shareUserId.trim()) {
        payload.user_ids = [shareUserId.trim()];
      }
      await apiClient.shareItem(payload);
      setSuccess("Image shared successfully");
      setShareImageId(null);
      setShareUserId("");
      setUserSearchQuery("");
      setUserSearchResults([]);
      setShareVisibility("private");
      setSharePermission("read");
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

  const getImageUrl = (url: string | null) => {
    if (!url) return null;
    if (url.startsWith("http")) return url;
    return `/api/images${url}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Images</h1>
          <p className="text-muted-foreground">{total} images</p>
        </div>
        <div>
          <input ref={fileInputRef} type="file" accept="image/*" onChange={handleUpload} className="hidden" id="image-upload" />
          <label htmlFor="image-upload" className={`inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700 cursor-pointer ${uploading ? "opacity-50" : ""}`}>
            {uploading ? "Uploading..." : "Upload Image"}
          </label>
        </div>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      {success && <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">{success}</div>}

      {loading ? (
        <div className="flex justify-center py-12"><div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" /></div>
      ) : images.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No images uploaded yet.</div>
      ) : (
        <div className="grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {images.map((img) => (
            <div key={img.id} className="rounded-lg border overflow-hidden hover:shadow-md transition-shadow">
              <div className="aspect-square bg-muted flex items-center justify-center">
                {getImageUrl(img.thumbnail_url) || getImageUrl(img.file_url) ? (
                  <img src={getImageUrl(img.thumbnail_url) || getImageUrl(img.file_url)!} alt={img.name} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-muted-foreground text-sm">No preview</span>
                )}
              </div>
              <div className="p-3">
                {editingId === img.id ? (
                  <form onSubmit={handleUpdate} className="space-y-2">
                    <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="block w-full rounded border px-2 py-1 text-sm" />
                    <select value={editForm.image_type} onChange={(e) => setEditForm({ ...editForm, image_type: e.target.value })} className="block w-full rounded border px-2 py-1 text-sm">
                      <option value="leaf">Leaf</option>
                      <option value="flower">Flower</option>
                      <option value="fruit">Fruit</option>
                      <option value="seed">Seed</option>
                      <option value="root">Root</option>
                      <option value="whole_plant">Whole Plant</option>
                      <option value="other">Other</option>
                    </select>
                    <div className="flex gap-1">
                      <button type="submit" className="text-xs text-green-600 hover:underline">Save</button>
                      <button type="button" onClick={() => setEditingId(null)} className="text-xs text-muted-foreground hover:underline">Cancel</button>
                    </div>
                  </form>
                ) : (
                  <>
                    <p className="text-sm font-medium truncate">{img.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800">{img.image_type}</span>
                      {img.species && <span className="text-xs text-muted-foreground">{img.species}</span>}
                    </div>
                    <div className="flex gap-2 mt-2">
                      <button onClick={() => startEdit(img)} className="text-xs text-blue-600 hover:underline">Edit</button>
                      <button onClick={() => setShareImageId(shareImageId === img.id ? null : img.id)} className="text-xs text-purple-600 hover:underline">Share</button>
                      <button onClick={() => handleDelete(img.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                    </div>
                    {shareImageId === img.id && (
                      <form onSubmit={handleShare} className="mt-2 space-y-2 rounded border bg-muted/50 p-2">
                        <select value={shareVisibility} onChange={(e) => setShareVisibility(e.target.value)} className="w-full rounded border bg-background px-2 py-1 text-xs">
                          <option value="private">Private</option>
                          <option value="link">Link</option>
                          <option value="public">Public</option>
                        </select>
                        <div className="relative">
                          <input
                            type="text"
                            value={userSearchQuery}
                            onChange={(e) => handleUserSearch(e.target.value)}
                            placeholder="Search by email or name..."
                            className="w-full rounded border bg-background px-2 py-1 text-xs"
                          />
                          {userSearchResults.length > 0 && (
                            <div className="absolute z-10 mt-1 w-full rounded border bg-background shadow-lg max-h-32 overflow-y-auto">
                              {userSearchResults.map((user) => (
                                <button
                                  key={user.id}
                                  type="button"
                                  onClick={() => {
                                    setShareUserId(user.id);
                                    setUserSearchQuery(user.email);
                                    setUserSearchResults([]);
                                  }}
                                  className="w-full px-2 py-1 text-left text-xs hover:bg-muted"
                                >
                                  {user.full_name} ({user.email})
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                        {shareUserId && (
                          <div className="text-xs text-green-600">Selected: {userSearchQuery}</div>
                        )}
                        <select value={sharePermission} onChange={(e) => setSharePermission(e.target.value)} className="w-full rounded border bg-background px-2 py-1 text-xs">
                          <option value="read">Read</option>
                          <option value="write">Write</option>
                        </select>
                        <div className="flex gap-1">
                          <button type="submit" disabled={sharing} className="text-xs text-green-600 hover:underline disabled:opacity-50">{sharing ? "Sharing..." : "Share"}</button>
                          <button type="button" onClick={() => { setShareImageId(null); setUserSearchQuery(""); setUserSearchResults([]); }} className="text-xs text-muted-foreground hover:underline">Cancel</button>
                        </div>
                      </form>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
