"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Entity {
  id: string;
  name: string;
  entity_type: string;
  description: string | null;
  source_module: string | null;
  created_at: string;
}

export default function KnowledgeGraphPage() {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", entity_type: "gene", description: "" });

  useEffect(() => { loadEntities(); }, []);

  const loadEntities = async (q?: string) => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (q) params.search = q;
      const data = await apiClient.listKnowledgeEntities(params);
      setEntities(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createKnowledgeEntity(form);
      setShowCreate(false);
      setForm({ name: "", entity_type: "gene", description: "" });
      loadEntities();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Knowledge Graph</h1>
          <p className="text-muted-foreground">{total} entities</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Add Entity</button>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); loadEntities(search || undefined); }} className="flex gap-2">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search entities..." className="flex-1 rounded-md border px-3 py-2" />
        <button type="submit" className="rounded-md border px-4 py-2 hover:bg-gray-50">Search</button>
      </form>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Add Entity</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Name *</label>
                <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Type</label>
                <select value={form.entity_type} onChange={(e) => setForm({ ...form, entity_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="gene">Gene</option>
                  <option value="protein">Protein</option>
                  <option value="pathway">Pathway</option>
                  <option value="disease">Disease</option>
                  <option value="species">Species</option>
                  <option value="compound">Compound</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" rows={3} />
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
      ) : entities.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No entities found.</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {entities.map((entity) => (
            <div key={entity.id} className="rounded-lg border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-lg">{entity.name}</h3>
                <span className="rounded-full bg-purple-100 px-2 py-1 text-xs font-medium text-purple-800">{entity.entity_type}</span>
              </div>
              {entity.description && <p className="text-sm text-muted-foreground line-clamp-2">{entity.description}</p>}
              {entity.source_module && <p className="text-xs text-muted-foreground mt-2">Source: {entity.source_module}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
