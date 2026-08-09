"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Sequence {
  id: string;
  name: string;
  description: string | null;
  sequence_type: string;
  organism: string | null;
  chromosome: string | null;
  length: number | null;
  created_at: string;
}

export default function GenomicsPage() {
  const [sequences, setSequences] = useState<Sequence[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", sequence_type: "genome", organism: "", chromosome: "" });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", description: "", sequence_type: "genome", organism: "", chromosome: "" });

  useEffect(() => { loadSequences(); }, []);

  const loadSequences = async (q?: string) => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (q) params.search = q;
      const data = await apiClient.listSequences(params);
      setSequences(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createSequence(form);
      setShowCreate(false);
      setForm({ name: "", description: "", sequence_type: "genome", organism: "", chromosome: "" });
      loadSequences();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const startEdit = (seq: Sequence) => {
    setEditingId(seq.id);
    setEditForm({
      name: seq.name,
      description: seq.description || "",
      sequence_type: seq.sequence_type,
      organism: seq.organism || "",
      chromosome: seq.chromosome || "",
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateSequence(editingId, editForm);
      setEditingId(null);
      loadSequences();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this sequence?")) return;
    try {
      await apiClient.deleteSequence(id);
      loadSequences();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Genomics</h1>
          <p className="text-muted-foreground">{total} sequences</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Sequence</button>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); loadSequences(search || undefined); }} className="flex gap-2">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search sequences..." className="flex-1 rounded-md border px-3 py-2" />
        <button type="submit" className="rounded-md border px-4 py-2 hover:bg-gray-50">Search</button>
      </form>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Create Sequence</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Name *</label>
                <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Type</label>
                <select value={form.sequence_type} onChange={(e) => setForm({ ...form, sequence_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="genome">Genome</option>
                  <option value="exome">Exome</option>
                  <option value="transcriptome">Transcriptome</option>
                  <option value="amplicon">Amplicon</option>
                  <option value="metagenome">Metagenome</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Organism</label>
                <input type="text" value={form.organism} onChange={(e) => setForm({ ...form, organism: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Chromosome</label>
                <input type="text" value={form.chromosome} onChange={(e) => setForm({ ...form, chromosome: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
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
      ) : sequences.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No sequences found.</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sequences.map((seq) => (
            <div key={seq.id} className="rounded-lg border p-6 hover:shadow-md transition-shadow">
              {editingId === seq.id ? (
                <form onSubmit={handleUpdate} className="space-y-3">
                  <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="w-full rounded border px-2 py-1 text-sm font-semibold" placeholder="Name" />
                  <select value={editForm.sequence_type} onChange={(e) => setEditForm({ ...editForm, sequence_type: e.target.value })} className="w-full rounded border px-2 py-1 text-sm">
                    <option value="genome">Genome</option>
                    <option value="exome">Exome</option>
                    <option value="transcriptome">Transcriptome</option>
                    <option value="amplicon">Amplicon</option>
                    <option value="metagenome">Metagenome</option>
                  </select>
                  <input type="text" value={editForm.organism} onChange={(e) => setEditForm({ ...editForm, organism: e.target.value })} className="w-full rounded border px-2 py-1 text-sm" placeholder="Organism" />
                  <input type="text" value={editForm.chromosome} onChange={(e) => setEditForm({ ...editForm, chromosome: e.target.value })} className="w-full rounded border px-2 py-1 text-sm" placeholder="Chromosome" />
                  <textarea value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} className="w-full rounded border px-2 py-1 text-sm" rows={2} placeholder="Description" />
                  <div className="flex gap-2">
                    <button type="submit" className="text-xs text-green-600 hover:underline">Save</button>
                    <button type="button" onClick={() => setEditingId(null)} className="text-xs text-muted-foreground hover:underline">Cancel</button>
                  </div>
                </form>
              ) : (
                <>
                  <h3 className="font-semibold text-lg mb-1">{seq.name}</h3>
                  <p className="text-sm text-muted-foreground">{seq.sequence_type}</p>
                  {seq.organism && <p className="text-xs text-muted-foreground mt-1">{seq.organism}</p>}
                  {seq.chromosome && <p className="text-xs text-muted-foreground">Chr: {seq.chromosome}</p>}
                  {seq.length && <p className="text-xs text-muted-foreground">Length: {seq.length.toLocaleString()} bp</p>}
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => startEdit(seq)} className="text-xs text-blue-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(seq.id)} className="text-xs text-red-600 hover:underline">Delete</button>
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
