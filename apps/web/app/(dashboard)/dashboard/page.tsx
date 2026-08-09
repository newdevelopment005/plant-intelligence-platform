"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  FolderKanban,
  Sprout,
  FlaskConical,
  BookOpen,
  Dna,
  MessageSquareText,
  ArrowRight,
  TrendingUp,
  Clock,
  Zap,
} from "lucide-react";

const stats = [
  { name: "Projects", icon: FolderKanban, color: "bg-blue-500/10 text-blue-600", href: "/projects", key: "projects" },
  { name: "Germplasm", icon: Sprout, color: "bg-emerald-500/10 text-emerald-600", href: "/germplasm", key: "germplasm" },
  { name: "Experiments", icon: FlaskConical, color: "bg-purple-500/10 text-purple-600", href: "/phenotyping", key: "experiments" },
  { name: "Papers", icon: BookOpen, color: "bg-amber-500/10 text-amber-600", href: "/literature", key: "papers" },
];

const quickActions = [
  { name: "AI Research Assistant", description: "Ask questions about plant science", icon: MessageSquareText, href: "/ai", color: "bg-primary/10 text-primary" },
  { name: "New Project", description: "Create a research project", icon: FolderKanban, href: "/projects", color: "bg-blue-500/10 text-blue-600" },
  { name: "Add Germplasm", description: "Register seed or tissue sample", icon: Sprout, href: "/germplasm", color: "bg-emerald-500/10 text-emerald-600" },
  { name: "Run Analysis", description: "Start a phenotyping experiment", icon: FlaskConical, href: "/phenotyping", color: "bg-purple-500/10 text-purple-600" },
  { name: "Search Literature", description: "Find relevant papers on PubMed", icon: BookOpen, href: "/literature", color: "bg-amber-500/10 text-amber-600" },
  { name: "Sequence Data", description: "Upload genomics data", icon: Dna, href: "/genomics", color: "bg-rose-500/10 text-rose-600" },
];

const recentActivity = [
  { action: "Project created", subject: "Wheat Drought Resistance Study", time: "2 hours ago", type: "project" },
  { action: "Germplasm added", subject: "Triticum aestivum - Line 234", time: "5 hours ago", type: "germplasm" },
  { action: "Paper summarized", subject: "CRISPR-mediated disease resistance in rice", time: "1 day ago", type: "literature" },
  { action: "Experiment started", subject: "Phenotyping trial #47 - Leaf Area", time: "2 days ago", type: "experiment" },
];

export default function DashboardPage() {
  const [counts, setCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    async function loadCounts() {
      const keys = ["projects", "germplasm", "experiments", "papers"] as const;
      const results: Record<string, number> = {};
      for (const key of keys) {
        try {
          const endpoints: Record<string, string> = {
            projects: "/projects",
            germplasm: "/germplasm/accessions",
            experiments: "/phenotyping/experiments",
            papers: "/literature/papers",
          };
          const data = await apiClient.request<{ total?: number; items?: any[] }>(endpoints[key]);
          results[key] = data?.total ?? data?.items?.length ?? 0;
        } catch {
          results[key] = 0;
        }
      }
      setCounts(results);
    }
    loadCounts();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
        <p className="text-muted-foreground">Here&apos;s an overview of your research platform.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Link key={stat.name} href={stat.href}>
            <Card className="transition-all hover:shadow-md hover:border-primary/20 cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.name}</p>
                    <p className="text-3xl font-bold">{counts[stat.key] ?? 0}</p>
                  </div>
                  <div className={`rounded-xl p-3 ${stat.color}`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick Actions + Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {quickActions.map((action) => (
                  <Link key={action.name} href={action.href}>
                    <div className="group flex items-start gap-3 rounded-lg border p-4 transition-all hover:bg-muted/50 hover:shadow-sm cursor-pointer">
                      <div className={`rounded-lg p-2 ${action.color}`}>
                        <action.icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium group-hover:text-primary transition-colors">{action.name}</p>
                        <p className="text-xs text-muted-foreground">{action.description}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity mt-1" />
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" />
                  <div>
                    <p className="text-sm font-medium">{item.action}</p>
                    <p className="text-xs text-muted-foreground truncate max-w-[200px]">{item.subject}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Assistant Banner */}
      <Card className="bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 border-primary/20">
        <CardContent className="flex items-center justify-between p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-xl bg-primary p-3">
              <MessageSquareText className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h3 className="font-semibold">AI Research Assistant</h3>
              <p className="text-sm text-muted-foreground">
                Powered by Gemma2:2b — Ask questions about plant genetics, design experiments, or analyze literature.
              </p>
            </div>
          </div>
          <Link href="/ai">
            <Button>
              Start Chat
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
