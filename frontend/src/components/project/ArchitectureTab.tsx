import { Project } from "@/types/project";

interface ArchitectureTabProps {
  project: Project;
}

const ArchitectureTab = ({ project }: ArchitectureTabProps) => {
  return (
    <div className="animate-fade-in space-y-8">
      <section>
        <h2 className="text-lg font-medium mb-4">System Architecture</h2>
        
        {/* Simple architecture diagram placeholder */}
        <div className="rounded-lg border border-border bg-card p-8">
          <div className="flex flex-col items-center gap-6">
            {/* Clients */}
            <div className="flex gap-4">
              <div className="rounded border border-border bg-secondary px-4 py-2 text-sm font-mono">
                web-storefront
              </div>
              <div className="rounded border border-border bg-secondary px-4 py-2 text-sm font-mono">
                admin-dashboard
              </div>
            </div>
            
            <div className="h-6 w-px bg-border" />
            
            {/* Gateway */}
            <div className="rounded border-2 border-primary bg-orange-soft px-6 py-3 text-sm font-mono font-medium">
              api-gateway
            </div>
            
            <div className="h-6 w-px bg-border" />
            
            {/* Services */}
            <div className="flex flex-wrap justify-center gap-3">
              {["auth-service", "user-service", "order-service", "payment-service", "inventory-service"].map((service) => (
                <div key={service} className="rounded border border-border bg-card px-3 py-2 text-xs font-mono">
                  {service}
                </div>
              ))}
            </div>
            
            <div className="h-6 w-px bg-border" />
            
            {/* Data */}
            <div className="flex gap-4">
              <div className="rounded border border-border bg-muted px-4 py-2 text-sm font-mono text-muted-foreground">
                PostgreSQL
              </div>
              <div className="rounded border border-border bg-muted px-4 py-2 text-sm font-mono text-muted-foreground">
                Redis
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">Core Services</h2>
        <div className="space-y-4">
          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm font-medium">api-gateway</span>
              <span className="rounded bg-orange-soft px-2 py-0.5 text-xs text-primary font-medium">Entry Point</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Central routing layer. Handles authentication, rate limiting, and request forwarding to downstream services.
            </p>
          </div>

          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm font-medium">auth-service</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">Backend</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Manages user authentication, JWT tokens, and OAuth provider integrations. Source of truth for identity.
            </p>
          </div>

          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm font-medium">payment-service</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">Backend</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Stripe integration for payment processing. Handles checkout sessions, webhooks, and invoicing.
            </p>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">Communication Patterns</h2>
        <div className="space-y-3 text-sm text-muted-foreground">
          <div className="flex items-start gap-3">
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground shrink-0">REST</span>
            <span>Synchronous HTTP/JSON for client-facing APIs and service-to-service calls where immediate response is needed.</span>
          </div>
          <div className="flex items-start gap-3">
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground shrink-0">Events</span>
            <span>Async event bus for order updates, inventory changes, and notifications. Services subscribe to relevant topics.</span>
          </div>
          <div className="flex items-start gap-3">
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground shrink-0">Cache</span>
            <span>Redis for session storage, rate limiting state, and frequently accessed data like product catalog.</span>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">Data Ownership</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="pb-2 text-left font-medium">Domain</th>
                <th className="pb-2 text-left font-medium">Owner</th>
                <th className="pb-2 text-left font-medium text-muted-foreground">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              <tr>
                <td className="py-3">Users & Auth</td>
                <td className="py-3 font-mono text-xs">auth-service</td>
                <td className="py-3 text-muted-foreground">Source of truth for identity</td>
              </tr>
              <tr>
                <td className="py-3">Orders</td>
                <td className="py-3 font-mono text-xs">order-service</td>
                <td className="py-3 text-muted-foreground">Includes order history, status</td>
              </tr>
              <tr>
                <td className="py-3">Payments</td>
                <td className="py-3 font-mono text-xs">payment-service</td>
                <td className="py-3 text-muted-foreground">Transactions, refunds, invoices</td>
              </tr>
              <tr>
                <td className="py-3">Products</td>
                <td className="py-3 font-mono text-xs">catalog-service</td>
                <td className="py-3 text-muted-foreground">Product metadata, pricing</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default ArchitectureTab;
