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
  description?: string | null;
  status: string;
  category: string | null;
  location?: string | null;
  manufacturer?: string | null;
  model_number?: string | null;
  serial_number?: string | null;
  created_at?: string;
}

const SAMPLE_TYPES = ["DNA", "RNA", "Protein", "Tissue", "Seed", "Leaf", "Root"];

function SampleTypeField({ value, onChange, editing }: { value: string; onChange: (v: string) => void; editing?: boolean }) {
  const preset = SAMPLE_TYPES.find((t) => t.toLowerCase() === value.toLowerCase());
  const [custom, setCustom] = useState(preset ? "" : value);
  const useCustom = !preset;

  return (
    <div>
      <label className="block text-sm font-medium">Type</label>
      <select
        value={useCustom ? "__custom__" : preset || "DNA"}
        onChange={(e) => {
          if (e.target.value === "__custom__") {
            onChange(custom || "Other");
            setCustom(custom || "Other");
          } else {
            onChange(e.target.value);
          }
        }}
        className="mt-1 block w-full rounded-md border px-3 py-2"
      >
        {SAMPLE_TYPES.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
        <option value="__custom__">{useCustom ? `Custom (${value})` : "Other / Custom"}</option>
      </select>
      {useCustom && (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="mt-2 block w-full rounded-md border px-3 py-2"
          placeholder="Free-text sample type"
        />
      )}
    </div>
  );
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

  const [showEquipmentForm, setShowEquipmentForm] = useState(false);
  const [equipmentForm, setEquipmentForm] = useState({ name: "", equipment_code: "", category: "", status: "available", location: "", manufacturer: "", model_number: "", serial_number: "", description: "" });
  const [editingEquipmentId, setEditingEquipmentId] = useState<string | null>(null);
  const [equipmentEditForm, setEquipmentEditForm] = useState({ name: "", equipment_code: "", category: "", status: "available", location: "", manufacturer: "", model_number: "", serial_number: "", description: "" });

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

  const emptyEquipmentForm = {
    name: "",
    equipment_code: "",
    category: "",
    status: "available",
    location: "",
    manufacturer: "",
    model_number: "",
    serial_number: "",
    description: "",
  };

  const handleCreateEquipment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createEquipment({
        ...equipmentForm,
        description: equipmentForm.description || undefined,
        category: equipmentForm.category || undefined,
        location: equipmentForm.location || undefined,
        manufacturer: equipmentForm.manufacturer || undefined,
        model_number: equipmentForm.model_number || undefined,
        serial_number: equipmentForm.serial_number || undefined,
      });
      setShowEquipmentForm(false);
      setEquipmentForm(emptyEquipmentForm);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const startEditEquipment = (eq: Equipment) => {
    setEditingEquipmentId(eq.id);
    setEquipmentEditForm({
      name: eq.name,
      equipment_code: eq.equipment_code,
      category: eq.category ?? "",
      status: eq.status,
      location: eq.location ?? "",
      manufacturer: eq.manufacturer ?? "",
      model_number: eq.model_number ?? "",
      serial_number: eq.serial_number ?? "",
      description: eq.description ?? "",
    });
  };

  const handleUpdateEquipment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingEquipmentId) return;
    try {
      await apiClient.updateEquipment(editingEquipmentId, {
        ...equipmentEditForm,
        description: equipmentEditForm.description || null,
        category: equipmentEditForm.category || null,
        location: equipmentEditForm.location || null,
        manufacturer: equipmentEditForm.manufacturer || null,
        model_number: equipmentEditForm.model_number || null,
        serial_number: equipmentEditForm.serial_number || null,
      });
      setEditingEquipmentId(null);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDeleteEquipment = async (id: string) => {
    if (!confirm("Are you sure you want to delete this equipment?")) return;
    try {
      await apiClient.deleteEquipment(id);
      setEditingEquipmentId(null);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  const equipmentFields: { key: "name" | "equipment_code" | "category" | "location" | "manufacturer" | "model_number" | "serial_number" | "description"; label: string; required?: boolean; full?: boolean }[] = [
    { key: "name", label: "Name", required: true },
    { key: "equipment_code", label: "Equipment Code", required: true },
    { key: "category", label: "Category" },
    { key: "location", label: "Location" },
    { key: "manufacturer", label: "Manufacturer" },
    { key: "model_number", label: "Model Number" },
    { key: "serial_number", label: "Serial Number" },
    { key: "description", label: "Description", full: true },
  ];

  const renderEquipmentInput = (key: (typeof equipmentFields)[number]["key"], op: "create" | "edit") => {
    const formVal = op === "create" ? equipmentForm : equipmentEditForm;
    const setFormVal = op === "create" ? setEquipmentForm : setEquipmentEditForm;
    const field = equipmentFields.find((f) => f.key === key)!;
    const common = {
      required: field.required,
      value: formVal[key],
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setFormVal({ ...formVal, [key]: e.target.value }),
      className: "mt-1 block w-full rounded-md border px-3 py-2",
    };
    return key === "description" ? (
      <textarea {...common} rows={2} />
    ) : (
      <input {...common} />
    );
  };

  const EquipmentFormModal = ({ create }: { create: boolean }) => {
    const formVal = create ? equipmentForm : equipmentEditForm;
    const setFormVal = create ? setEquipmentForm : setEquipmentEditForm;
    const onClose = () => (create ? setShowEquipmentForm(false) : setEditingEquipmentId(null));
    const onSubmit = create ? handleCreateEquipment : handleUpdateEquipment;
    const hasOtherFields = equipmentFields.some((f) => f.key !== "name" && f.key !== "equipment_code" && f.key !== "description");
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
          <h2 className="text-xl font-bold mb-4">{create ? "New Equipment" : "Edit Equipment"}</h2>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {["name", "equipment_code"].map((k) => (
                <div key={k}>{renderEquipmentInput(k as "name" | "equipment_code", create ? "create" : "edit")}</div>
              ))}
            </div>
            <div>
              <label className="block text-sm font-medium">Status</label>
              <select
                value={formVal.status}
                onChange={(e) => setFormVal({ ...formVal, status: e.target.value })}
                className="mt-1 block w-full rounded-md border px-3 py-2"
              >
                <option value="available">Available</option>
                <option value="in_use">In Use</option>
                <option value="maintenance">Maintenance</option>
                <option value="out_of_service">Out of Service</option>
              </select>
            </div>
            {hasOtherFields && (
              <div className="grid grid-cols-2 gap-4">
                {equipmentFields.filter((f) => f.key !== "name" && f.key !== "equipment_code").map((f) => (
                  <div key={f.key} className={f.full ? "col-span-2" : ""}>
                    <label className="block text-sm font-medium">{f.label}</label>
                    {renderEquipmentInput(f.key, create ? "create" : "edit")}
                  </div>
                ))}
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={onClose} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
              <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">{create ? "Create" : "Save"}</button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">LIMS</h1>
          <p className="text-muted-foreground">{total} samples</p>
        </div>
        {tab === "samples" ? (
          <button onClick={() => setShowCreate(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Sample</button>
        ) : (
          <button onClick={() => setShowEquipmentForm(true)} className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">New Equipment</button>
        )}
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
              <SampleTypeField value={form.sample_type} onChange={(v) => setForm({ ...form, sample_type: v })} />
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

      {showEquipmentForm && <EquipmentFormModal create />}

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
                <SampleTypeField editing value={editForm.sample_type} onChange={(v) => setEditForm({ ...editForm, sample_type: v })} />
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

      {editingEquipmentId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Edit Equipment</h2>
            <form onSubmit={handleUpdateEquipment} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {["name", "equipment_code"].map((k) => (
                  <div key={k}>
                    <label className="block text-sm font-medium">{equipmentFields.find((f) => f.key === k)?.label}{equipmentFields.find((f) => f.key === k)?.required ? " *" : ""}</label>
                    {renderEquipmentInput(k as "name" | "equipment_code", "edit")}
                  </div>
                ))}
              </div>
              <div>
                <label className="block text-sm font-medium">Status</label>
                <select
                  value={equipmentEditForm.status}
                  onChange={(e) => setEquipmentEditForm({ ...equipmentEditForm, status: e.target.value })}
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                >
                  <option value="available">Available</option>
                  <option value="in_use">In Use</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="out_of_service">Out of Service</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {equipmentFields.filter((f) => f.key !== "name" && f.key !== "equipment_code").map((f) => (
                  <div key={f.key} className={f.full ? "col-span-2" : ""}>
                    <label className="block text-sm font-medium">{f.label}</label>
                    {renderEquipmentInput(f.key, "edit")}
                  </div>
                ))}
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setEditingEquipmentId(null)} className="rounded-md border px-4 py-2 hover:bg-gray-50">Cancel</button>
                <button type="submit" className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700">Save</button>
              </div>
            </form>
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
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{eq.name}</h3>
                    <p className="text-sm text-muted-foreground">{eq.equipment_code}</p>
                  </div>
                  <div className="flex flex-col gap-1">
                    <button onClick={() => startEditEquipment(eq)} className="text-xs text-blue-600 hover:underline text-right">Edit</button>
                    <button onClick={() => handleDeleteEquipment(eq.id)} className="text-xs text-red-600 hover:underline text-right">Delete</button>
                  </div>
                </div>
                {eq.category && <p className="text-xs text-muted-foreground mt-1">{eq.category}</p>}
                {eq.location && <p className="text-xs text-muted-foreground mt-1">Location: {eq.location}</p>}
                {(eq.manufacturer || eq.model_number) && <p className="text-xs text-muted-foreground mt-1">{eq.manufacturer}{eq.manufacturer && eq.model_number ? " · " : ""}{eq.model_number}</p>}
                {eq.description && <p className="text-xs text-muted-foreground mt-1">{eq.description}</p>}
                <span className={`mt-2 inline-block rounded-full px-2 py-1 text-xs font-medium ${eq.status === "available" ? "bg-green-100 text-green-800" : eq.status === "in_use" ? "bg-blue-100 text-blue-800" : eq.status === "maintenance" ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800"}`}>{eq.status}</span>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}