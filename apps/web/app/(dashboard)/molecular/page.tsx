"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface MolExperiment {
  id: string;
  name: string;
  description: string | null;
  experiment_type: string;
  status: string;
  start_date: string | null;
  created_at: string;
}

export default function MolecularPage() {
  const [experiments, setExperiments] = useState<MolExperiment[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", experiment_type: "PCR" });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", description: "", experiment_type: "PCR" });

  useEffect(() => { loadExperiments(); }, []);

  const loadExperiments = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listMolecularExperiments();
      setExperiments(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createMolecularExperiment(form);
      setShowCreate(false);
      setForm({ name: "", description: "", experiment_type: "PCR" });
      loadExperiments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const startEdit = (exp: MolExperiment) => {
    setEditingId(exp.id);
    setEditForm({ name: exp.name, description: exp.description || "", experiment_type: exp.experiment_type });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateMolecularExperiment(editingId, editForm);
      setEditingId(null);
      loadExperiments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this experiment?")) return;
    try {
      await apiClient.deleteMolecularExperiment(id);
      loadExperiments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Molecular</h1>
          <p className="text-muted-foreground">{total} experiments</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Experiment</button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Create Molecular Experiment</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Name *</label>
                <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Type</label>
                <select value={form.experiment_type} onChange={(e) => setForm({ ...form, experiment_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="PCR">PCR</option>
                  <option value="qPCR">qPCR</option>
                  <option value="cloning">Cloning</option>
                  <option value="sequencing">Sequencing</option>
                  <option value="gene_expression">Gene Expression</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" rows={3} />
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setShowCreate(false)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
                <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" /></div>
      ) : experiments.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No experiments found.</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {experiments.map((exp) => (
            <div key={exp.id} className="rounded-lg border p-6 hover:shadow-md transition-shadow">
              {editingId === exp.id ? (
                <form onSubmit={handleUpdate} className="space-y-3">
                  <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Name" />
                  <select value={editForm.experiment_type} onChange={(e) => setEditForm({ ...editForm, experiment_type: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm">
                    <option value="PCR">PCR</option>
                    <option value="qPCR">qPCR</option>
                    <option value="cloning">Cloning</option>
                    <option value="sequencing">Sequencing</option>
                    <option value="gene_expression">Gene Expression</option>
                  </select>
                  <textarea value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" rows={2} placeholder="Description" />
                  <div className="flex gap-2">
                    <button type="submit" className="text-sm text-green-600 hover:underline">Save</button>
                    <button type="button" onClick={() => setEditingId(null)} className="text-sm text-muted-foreground hover:underline">Cancel</button>
                  </div>
                </form>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-lg">{exp.name}</h3>
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${exp.status === "completed" ? "bg-green-100 text-green-800" : exp.status === "in_progress" ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-800"}`}>{exp.status}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{exp.experiment_type}</p>
                  {exp.description && <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{exp.description}</p>}
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => startEdit(exp)} className="text-xs text-blue-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(exp.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
