import { useParams, useNavigate } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Users } from "lucide-react";
import { mockProjects } from "@/data/mockData";
import OverviewTab from "@/components/project/OverviewTab";
import ArchitectureTab from "@/components/project/ArchitectureTab";
import RepositoriesTab from "@/components/project/RepositoriesTab";
import FlowsTab from "@/components/project/FlowsTab";
import OnboardingTab from "@/components/project/OnboardingTab";

const Project = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const project = mockProjects.find((p) => p.id === id);

  if (!project) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Project not found</h1>
          <Button
            variant="link"
            onClick={() => navigate("/dashboard")}
            className="mt-4"
          >
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-14 max-w-5xl items-center px-6">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Projects
          </button>
        </div>
      </header>

      {/* Project Header */}
      <div className="border-b border-border">
        <div className="mx-auto max-w-5xl px-6 py-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">{project.name}</h1>
              <p className="mt-1 text-muted-foreground">{project.description}</p>
              
              <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  {project.repositories.length} repositories
                </span>
                <span>•</span>
                <span>Updated {project.lastUpdated}</span>
              </div>

              <div className="mt-4 flex flex-wrap gap-1.5">
                {project.techStack.map((tech) => (
                  <span
                    key={tech}
                    className="inline-flex items-center rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>

            <Button variant="outline" size="sm">
              <Users className="h-4 w-4" />
              Invite
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mx-auto max-w-5xl px-6 py-6">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="h-auto w-full justify-start gap-1 rounded-none border-b border-border bg-transparent p-0">
            {["Overview", "Architecture", "Repositories", "Flows", "Onboarding"].map((tab) => (
              <TabsTrigger
                key={tab}
                value={tab.toLowerCase()}
                className="relative rounded-none border-b-2 border-transparent bg-transparent px-4 pb-3 pt-2 font-medium text-muted-foreground hover:text-foreground data-[state=active]:border-primary data-[state=active]:text-foreground data-[state=active]:shadow-none"
              >
                {tab}
              </TabsTrigger>
            ))}
          </TabsList>

          <div className="mt-6">
            <TabsContent value="overview" className="mt-0">
              <OverviewTab project={project} />
            </TabsContent>
            <TabsContent value="architecture" className="mt-0">
              <ArchitectureTab project={project} />
            </TabsContent>
            <TabsContent value="repositories" className="mt-0">
              <RepositoriesTab project={project} />
            </TabsContent>
            <TabsContent value="flows" className="mt-0">
              <FlowsTab project={project} />
            </TabsContent>
            <TabsContent value="onboarding" className="mt-0">
              <OnboardingTab project={project} />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
};

export default Project;
