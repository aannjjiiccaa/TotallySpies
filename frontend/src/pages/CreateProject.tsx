import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, X } from "lucide-react";
import TopNav from "@/components/TopNav";
import { useState } from "react";
import { getGraph } from "@/services/api.service";

const CreateProject = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  
  const [repoUrls, setRepoUrls] = useState<string[]>([""]);

  const addRepoField = () => {
    setRepoUrls([...repoUrls, ""]);
  };

  const removeRepoField = (index: number) => {
    if (repoUrls.length > 1) {
      setRepoUrls(repoUrls.filter((_, i) => i !== index));
    }
  };

  const updateRepoUrl = (index: number, value: string) => {
    const updated = [...repoUrls];
    updated[index] = value;
    setRepoUrls(updated);
  };

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const graphJson = await getGraph();

      const project = {
        id: "new",
        name: name || "New Project",
        repositories: repoUrls.filter(Boolean),
        lastUpdated: new Date().toLocaleDateString(),
        techStack: [],
        graph: graphJson,
      } as any;

      navigate(`/project/${project.id}`, { state: { project } });
    } catch (err: any) {
      setError(err?.message || "Failed to fetch graph");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <TopNav onBack={() => navigate("/dashboard")} backLabel="Projects" />

      {/* Main content */}
      <main className="mx-auto max-w-[1600px] px-8 py-12">
        <div className="max-w-[900px] mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold tracking-tight">Create Project</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Add your repositories to generate a system map.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 w-full mx-auto">
          <div className="space-y-2">
            <Label htmlFor="name">Project name</Label>
            <Input
              id="name"
              placeholder="Enter project name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* Description removed — not used in project creation */}

          <div className="space-y-3">
            <Label>Repository URLs</Label>
            <p className="text-xs text-muted-foreground">
              Add links to your GitHub, GitLab, or other git repositories.
            </p>

            <div className="space-y-2">
              {repoUrls.map((url, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    placeholder="https://github.com/org/repo"
                    value={url}
                    onChange={(e) => updateRepoUrl(index, e.target.value)}
                    className="font-mono text-sm"
                  />
                  {repoUrls.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeRepoField(index)}
                      className="shrink-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addRepoField}
              className="mt-2"
            >
              <Plus className="h-4 w-4" />
              Add repository
            </Button>
          </div>

          <div className="flex justify-start gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate("/dashboard")}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>{loading ? "Creating..." : "Create project"}</Button>
          </div>
          {error && <p className="text-sm text-destructive mt-2">{error}</p>}
        </form>
        </div>
      </main>
    </div>
  );
};

export default CreateProject;
