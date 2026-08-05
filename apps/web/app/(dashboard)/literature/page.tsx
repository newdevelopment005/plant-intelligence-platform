"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Paper {
  id: string;
  title: string;
  authors: string[] | null;
  journal: string | null;
  year: number | null;
  doi: string | null;
  paper_type: string;
  created_at: string;
}

export default function LiteraturePage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: "", authors: "", journal: "", doi: "", year: "", abstract: "" });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ title: "", authors: "", journal: "", doi: "", year: "", abstract: "" });

  useEffect(() => { loadPapers(); }, []);

  const loadPapers = async (q?: string) => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (q) params.search = q;
      const data = await apiClient.listPapers(params);
      setPapers(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createPaper({
        title: form.title,
        authors: form.authors ? form.authors.split(",").map((a) => a.trim()) : undefined,
        journal: form.journal || undefined,
        doi: form.doi || undefined,
        year: form.year ? parseInt(form.year) : undefined,
        abstract: form.abstract || undefined,
      });
      setShowCreate(false);
      setForm({ title: "", authors: "", journal: "", doi: "", year: "", abstract: "" });
      loadPapers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const startEdit = (paper: Paper) => {
    setEditingId(paper.id);
    setEditForm({
      title: paper.title,
      authors: paper.authors?.join(", ") || "",
      journal: paper.journal || "",
      doi: paper.doi || "",
      year: paper.year?.toString() || "",
      abstract: "",
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updatePaper(editingId, {
        title: editForm.title,
        authors: editForm.authors ? editForm.authors.split(",").map((a) => a.trim()) : undefined,
        journal: editForm.journal || undefined,
        doi: editForm.doi || undefined,
        year: editForm.year ? parseInt(editForm.year) : undefined,
        abstract: editForm.abstract || undefined,
      });
      setEditingId(null);
      loadPapers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this paper?")) return;
    try {
      await apiClient.deletePaper(id);
      loadPapers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Literature</h1>
          <p className="text-muted-foreground">{total} papers</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Add Paper</button>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); loadPapers(search || undefined); }} className="flex gap-2">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search papers..." className="flex-1 rounded-md border px-3 py-2" />
        <button type="submit" className="rounded-md border px-4 py-2 hover:bg-gray-50">Search</button>
      </form>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Add Paper</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Title *</label>
                <input type="text" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Authors (comma separated)</label>
                  <input type="text" value={form.authors} onChange={(e) => setForm({ ...form, authors: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Journal</label>
                  <input type="text" value={form.journal} onChange={(e) => setForm({ ...form, journal: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">DOI</label>
                  <input type="text" value={form.doi} onChange={(e) => setForm({ ...form, doi: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Year</label>
                  <input type="number" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium">Abstract</label>
                <textarea value={form.abstract} onChange={(e) => setForm({ ...form, abstract: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" rows={4} />
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setShowCreate(false)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
                <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" /></div>
      ) : papers.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No papers found.</div>
      ) : (
        <div className="space-y-4">
          {papers.map((paper) => (
            <div key={paper.id} className="rounded-lg border p-6 hover:shadow-md transition-shadow">
              {editingId === paper.id ? (
                <form onSubmit={handleUpdate} className="space-y-3">
                  <input type="text" value={editForm.title} onChange={(e) => setEditForm({ ...editForm, title: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Title" />
                  <div className="grid grid-cols-2 gap-3">
                    <input type="text" value={editForm.authors} onChange={(e) => setEditForm({ ...editForm, authors: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Authors (comma separated)" />
                    <input type="text" value={editForm.journal} onChange={(e) => setEditForm({ ...editForm, journal: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Journal" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <input type="text" value={editForm.doi} onChange={(e) => setEditForm({ ...editForm, doi: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="DOI" />
                    <input type="number" value={editForm.year} onChange={(e) => setEditForm({ ...editForm, year: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" placeholder="Year" />
                  </div>
                  <textarea value={editForm.abstract} onChange={(e) => setEditForm({ ...editForm, abstract: e.target.value })} className="block w-full rounded-md border px-3 py-2 text-sm" rows={2} placeholder="Abstract" />
                  <div className="flex gap-2">
                    <button type="submit" className="text-sm text-green-600 hover:underline">Save</button>
                    <button type="button" onClick={() => setEditingId(null)} className="text-sm text-muted-foreground hover:underline">Cancel</button>
                  </div>
                </form>
              ) : (
                <>
                  <h3 className="font-semibold text-lg mb-1">{paper.title}</h3>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    {paper.authors && <span>{paper.authors.slice(0, 3).join(", ")}{paper.authors.length > 3 ? " et al." : ""}</span>}
                    {paper.journal && <span>{paper.journal}</span>}
                    {paper.year && <span>({paper.year})</span>}
                  </div>
                  {paper.doi && <p className="text-xs text-blue-600 mt-1">DOI: {paper.doi}</p>}
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => startEdit(paper)} className="text-xs text-blue-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(paper.id)} className="text-xs text-red-600 hover:underline">Delete</button>
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
