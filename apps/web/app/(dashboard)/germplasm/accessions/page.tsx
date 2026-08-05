"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";

interface Accession {
  id: string;
  accession_number: string;
  name: string;
  species_id: string;
  description: string | null;
  availability_status: string;
  latitude: number | null;
  longitude: number | null;
  tags: string[] | null;
  created_at: string;
}

interface Species {
  id: string;
  common_name: string;
  scientific_name: string;
}

export default function AccessionsPage() {
  const [accessions, setAccessions] = useState<Accession[]>([]);
  const [total, setTotal] = useState(0);
  const [speciesList, setSpeciesList] = useState<Species[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [speciesFilter, setSpeciesFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newAccession, setNewAccession] = useState({
    accession_number: "",
    species_id: "",
    name: "",
    description: "",
    collection_source: "",
    latitude: "",
    longitude: "",
    tags: "",
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", description: "", availability_status: "available" });

  useEffect(() => {
    loadAccessions();
    loadSpecies();
  }, []);

  const loadAccessions = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (speciesFilter) params.set("species_id", speciesFilter);
      if (statusFilter) params.set("status", statusFilter);
      const data = await apiClient.request(`/germplasm/accessions?${params.toString()}`);
      setAccessions(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load accessions");
    } finally {
      setLoading(false);
    }
  };

  const loadSpecies = async () => {
    try {
      const data = await apiClient.request("/germplasm/species?limit=100");
      setSpeciesList(data?.items ?? []);
    } catch (err) {
      console.error("Failed to load species:", err);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadAccessions();
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const tags = newAccession.tags ? newAccession.tags.split(",").map((t) => t.trim()) : undefined;
      await apiClient.request("/germplasm/accessions", {
        method: "POST",
        body: JSON.stringify({
          accession_number: newAccession.accession_number,
          species_id: newAccession.species_id,
          name: newAccession.name,
          description: newAccession.description || undefined,
          collection_source: newAccession.collection_source || undefined,
          latitude: newAccession.latitude ? parseFloat(newAccession.latitude) : undefined,
          longitude: newAccession.longitude ? parseFloat(newAccession.longitude) : undefined,
          tags,
        }),
      });
      setShowCreate(false);
      setNewAccession({
        accession_number: "",
        species_id: "",
        name: "",
        description: "",
        collection_source: "",
        latitude: "",
        longitude: "",
        tags: "",
      });
      loadAccessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create accession");
    }
  };

  const startEdit = (a: Accession) => {
    setEditingId(a.id);
    setEditForm({ name: a.name, description: a.description || "", availability_status: a.availability_status });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateAccession(editingId, {
        name: editForm.name,
        description: editForm.description || undefined,
        availability_status: editForm.availability_status,
      });
      setEditingId(null);
      loadAccessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this accession?")) return;
    try {
      await apiClient.deleteAccession(id);
      loadAccessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  const statusColors: Record<string, string> = {
    available: "bg-green-100 text-green-800",
    limited: "bg-yellow-100 text-yellow-800",
    unavailable: "bg-red-100 text-red-800",
    reserved: "bg-blue-100 text-blue-800",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/germplasm" className="text-sm text-muted-foreground hover:text-foreground">
            ← Back to Germplasm
          </Link>
          <h1 className="text-3xl font-bold mt-2">Accessions</h1>
          <p className="text-muted-foreground">{total} accessions</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
        >
          New Accession
        </button>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 flex-wrap">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search accessions..."
          className="flex-1 min-w-[200px] rounded-md border px-3 py-2"
        />
        <select
          value={speciesFilter}
          onChange={(e) => setSpeciesFilter(e.target.value)}
          className="rounded-md border px-3 py-2"
        >
          <option value="">All Species</option>
          {speciesList.map((s) => (
            <option key={s.id} value={s.id}>
              {s.common_name} ({s.scientific_name})
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-md border px-3 py-2"
        >
          <option value="">All Status</option>
          <option value="available">Available</option>
          <option value="limited">Limited</option>
          <option value="unavailable">Unavailable</option>
          <option value="reserved">Reserved</option>
        </select>
        <button type="submit" className="rounded-md border px-4 py-2 hover:bg-gray-50">
          Search
        </button>
      </form>

      {error && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">New Accession</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Accession Number *</label>
                  <input
                    type="text"
                    required
                    value={newAccession.accession_number}
                    onChange={(e) => setNewAccession({ ...newAccession, accession_number: e.target.value })}
                    className="mt-1 block w-full rounded-md border px-3 py-2"
                    placeholder="PI 123456"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Name *</label>
                  <input
                    type="text"
                    required
                    value={newAccession.name}
                    onChange={(e) => setNewAccession({ ...newAccession, name: e.target.value })}
                    className="mt-1 block w-full rounded-md border px-3 py-2"
                    placeholder="Wheat landrace"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium">Species *</label>
                <select
                  required
                  value={newAccession.species_id}
                  onChange={(e) => setNewAccession({ ...newAccession, species_id: e.target.value })}
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                >
                  <option value="">Select species</option>
                  {speciesList.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.common_name} ({s.scientific_name})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Description</label>
                <textarea
                  value={newAccession.description}
                  onChange={(e) => setNewAccession({ ...newAccession, description: e.target.value })}
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                  rows={2}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    value={newAccession.latitude}
                    onChange={(e) => setNewAccession({ ...newAccession, latitude: e.target.value })}
                    className="mt-1 block w-full rounded-md border px-3 py-2"
                    placeholder="35.6762"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={newAccession.longitude}
                    onChange={(e) => setNewAccession({ ...newAccession, longitude: e.target.value })}
                    className="mt-1 block w-full rounded-md border px-3 py-2"
                    placeholder="139.6503"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium">Tags (comma separated)</label>
                <input
                  type="text"
                  value={newAccession.tags}
                  onChange={(e) => setNewAccession({ ...newAccession, tags: e.target.value })}
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                  placeholder="drought tolerant, high yield"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="rounded-md border px-4 py-2 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
        </div>
      ) : accessions.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No accessions found. Create your first accession to get started.
        </div>
      ) : (
        <div className="rounded-lg border">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="px-4 py-3 text-left text-sm font-medium">Accession #</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Location</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Added</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {accessions.map((a) => (
                <tr key={a.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium">
                    <Link href={`/germplasm/accessions/${a.id}`} className="text-green-600 hover:underline">
                      {a.accession_number}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {editingId === a.id ? (
                      <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="w-full rounded border px-2 py-1 text-sm" />
                    ) : (
                      a.name
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {editingId === a.id ? (
                      <select value={editForm.availability_status} onChange={(e) => setEditForm({ ...editForm, availability_status: e.target.value })} className="w-full rounded border px-2 py-1 text-sm">
                        <option value="available">Available</option>
                        <option value="limited">Limited</option>
                        <option value="unavailable">Unavailable</option>
                        <option value="reserved">Reserved</option>
                      </select>
                    ) : (
                      <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusColors[a.availability_status] || ""}`}>
                        {a.availability_status}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {a.latitude && a.longitude ? `${a.latitude.toFixed(2)}, ${a.longitude.toFixed(2)}` : "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {new Date(a.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    {editingId === a.id ? (
                      <div className="flex gap-2">
                        <button onClick={handleUpdate} className="text-xs text-green-600 hover:underline">Save</button>
                        <button onClick={() => setEditingId(null)} className="text-xs text-muted-foreground hover:underline">Cancel</button>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <button onClick={() => startEdit(a)} className="text-xs text-blue-600 hover:underline">Edit</button>
                        <button onClick={() => handleDelete(a.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
