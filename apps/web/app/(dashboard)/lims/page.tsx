"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Sample {
  id: string;
  sample_code: string;
  sample_type: string;
  name: string;
  status: string;
  location: string | null;
  quantity: number | null;
  unit: string | null;
  created_at: string;
}

interface Equipment {
  id: string;
  name: string;
  equipment_code: string;
  status: string;
  category: string | null;
}

export default function LimsPage() {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"samples" | "equipment">("samples");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ sample_code: "", sample_type: "DNA", name: "", location: "" });
  const [selectedSample, setSelectedSample] = useState<Sample | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", sample_type: "DNA", status: "active", location: "" });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sampleData, equipData] = await Promise.all([
        apiClient.listSamples(),
        apiClient.listEquipment(),
      ]);
      setSamples(sampleData?.items ?? []);
      setTotal(sampleData?.total ?? 0);
      setEquipment(equipData?.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createSample(form);
      setShowCreate(false);
      setForm({ sample_code: "", sample_type: "DNA", name: "", location: "" });
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const startEdit = (s: Sample) => {
    setEditingId(s.id);
    setEditForm({ name: s.name, sample_type: s.sample_type, status: s.status, location: s.location || "" });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateSample(editingId, editForm);
      setEditingId(null);
      setSelectedSample(null);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDeleteSample = async (id: string) => {
    if (!confirm("Are you sure you want to delete this sample?")) return;
    try {
      await apiClient.deleteSample(id);
      setSelectedSample(null);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">LIMS</h1>
          <p className="text-muted-foreground">{total} samples</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Sample</button>
      </div>

      <div className="flex gap-4 border-b">
        <button onClick={() => setTab("samples")} className={`pb-2 px-4 text-sm font-medium ${tab === "samples" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Samples</button>
        <button onClick={() => setTab("equipment")} className={`pb-2 px-4 text-sm font-medium ${tab === "equipment" ? "border-b-2 border-green-600" : "text-muted-foreground"}`}>Equipment ({equipment.length})</button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">New Sample</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Sample Code *</label>
                <input type="text" required value={form.sample_code} onChange={(e) => setForm({ ...form, sample_code: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" placeholder="SMP-001" />
              </div>
              <div>
                <label className="block text-sm font-medium">Name *</label>
                <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Type</label>
                <select value={form.sample_type} onChange={(e) => setForm({ ...form, sample_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="DNA">DNA</option>
                  <option value="RNA">RNA</option>
                  <option value="protein">Protein</option>
                  <option value="tissue">Tissue</option>
                  <option value="seed">Seed</option>
                  <option value="leaf">Leaf</option>
                  <option value="root">Root</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Location</label>
                <input type="text" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setShowCreate(false)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
                <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selectedSample && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Sample Details</h2>
            {editingId === selectedSample.id ? (
              <form onSubmit={handleUpdate} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Name</label>
                  <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Type</label>
                  <select value={editForm.sample_type} onChange={(e) => setEditForm({ ...editForm, sample_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                    <option value="DNA">DNA</option>
                    <option value="RNA">RNA</option>
                    <option value="protein">Protein</option>
                    <option value="tissue">Tissue</option>
                    <option value="seed">Seed</option>
                    <option value="leaf">Leaf</option>
                    <option value="root">Root</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium">Status</label>
                  <select value={editForm.status} onChange={(e) => setEditForm({ ...editForm, status: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                    <option value="active">Active</option>
                    <option value="consumed">Consumed</option>
                    <option value="discarded">Discarded</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium">Location</label>
                  <input type="text" value={editForm.location} onChange={(e) => setEditForm({ ...editForm, location: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
                </div>
                <div className="flex gap-2 justify-end">
                  <button type="button" onClick={() => setEditingId(null)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
                  <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Save</button>
                </div>
              </form>
            ) : (
              <>
                <div className="space-y-3">
                  <div><span className="font-medium">Code:</span> {selectedSample.sample_code}</div>
                  <div><span className="font-medium">Name:</span> {selectedSample.name}</div>
                  <div><span className="font-medium">Type:</span> {selectedSample.sample_type}</div>
                  <div><span className="font-medium">Status:</span> {selectedSample.status}</div>
                  <div><span className="font-medium">Location:</span> {selectedSample.location || "-"}</div>
                  <div><span className="font-medium">Created:</span> {new Date(selectedSample.created_at).toLocaleString()}</div>
                </div>
                <div className="flex gap-2 justify-end mt-6">
                  <button onClick={() => startEdit(selectedSample)} className="rounded-md border border-blue-300 px-4 py-2 text-blue-600 hover:bg-blue-50">Edit</button>
                  <button onClick={() => setSelectedSample(null)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Close</button>
                  <button onClick={() => handleDeleteSample(selectedSample.id)} className="rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700">Delete</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" /></div>
      ) : tab === "samples" ? (
        samples.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">No samples found.</div>
        ) : (
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Code</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Location</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {samples.map((s) => (
                  <tr key={s.id} className="border-t hover:bg-muted/20 cursor-pointer" onClick={() => setSelectedSample(s)}>
                    <td className="px-4 py-3 text-sm font-mono">{s.sample_code}</td>
                    <td className="px-4 py-3 text-sm">{s.name}</td>
                    <td className="px-4 py-3 text-sm">{s.sample_type}</td>
                    <td className="px-4 py-3"><span className={`rounded-full px-2 py-1 text-xs font-medium ${s.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>{s.status}</span></td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">{s.location || "-"}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={(e) => { e.stopPropagation(); startEdit(s); setSelectedSample(s); }} className="text-xs text-blue-600 hover:underline">Edit</button>
                        <button onClick={(e) => { e.stopPropagation(); handleDeleteSample(s.id); }} className="text-xs text-red-600 hover:underline">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : (
        equipment.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">No equipment found.</div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {equipment.map((eq) => (
              <div key={eq.id} className="rounded-lg border p-6 hover:shadow-md transition-shadow">
                <h3 className="font-semibold">{eq.name}</h3>
                <p className="text-sm text-muted-foreground">{eq.equipment_code}</p>
                {eq.category && <p className="text-xs text-muted-foreground mt-1">{eq.category}</p>}
                <span className={`mt-2 inline-block rounded-full px-2 py-1 text-xs font-medium ${eq.status === "available" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>{eq.status}</span>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}
