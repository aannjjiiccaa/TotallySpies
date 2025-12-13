import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ProjectCard from "@/components/ProjectCard";
import { mockProjects } from "@/data/mockData";
import { Plus } from "lucide-react";
import TopNav from "@/components/TopNav";

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <TopNav />

      {/* Main content */}
      <main className="mx-auto max-w-[1600px] px-6 py-10">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Your codebases, mapped and documented.
            </p>
          </div>
          <Button onClick={() => navigate("/create-project")}>
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {mockProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>

        {mockProjects.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
              <svg className="h-6 w-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <h3 className="mt-4 font-medium">No projects yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">Create your first project to get started.</p>
            <Button className="mt-4" onClick={() => navigate("/create-project")}>
              <Plus className="h-4 w-4" />
              Create Project
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;