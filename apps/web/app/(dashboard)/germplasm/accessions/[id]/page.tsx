"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";

interface Accession {
  id: string;
  accession_number: string;
  name: string;
  species_id: string;
  description: string | null;
  collection_source: string | null;
  collection_date: string | null;
  collection_location: string | null;
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  availability_status: string;
  tags: string[] | null;
  metadata: Record<string, unknown> | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface SeedStorage {
  id: string;
  location: string;
  container_type: string | null;
  quantity_grams: number | null;
  seed_count: number | null;
  storage_conditions: string | null;
  storage_date: string | null;
  expiry_date: string | null;
  viability: number | null;
  notes: string | null;
}

interface GermplasmImage {
  id: string;
  filename: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  caption: string | null;
  image_type: string | null;
  created_at: string;
}

export default function AccessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const accessionId = params.id as string;

  const [accession, setAccession] = useState<Accession | null>(null);
  const [storages, setStorages] = useState<SeedStorage[]>([]);
  const [images, setImages] = useState<GermplasmImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "passport" | "pedigree" | "storage" | "images">("overview");
  const [showAddStorage, setShowAddStorage] = useState(false);
  const [newStorage, setNewStorage] = useState({
    location: "",
    container_type: "",
    quantity_grams: "",
    seed_count: "",
    storage_conditions: "",
  });
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    name: "",
    description: "",
    collection_source: "",
    collection_location: "",
    availability_status: "available",
  });

  useEffect(() => {
    loadAccession();
  }, [accessionId]);

  const loadAccession = async () => {
    setLoading(true);
    try {
      const data = await apiClient.request(`/germplasm/accessions/${accessionId}`);
      setAccession(data);
      const storagesData = await apiClient.request(`/germplasm/accessions/${accessionId}/storage`);
      setStorages(storagesData);
      const imagesData = await apiClient.request(`/germplasm/accessions/${accessionId}/images`);
      setImages(imagesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load accession");
    } finally {
      setLoading(false);
    }
  };

  const handleAddStorage = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.request(`/germplasm/accessions/${accessionId}/storage`, {
        method: "POST",
        body: JSON.stringify({
          location: newStorage.location,
          container_type: newStorage.container_type || undefined,
          quantity_grams: newStorage.quantity_grams ? parseFloat(newStorage.quantity_grams) : undefined,
          seed_count: newStorage.seed_count ? parseInt(newStorage.seed_count) : undefined,
          storage_conditions: newStorage.storage_conditions || undefined,
        }),
      });
      setShowAddStorage(false);
      setNewStorage({ location: "", container_type: "", quantity_grams: "", seed_count: "", storage_conditions: "" });
      loadAccession();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add storage");
    }
  };

  const startEdit = () => {
    if (!accession) return;
    setEditing(true);
    setEditForm({
      name: accession.name,
      description: accession.description || "",
      collection_source: accession.collection_source || "",
      collection_location: accession.collection_location || "",
      availability_status: accession.availability_status,
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.updateAccession(accessionId, {
        name: editForm.name,
        description: editForm.description || undefined,
        collection_source: editForm.collection_source || undefined,
        collection_location: editForm.collection_location || undefined,
        availability_status: editForm.availability_status,
      });
      setEditing(false);
      loadAccession();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this accession? This action cannot be undone.")) return;
    try {
      await apiClient.deleteAccession(accessionId);
      router.push("/germplasm/accessions");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Not set";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !accession) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || "Accession not found"}</p>
        <Link href="/germplasm/accessions" className="text-green-600 hover:underline">
          Back to accessions
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/germplasm/accessions" className="text-sm text-muted-foreground hover:text-foreground">
          ← Back to accessions
        </Link>
        <div className="flex items-start justify-between mt-2">
          <div>
            {editing ? (
              <form onSubmit={handleUpdate} className="space-y-3">
                <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-2xl font-bold" placeholder="Name" />
                <input type="text" value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Description" />
                <div className="grid grid-cols-2 gap-3">
                  <input type="text" value={editForm.collection_source} onChange={(e) => setEditForm({ ...editForm, collection_source: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Collection source" />
                  <input type="text" value={editForm.collection_location} onChange={(e) => setEditForm({ ...editForm, collection_location: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Collection location" />
                </div>
                <select value={editForm.availability_status} onChange={(e) => setEditForm({ ...editForm, availability_status: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm">
                  <option value="available">Available</option>
                  <option value="limited">Limited</option>
                  <option value="unavailable">Unavailable</option>
                </select>
                <div className="flex gap-2">
                  <button type="submit" className="text-sm text-green-600 hover:underline">Save</button>
                  <button type="button" onClick={() => setEditing(false)} className="text-sm text-muted-foreground hover:underline">Cancel</button>
                </div>
              </form>
            ) : (
              <>
                <h1 className="text-3xl font-bold">{accession.name}</h1>
                <p className="text-muted-foreground">{accession.accession_number}</p>
              </>
            )}
          </div>
          {!editing && (
            <div className="flex items-center gap-3">
              <span
                className={`rounded-full px-3 py-1 text-sm font-medium ${
                  accession.availability_status === "available"
                    ? "bg-green-100 text-green-800"
                    : accession.availability_status === "limited"
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {accession.availability_status}
              </span>
              <button onClick={startEdit} className="text-sm text-blue-600 hover:underline">Edit</button>
              <button onClick={handleDelete} className="text-sm text-red-600 hover:underline">Delete</button>
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-1 border-b">
        {(["overview", "passport", "pedigree", "storage", "images"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              activeTab === tab
                ? "border-b-2 border-green-600 text-green-600"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-2">Description</h3>
              <p className="text-sm text-muted-foreground">
                {accession.description || "No description provided"}
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-2">Collection Info</h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Source</dt>
                  <dd>{accession.collection_source || "-"}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Date</dt>
                  <dd>{formatDate(accession.collection_date)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Location</dt>
                  <dd>{accession.collection_location || "-"}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Coordinates</dt>
                  <dd>
                    {accession.latitude && accession.longitude
                      ? `${accession.latitude.toFixed(4)}, ${accession.longitude.toFixed(4)}`
                      : "-"}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Altitude</dt>
                  <dd>{accession.altitude ? `${accession.altitude}m` : "-"}</dd>
                </div>
              </dl>
            </div>
          </div>
          <div className="space-y-4">
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-2">Details</h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Created</dt>
                  <dd>{formatDate(accession.created_at)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Last Updated</dt>
                  <dd>{formatDate(accession.updated_at)}</dd>
                </div>
              </dl>
            </div>
            {accession.tags && accession.tags.length > 0 && (
              <div className="rounded-lg border p-4">
                <h3 className="font-medium mb-2">Tags</h3>
                <div className="flex gap-2 flex-wrap">
                  {accession.tags.map((tag) => (
                    <span key={tag} className="rounded bg-gray-100 px-2 py-1 text-sm">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "passport" && (
        <div className="rounded-lg border p-6">
          <h3 className="font-medium mb-4">Passport Data</h3>
          <p className="text-sm text-muted-foreground">
            Passport data for this accession is managed through the API.
          </p>
        </div>
      )}

      {activeTab === "pedigree" && (
        <div className="rounded-lg border p-6">
          <h3 className="font-medium mb-4">Pedigree</h3>
          <p className="text-sm text-muted-foreground">
            Pedigree information for this accession is managed through the API.
          </p>
        </div>
      )}

      {activeTab === "storage" && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-medium">Seed Storage Locations ({storages.length})</h3>
            <button
              onClick={() => setShowAddStorage(true)}
              className="rounded-md bg-green-600 px-4 py-2 text-white text-sm hover:bg-green-700"
            >
              Add Storage
            </button>
          </div>

          {showAddStorage && (
            <div className="rounded-lg border p-4 bg-gray-50">
              <h4 className="font-medium mb-3">Add Storage Location</h4>
              <form onSubmit={handleAddStorage} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium">Location *</label>
                    <input
                      type="text"
                      required
                      value={newStorage.location}
                      onChange={(e) => setNewStorage({ ...newStorage, location: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                      placeholder="Genebank vault A"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Container Type</label>
                    <input
                      type="text"
                      value={newStorage.container_type}
                      onChange={(e) => setNewStorage({ ...newStorage, container_type: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                      placeholder="Paper envelope"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm font-medium">Quantity (g)</label>
                    <input
                      type="number"
                      step="any"
                      value={newStorage.quantity_grams}
                      onChange={(e) => setNewStorage({ ...newStorage, quantity_grams: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Seed Count</label>
                    <input
                      type="number"
                      value={newStorage.seed_count}
                      onChange={(e) => setNewStorage({ ...newStorage, seed_count: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Conditions</label>
                    <input
                      type="text"
                      value={newStorage.storage_conditions}
                      onChange={(e) => setNewStorage({ ...newStorage, storage_conditions: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                      placeholder="-18°C, 20% RH"
                    />
                  </div>
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    type="button"
                    onClick={() => setShowAddStorage(false)}
                    className="rounded-md border px-3 py-1 text-sm hover:bg-gray-100"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-md bg-green-600 px-3 py-1 text-white text-sm hover:bg-green-700"
                  >
                    Add
                  </button>
                </div>
              </form>
            </div>
          )}

          {storages.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No storage locations recorded.</div>
          ) : (
            <div className="rounded-lg border">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="px-4 py-3 text-left text-sm font-medium">Location</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Container</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Quantity</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Conditions</th>
                  </tr>
                </thead>
                <tbody>
                  {storages.map((s) => (
                    <tr key={s.id} className="border-b last:border-0">
                      <td className="px-4 py-3 text-sm font-medium">{s.location}</td>
                      <td className="px-4 py-3 text-sm">{s.container_type || "-"}</td>
                      <td className="px-4 py-3 text-sm">
                        {s.quantity_grams ? `${s.quantity_grams}g` : s.seed_count ? `${s.seed_count} seeds` : "-"}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{s.storage_conditions || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === "images" && (
        <div className="space-y-4">
          <h3 className="font-medium">Images ({images.length})</h3>
          {images.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No images uploaded.</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {images.map((img) => (
                <div key={img.id} className="rounded-lg border overflow-hidden">
                  <div className="aspect-square bg-gray-100 flex items-center justify-center text-muted-foreground text-sm">
                    {img.image_type || "Image"}
                  </div>
                  <div className="p-2">
                    <p className="text-xs truncate">{img.original_filename}</p>
                    <p className="text-xs text-muted-foreground">{formatFileSize(img.file_size)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
