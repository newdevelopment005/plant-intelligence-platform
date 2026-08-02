"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface NotebookEntry {
  id: string;
  title: string;
  content: string;
  entry_type: string;
  tags: string[] | null;
  is_locked: boolean;
  created_at: string;
}

export default function NotebookPage() {
  const [entries, setEntries] = useState<NotebookEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: "", content: "", entry_type: "note", tags: "" });

  useEffect(() => { loadEntries(); }, []);

  const loadEntries = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listNotebookEntries();
      setEntries(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createNotebookEntry({
        title: form.title,
        content: form.content,
        entry_type: form.entry_type,
        tags: form.tags ? form.tags.split(",").map((t) => t.trim()) : undefined,
      });
      setShowCreate(false);
      setForm({ title: "", content: "", entry_type: "note", tags: "" });
      loadEntries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notebook</h1>
          <p className="text-muted-foreground">{total} entries</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Entry</button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">New Notebook Entry</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Title *</label>
                <input type="text" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Type</label>
                <select value={form.entry_type} onChange={(e) => setForm({ ...form, entry_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="note">Note</option>
                  <option value="protocol">Protocol</option>
                  <option value="observation">Observation</option>
                  <option value="analysis">Analysis</option>
                  <option value="result">Result</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Content *</label>
                <textarea required value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2 font-mono text-sm" rows={10} />
              </div>
              <div>
                <label className="block text-sm font-medium">Tags (comma separated)</label>
                <input type="text" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
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
      ) : entries.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No entries yet. Start documenting your research.</div>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => (
            <div key={entry.id} className="rounded-lg border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-lg">{entry.title}</h3>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800">{entry.entry_type}</span>
                  {entry.is_locked && <span className="text-xs text-muted-foreground">Locked</span>}
                </div>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-3 font-mono">{entry.content}</p>
              {entry.tags && entry.tags.length > 0 && (
                <div className="flex gap-1 mt-3 flex-wrap">
                  {entry.tags.map((tag) => (
                    <span key={tag} className="rounded bg-gray-100 px-2 py-0.5 text-xs">{tag}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
