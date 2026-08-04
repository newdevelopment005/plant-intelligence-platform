import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Leaf, FlaskConical, Dna, BookOpen, Brain, ArrowRight } from "lucide-react";

const features = [
  { icon: Brain, title: "AI Research Assistant", desc: "Chat with a local AI trained on plant science. No API costs." },
  { icon: FlaskConical, title: "Phenotyping", desc: "Track field, greenhouse, and controlled environment experiments." },
  { icon: Dna, title: "Genomics", desc: "Manage genome, exome, and transcriptome sequencing data." },
  { icon: BookOpen, title: "Literature", desc: "Search PubMed, summarize papers, and extract findings." },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center px-6 py-24 text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent" />
        <div className="relative z-10 max-w-3xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-primary/5 px-4 py-1.5 text-sm text-primary">
            <Leaf className="h-4 w-4" />
            Powered by Local AI — Zero API Costs
          </div>
          <h1 className="mb-6 text-5xl font-bold tracking-tight sm:text-6xl">
            Plant Intelligence{" "}
            <span className="text-primary">Platform</span>
          </h1>
          <p className="mb-10 text-lg text-muted-foreground max-w-2xl mx-auto">
            Enterprise-grade AI-powered scientific research platform for plant science.
            Manage germplasm, run experiments, analyze genomics, and chat with a local LLM.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/login">
              <Button size="lg" className="gap-2">
                Sign In <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/register">
              <Button size="lg" variant="outline">
                Create Account
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-12 text-center text-3xl font-bold">Everything for Plant Research</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div key={f.title} className="rounded-xl border bg-card p-6 transition-all hover:shadow-md">
                <div className="mb-4 rounded-lg bg-primary/10 p-3 w-fit">
                  <f.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-2 font-semibold">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t px-6 py-8 text-center text-sm text-muted-foreground">
        <p>Plant Intelligence Platform — Open Source, Local AI, Zero Costs</p>
      </footer>
    </div>
  );
}
