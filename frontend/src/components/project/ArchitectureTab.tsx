import { Project } from "@/types/project";
import ProjectGraphPlaceholder from "@/components/ui/graph-placeholder";

interface ArchitectureTabProps {
  project: Project;
}

const ArchitectureTab = ({ project }: ArchitectureTabProps) => {
  // derive unique repo names from graph nodes (fallback empty array)
  const graphNodes: any[] = (project as any).graph?.nodes || [];
  const repoNames = Array.from(new Set(graphNodes.map((n) => n.repo).filter(Boolean)));

  return (
    <div className="animate-fade-in space-y-8">
      {/* Repositories found in the graph */}
      {repoNames.length > 0 && (
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium">Repositories:</h3>
          <div className="flex flex-wrap gap-2">
            {repoNames.map((r) => (
              <span key={r} className="inline-flex items-center rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                {r}
              </span>
            ))}
          </div>
        </div>
      )}
      {/* System graph */}
      <section>
        <h2 className="text-lg font-medium mb-4">System Graph</h2>
        <ProjectGraphPlaceholder graphData={project.graph} />
      </section>

      {/* Core services */}
      <section>
        <h2 className="text-lg font-medium mb-3">Core Services</h2>
        <div className="space-y-4">
          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm font-medium">api-gateway</span>
              <span className="rounded bg-orange-soft px-2 py-0.5 text-xs text-primary font-medium">
                Entry Point
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Central routing layer. Handles authentication, rate limiting, and request
              forwarding to downstream services.
            </p>
          </div>

          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm font-medium">auth-service</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                Backend
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Manages user authentication, JWT tokens, and OAuth provider integrations.
              Source of truth for identity.
            </p>
          </div>

          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm font-medium">payment-service</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                Backend
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Stripe integration for payment processing. Handles checkout sessions,
              webhooks, and invoicing.
            </p>
          </div>
        </div>
      </section>

      {/* Communication patterns */}
      <section>
        <h2 className="text-lg font-medium mb-3">Communication Patterns</h2>
        <div className="space-y-3 text-sm text-muted-foreground">
          <div className="flex items-start gap-3">
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground shrink-0">
              REST
            </span>
            <span>
              Synchronous HTTP/JSON for client-facing APIs and service-to-service calls
              where immediate response is needed.
            </span>
          </div>

          <div className="flex items-start gap-3">
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground shrink-0">
              Events
            </span>
            <span>
              Async event bus for order updates, inventory changes, and notifications.
              Services subscribe to relevant topics.
            </span>
          </div>

          <div className="flex items-start gap-3">
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground shrink-0">
              Cache
            </span>
            <span>
              Redis for session storage, rate limiting state, and frequently accessed data
              like product catalog.
            </span>
          </div>
        </div>
      </section>

      {/* Data ownership */}
      <section>
        <h2 className="text-lg font-medium mb-3">Data Ownership</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="pb-2 text-left font-medium">Domain</th>
                <th className="pb-2 text-left font-medium">Owner</th>
                <th className="pb-2 text-left font-medium text-muted-foreground">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              <tr>
                <td className="py-3">Users & Auth</td>
                <td className="py-3 font-mono text-xs">auth-service</td>
                <td className="py-3 text-muted-foreground">
                  Source of truth for identity
                </td>
              </tr>
              <tr>
                <td className="py-3">Orders</td>
                <td className="py-3 font-mono text-xs">order-service</td>
                <td className="py-3 text-muted-foreground">
                  Includes order history and status
                </td>
              </tr>
              <tr>
                <td className="py-3">Payments</td>
                <td className="py-3 font-mono text-xs">payment-service</td>
                <td className="py-3 text-muted-foreground">
                  Transactions, refunds, invoices
                </td>
              </tr>
              <tr>
                <td className="py-3">Products</td>
                <td className="py-3 font-mono text-xs">catalog-service</td>
                <td className="py-3 text-muted-foreground">
                  Product metadata and pricing
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default ArchitectureTab;
