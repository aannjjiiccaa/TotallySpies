import { Project } from "@/types/project";

interface FlowsTabProps {
  project: Project;
}

const FlowsTab = ({ project }: FlowsTabProps) => {
  return (
    <div className="animate-fade-in space-y-6">
      <p className="text-sm text-muted-foreground">
        Cross-repository flows showing how data moves through the system.
      </p>

      {project.flows.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-12 text-center">
          <p className="text-sm text-muted-foreground">No flows documented yet.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {project.flows.map((flow) => (
            <div key={flow.id} className="rounded-lg border border-border bg-card">
              <div className="border-b border-border p-4">
                <h3 className="font-medium">{flow.name}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{flow.description}</p>
              </div>
              
              <div className="p-4">
                <div className="space-y-0">
                  {flow.steps.map((step, index) => (
                    <div key={step.step} className="flex gap-4">
                      {/* Step number and line */}
                      <div className="flex flex-col items-center">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-medium text-primary-foreground">
                          {step.step}
                        </div>
                        {index < flow.steps.length - 1 && (
                          <div className="w-px flex-1 bg-border my-1" />
                        )}
                      </div>
                      
                      {/* Step content */}
                      <div className="flex-1 pb-4">
                        <p className="text-sm">{step.action}</p>
                        <span className="mt-1 inline-block rounded bg-secondary px-2 py-0.5 font-mono text-xs text-secondary-foreground">
                          {step.service}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FlowsTab;
