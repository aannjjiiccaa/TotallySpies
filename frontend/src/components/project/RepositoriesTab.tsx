import { Project } from "@/types/project";

interface RepositoriesTabProps {
  project: Project;
}

const typeColors: Record<string, string> = {
  backend: "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  frontend: "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300",
  infra: "bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300",
  library: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
};

const RepositoriesTab = ({ project }: RepositoriesTabProps) => {
  // Prefer repository names extracted from the graph nodes when available
  const graphNodes: any[] = (project as any).graph?.nodes || [];
  const repoNames = Array.from(new Set(graphNodes.map((n) => n.repo).filter(Boolean)));

  return (
    <div className="animate-fade-in">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {repoNames.length > 0 ? `${repoNames.length} repositories in this project` : `${project.repositories.length} repositories in this project`}
        </p>
      </div>

      <div className="space-y-3">
        {repoNames.length > 0 ? (
          repoNames.map((name) => (
            <div
              key={name}
              className="rounded-lg border border-border bg-card p-4 hover:bg-surface-hover transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-sm font-medium">{name}</span>
                    <span className="rounded px-2 py-0.5 text-xs font-medium bg-secondary text-secondary-foreground">python</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Repository discovered in the analyzed graph.</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          project.repositories.map((repo) => (
            <div
              key={repo.id}
              className="rounded-lg border border-border bg-card p-4 hover:bg-surface-hover transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <a
                      href={repo.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-mono text-sm font-medium hover:text-primary transition-colors"
                    >
                      {repo.name}
                    </a>
                    <span className={`rounded px-2 py-0.5 text-xs font-medium ${typeColors[repo.type]}`}>
                      {repo.type}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {repo.responsibility}
                  </p>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-xs">
                {repo.dependsOn.length > 0 && (
                  <div>
                    <span className="text-muted-foreground">Depends on: </span>
                    <span className="font-mono">
                      {repo.dependsOn.join(", ")}
                    </span>
                  </div>
                )}
                {repo.usedBy.length > 0 && (
                  <div>
                    <span className="text-muted-foreground">Used by: </span>
                    <span className="font-mono">
                      {repo.usedBy.join(", ")}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RepositoriesTab;
