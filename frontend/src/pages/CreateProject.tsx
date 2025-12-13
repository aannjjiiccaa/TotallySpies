import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, X } from "lucide-react";
import TopNav from "@/components/TopNav";

const CreateProject = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // For now, just navigate to dashboard with mock success
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-background">
      <TopNav onBack={() => navigate("/dashboard")} backLabel="Projects" />

      {/* Main content */}
      <main className="mx-auto max-w-[1600px] px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">Create Project</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Add your repositories to generate a system map.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Project name</Label>
            <Input
              id="name"
              placeholder="E-Commerce Platform"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              placeholder="A brief description of what this system does..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

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

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate("/dashboard")}
            >
              Cancel
            </Button>
            <Button type="submit">Create project</Button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default CreateProject;
