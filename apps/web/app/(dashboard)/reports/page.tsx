"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Report {
  id: string;
  name: string;
  report_type: string;
  status: string;
  format: string;
  created_at: string;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", report_type: "project_summary", format: "pdf" });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", report_type: "project_summary", format: "pdf" });

  useEffect(() => { loadReports(); }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listReports();
      setReports(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createReport(form);
      setShowCreate(false);
      setForm({ name: "", report_type: "project_summary", format: "pdf" });
      loadReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const startEdit = (r: Report) => {
    setEditingId(r.id);
    setEditForm({ name: r.name, report_type: r.report_type, format: r.format });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    try {
      await apiClient.updateReport(editingId, editForm);
      setEditingId(null);
      loadReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDownload = async (id: string, name: string) => {
    try {
      const data = await apiClient.request(`/reports/${id}/download`);
      if (data.download_url) {
        const downloadUrl = data.download_url.startsWith("http") ? data.download_url : `/api/images${data.download_url}`;
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${name}.${data.format || "pdf"}`;
        a.click();
      } else {
        setError("Report not ready for download");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this report?")) return;
    try {
      await apiClient.request(`/reports/${id}`, { method: "DELETE" });
      loadReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">{total} reports</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Report</button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Create Report</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Name *</label>
                <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Type</label>
                <select value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="project_summary">Project Summary</option>
                  <option value="phenotyping">Phenotyping</option>
                  <option value="genotyping">Genotyping</option>
                  <option value="germplasm">Germplasm</option>
                  <option value="experiment">Experiment</option>
                  <option value="statistical">Statistical</option>
                  <option value="comparative">Comparative</option>
                  <option value="temporal">Temporal</option>
                  <option value="geospatial">Geospatial</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium">Format</label>
                <select value={form.format} onChange={(e) => setForm({ ...form, format: e.target.value })} className="mt-1 block w-full rounded-md border px-3 py-2">
                  <option value="pdf">PDF</option>
                  <option value="csv">CSV</option>
                  <option value="json">JSON</option>
                </select>
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
      ) : reports.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No reports yet.</div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Format</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id} className="border-t hover:bg-muted/20">
                  {editingId === r.id ? (
                    <td colSpan={5} className="px-4 py-3">
                      <form onSubmit={handleUpdate} className="flex items-center gap-3">
                        <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="flex-1 rounded border px-2 py-1 text-sm" placeholder="Name" />
                        <select value={editForm.report_type} onChange={(e) => setEditForm({ ...editForm, report_type: e.target.value })} className="rounded border px-2 py-1 text-sm">
                          <option value="project_summary">Project Summary</option>
                          <option value="phenotyping">Phenotyping</option>
                          <option value="genotyping">Genotyping</option>
                          <option value="germplasm">Germplasm</option>
                          <option value="experiment">Experiment</option>
                          <option value="statistical">Statistical</option>
                        </select>
                        <select value={editForm.format} onChange={(e) => setEditForm({ ...editForm, format: e.target.value })} className="rounded border px-2 py-1 text-sm">
                          <option value="pdf">PDF</option>
                          <option value="csv">CSV</option>
                          <option value="json">JSON</option>
                        </select>
                        <button type="submit" className="text-xs text-green-600 hover:underline">Save</button>
                        <button type="button" onClick={() => setEditingId(null)} className="text-xs text-muted-foreground hover:underline">Cancel</button>
                      </form>
                    </td>
                  ) : (
                    <>
                      <td className="px-4 py-3 text-sm font-medium">{r.name}</td>
                      <td className="px-4 py-3 text-sm">{r.report_type}</td>
                      <td className="px-4 py-3 text-sm uppercase">{r.format}</td>
                      <td className="px-4 py-3"><span className={`rounded-full px-2 py-1 text-xs font-medium ${r.status === "completed" ? "bg-green-100 text-green-800" : r.status === "generating" ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-800"}`}>{r.status}</span></td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button onClick={() => startEdit(r)} className="text-sm text-blue-600 hover:underline">Edit</button>
                          {r.status === "completed" && (
                            <button onClick={() => handleDownload(r.id, r.name)} className="text-sm text-green-600 hover:underline">Download</button>
                          )}
                          <button onClick={() => handleDelete(r.id)} className="text-sm text-red-600 hover:underline">Delete</button>
                        </div>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
