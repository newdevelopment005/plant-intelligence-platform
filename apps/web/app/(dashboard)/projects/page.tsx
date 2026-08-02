"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";

interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  owner_id: string;
  member_count: number;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newProject, setNewProject] = useState({
    name: "",
    description: "",
    tags: "",
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async (searchQuery?: string) => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.set("search", searchQuery);
      const data = await apiClient.request(`/projects?${params.toString()}`);
      setProjects(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadProjects(search || undefined);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const tags = newProject.tags
        ? newProject.tags.split(",").map((t) => t.trim())
        : undefined;
      await apiClient.request("/projects", {
        method: "POST",
        body: JSON.stringify({
          name: newProject.name,
          description: newProject.description || undefined,
          tags,
        }),
      });
      setShowCreate(false);
      setNewProject({ name: "", description: "", tags: "" });
      loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">{total} projects</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
        >
          New Project
        </button>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search projects..."
          className="flex-1 rounded-md border px-3 py-2"
        />
        <button
          type="submit"
          className="rounded-md border px-4 py-2 hover:bg-gray-50"
        >
          Search
        </button>
      </form>

      {error && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Create Project</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Name *</label>
                <input
                  type="text"
                  required
                  value={newProject.name}
                  onChange={(e) =>
                    setNewProject({ ...newProject, name: e.target.value })
                  }
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                  placeholder="Drought Resistance Study"
                />
              </div>
              <div>
                <label className="block text-sm font-medium">Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) =>
                    setNewProject({
                      ...newProject,
                      description: e.target.value,
                    })
                  }
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  value={newProject.tags}
                  onChange={(e) =>
                    setNewProject({ ...newProject, tags: e.target.value })
                  }
                  className="mt-1 block w-full rounded-md border px-3 py-2"
                  placeholder="drought, wheat, genetics"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="rounded-md border px-4 py-2 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                >
                  Create
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
      ) : projects.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No projects found. Create your first project to get started.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="block rounded-lg border p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-lg">{project.name}</h3>
                <span
                  className={`rounded-full px-2 py-1 text-xs font-medium ${
                    project.status === "active"
                      ? "bg-green-100 text-green-800"
                      : project.status === "archived"
                      ? "bg-gray-100 text-gray-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {project.status}
                </span>
              </div>
              {project.description && (
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                  {project.description}
                </p>
              )}
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span>{project.member_count} members</span>
                <span>{formatDate(project.created_at)}</span>
              </div>
              {project.tags && project.tags.length > 0 && (
                <div className="flex gap-1 mt-3 flex-wrap">
                  {project.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="rounded bg-gray-100 px-2 py-0.5 text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                  {project.tags.length > 3 && (
                    <span className="text-xs text-muted-foreground">
                      +{project.tags.length - 3}
                    </span>
                  )}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
