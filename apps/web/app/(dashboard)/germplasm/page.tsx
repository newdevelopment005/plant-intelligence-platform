"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";

interface Species {
  id: string;
  common_name: string;
  scientific_name: string;
  family: string | null;
  genus: string | null;
  created_at: string;
}

export default function GermplasmPage() {
  const [activeTab, setActiveTab] = useState<"species" | "accessions">("species");
  const [species, setSpecies] = useState<Species[]>([]);
  const [speciesTotal, setSpeciesTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreateSpecies, setShowCreateSpecies] = useState(false);
  const [newSpecies, setNewSpecies] = useState({
    common_name: "",
    scientific_name: "",
    family: "",
    genus: "",
    species_epithet: "",
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ common_name: "", scientific_name: "", family: "", genus: "" });

  useEffect(() => {
    loadSpecies();
  }, []);

  const loadSpecies = async (searchQuery?: string) => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.set("search", searchQuery);
      const data = await apiClient.request(`/germplasm/species?${params.toString()}`);
      setSpecies(data?.items ?? []);
      setSpeciesTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load species");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadSpecies(search || undefined);
  };

  const handleCreateSpecies = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.request("/germplasm/species", {
        method: "POST",
        body: JSON.stringify({
          common_name: newSpecies.common_name,
          scientific_name: newSpecies.scientific_name,
          family: newSpecies.family || undefined,
          genus: newSpecies.genus || undefined,
          species_epithet: newSpecies.species_epithet || undefined,
        }),
      });
      setShowCreateSpecies(false);
      setNewSpecies({ common_name: "", scientific_name: "", family: "", genus: "", species_epithet: "" });
      loadSpecies();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create species");
    }
  };

  const startEdit = (s: Species) => {
    setEditingId(s.id);
    setEditForm({ common_name: s.common_name, scientific_name: s.scientific_name, family: s.family || "", genus: s.genus || "" });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateSpecies(editingId, {
        common_name: editForm.common_name,
        scientific_name: editForm.scientific_name,
        family: editForm.family || undefined,
        genus: editForm.genus || undefined,
      });
      setEditingId(null);
      loadSpecies();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this species?")) return;
    try {
      await apiClient.deleteSpecies(id);
      loadSpecies();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Germplasm Repository</h1>
          <p className="text-muted-foreground">Manage species, accessions, and germplasm data</p>
        </div>
      </div>

      <div className="flex gap-1 border-b">
        {(["species", "accessions"] as const).map((tab) => (
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

      {error && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}

      {activeTab === "species" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <form onSubmit={handleSearch} className="flex gap-2 flex-1 max-w-md">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search species..."
                className="flex-1 rounded-md border px-3 py-2"
              />
              <button type="submit" className="rounded-md border px-4 py-2 hover:bg-gray-50">
                Search
              </button>
            </form>
            <button
              onClick={() => setShowCreateSpecies(true)}
              className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
            >
              Add Species
            </button>
          </div>

          {showCreateSpecies && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
              <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
                <h2 className="text-xl font-bold mb-4">Add Species</h2>
                <form onSubmit={handleCreateSpecies} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium">Common Name *</label>
                    <input
                      type="text"
                      required
                      value={newSpecies.common_name}
                      onChange={(e) => setNewSpecies({ ...newSpecies, common_name: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                      placeholder="Common wheat"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Scientific Name *</label>
                    <input
                      type="text"
                      required
                      value={newSpecies.scientific_name}
                      onChange={(e) => setNewSpecies({ ...newSpecies, scientific_name: e.target.value })}
                      className="mt-1 block w-full rounded-md border px-3 py-2"
                      placeholder="Triticum aestivum"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium">Family</label>
                      <input
                        type="text"
                        value={newSpecies.family}
                        onChange={(e) => setNewSpecies({ ...newSpecies, family: e.target.value })}
                        className="mt-1 block w-full rounded-md border px-3 py-2"
                        placeholder="Poaceae"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium">Genus</label>
                      <input
                        type="text"
                        value={newSpecies.genus}
                        onChange={(e) => setNewSpecies({ ...newSpecies, genus: e.target.value })}
                        className="mt-1 block w-full rounded-md border px-3 py-2"
                        placeholder="Triticum"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2 justify-end">
                    <button
                      type="button"
                      onClick={() => setShowCreateSpecies(false)}
                      className="rounded-md border px-4 py-2 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                    >
                      Add
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {editingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Edit Species</h2>
            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Common Name *</label>
                <input
                  type="text"
                  required
                  value={editForm.common_name}
                  onChange={(e) => setEditForm({ ...editForm, common_name: e.target.value })}
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium">Scientific Name *</label>
                <input
                  type="text"
                  required
                  value={editForm.scientific_name}
                  onChange={(e) => setEditForm({ ...editForm, scientific_name: e.target.value })}
                  className="mt-1 block w-full rounded-md border px-3 py-2 italic"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Family</label>
                  <input
                    type="text"
                    value={editForm.family}
                    onChange={(e) => setEditForm({ ...editForm, family: e.target.value })}
                    className="mt-1 block w-full rounded-md border px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Genus</label>
                  <input
                    type="text"
                    value={editForm.genus}
                    onChange={(e) => setEditForm({ ...editForm, genus: e.target.value })}
                    className="mt-1 block w-full rounded-md border px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setEditingId(null)}
                  className="rounded-md border px-4 py-2 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                >
                  Save
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
          ) : species.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No species found. Add your first species to get started.
            </div>
          ) : (
            <div className="rounded-lg border">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="px-4 py-3 text-left text-sm font-medium">Common Name</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Scientific Name</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Family</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Genus</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Added</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {species.map((s) => (
                    <tr key={s.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium">{s.common_name}</td>
                      <td className="px-4 py-3 text-sm italic text-muted-foreground">{s.scientific_name}</td>
                      <td className="px-4 py-3 text-sm">{s.family || "-"}</td>
                      <td className="px-4 py-3 text-sm">{s.genus || "-"}</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {new Date(s.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button onClick={() => startEdit(s)} className="text-xs text-blue-600 hover:underline">Edit</button>
                          <button onClick={() => handleDelete(s.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === "accessions" && (
        <div className="text-center py-12 text-muted-foreground">
          <Link href="/germplasm/accessions" className="text-green-600 hover:underline">
            Go to Accessions →
          </Link>
        </div>
      )}
    </div>
  );
}
