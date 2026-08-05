"use client";

import { useEffect, useState, useRef } from "react";
import { apiClient } from "@/lib/api-client";

interface PlantImage {
  id: string;
  name: string;
  file_url: string;
  thumbnail_url: string | null;
  image_type: string;
  species: string | null;
  width: number | null;
  height: number | null;
  created_at: string;
}

export default function ImagesPage() {
  const [images, setImages] = useState<PlantImage[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadImages(); }, []);

  const loadImages = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listImages();
      setImages(data?.items ?? []);
      setTotal(data?.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally { setLoading(false); }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", file.name);
      await apiClient.uploadImage(formData);
      loadImages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Images</h1>
          <p className="text-muted-foreground">{total} images</p>
        </div>
        <div>
          <input ref={fileInputRef} type="file" accept="image/*" onChange={handleUpload} className="hidden" id="image-upload" />
          <label htmlFor="image-upload" className={`inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700 cursor-pointer ${uploading ? "opacity-50" : ""}`}>
            {uploading ? "Uploading..." : "Upload Image"}
          </label>
        </div>
      </div>

      {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {loading ? (
        <div className="flex justify-center py-12"><div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" /></div>
      ) : images.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No images uploaded yet.</div>
      ) : (
        <div className="grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {images.map((img) => (
            <div key={img.id} className="rounded-lg border overflow-hidden hover:shadow-md transition-shadow">
              <div className="aspect-square bg-muted flex items-center justify-center">
                {img.thumbnail_url || img.file_url ? (
                  <img src={img.thumbnail_url || img.file_url} alt={img.name} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-muted-foreground text-sm">No preview</span>
                )}
              </div>
              <div className="p-3">
                <p className="text-sm font-medium truncate">{img.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800">{img.image_type}</span>
                  {img.species && <span className="text-xs text-muted-foreground">{img.species}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
