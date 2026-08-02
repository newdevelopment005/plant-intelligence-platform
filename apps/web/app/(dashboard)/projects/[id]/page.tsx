"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";

interface Member {
  id: string;
  user_id: string;
  role: string;
  joined_at: string;
}

interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  owner_id: string;
  start_date: string | null;
  end_date: string | null;
  tags: string[] | null;
  metadata: Record<string, unknown> | null;
  members: Member[];
  member_count: number;
  created_at: string;
  updated_at: string;
}

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "members" | "settings">("overview");

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    setLoading(true);
    try {
      const data = await apiClient.request(`/projects/${projectId}`);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this project? This action cannot be undone.")) {
      return;
    }
    try {
      await apiClient.request(`/projects/${projectId}`, { method: "DELETE" });
      router.push("/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete project");
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Not set";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || "Project not found"}</p>
        <Link href="/projects" className="text-green-600 hover:underline">
          Back to projects
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <Link href="/projects" className="text-sm text-muted-foreground hover:text-foreground">
            ← Back to projects
          </Link>
          <h1 className="text-3xl font-bold mt-2">{project.name}</h1>
          <div className="flex items-center gap-3 mt-2">
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
            <span className="text-sm text-muted-foreground">
              {project.member_count} members
            </span>
          </div>
        </div>
      </div>

      <div className="flex gap-1 border-b">
        {(["overview", "members", "settings"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              activeTab === tab
                ? "border-b-2 border-green-600 text-green-600"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-2">Description</h3>
              <p className="text-sm text-muted-foreground">
                {project.description || "No description provided"}
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-2">Details</h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Start Date</dt>
                  <dd>{formatDate(project.start_date)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">End Date</dt>
                  <dd>{formatDate(project.end_date)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Created</dt>
                  <dd>{formatDate(project.created_at)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Last Updated</dt>
                  <dd>{formatDate(project.updated_at)}</dd>
                </div>
              </dl>
            </div>
          </div>
          <div className="space-y-4">
            {project.tags && project.tags.length > 0 && (
              <div className="rounded-lg border p-4">
                <h3 className="font-medium mb-2">Tags</h3>
                <div className="flex gap-2 flex-wrap">
                  {project.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded bg-gray-100 px-2 py-1 text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-2">Quick Links</h3>
              <div className="space-y-2">
                <Link
                  href={`/projects/${projectId}/germplasm`}
                  className="block text-sm text-green-600 hover:underline"
                >
                  → Germplasm Repository
                </Link>
                <Link
                  href={`/projects/${projectId}/phenotyping`}
                  className="block text-sm text-green-600 hover:underline"
                >
                  → Phenotyping Data
                </Link>
                <Link
                  href={`/projects/${projectId}/genomics`}
                  className="block text-sm text-green-600 hover:underline"
                >
                  → Genomics Data
                </Link>
                <Link
                  href={`/projects/${projectId}/literature`}
                  className="block text-sm text-green-600 hover:underline"
                >
                  → Literature
                </Link>
                <Link
                  href={`/projects/${projectId}/notebook`}
                  className="block text-sm text-green-600 hover:underline"
                >
                  → Lab Notebook
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "members" && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Team Members ({project.members.length})</h3>
          </div>
          <div className="rounded-lg border">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-4 py-3 text-left text-sm font-medium">User ID</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Role</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Joined</th>
                </tr>
              </thead>
              <tbody>
                {project.members.map((member) => (
                  <tr key={member.id} className="border-b last:border-0">
                    <td className="px-4 py-3 text-sm">{member.user_id}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="capitalize">{member.role}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {formatDate(member.joined_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "settings" && (
        <div className="max-w-md space-y-4">
          <h3 className="font-medium">Project Settings</h3>
          <div className="rounded-lg border p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select className="w-full rounded-md border px-3 py-2">
                <option value="active" selected={project.status === "active"}>
                  Active
                </option>
                <option value="archived" selected={project.status === "archived"}>
                  Archived
                </option>
              </select>
            </div>
            <button className="w-full rounded-md border border-red-300 px-4 py-2 text-red-600 hover:bg-red-50">
              Delete Project
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
