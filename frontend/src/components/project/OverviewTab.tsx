import { Project } from "@/types/project";

interface OverviewTabProps {
  project: Project;
}

const OverviewTab = ({ project }: OverviewTabProps) => {
  return (
    <div className="animate-fade-in space-y-8">
      <section>
        <h2 className="text-lg font-medium mb-3">What is this?</h2>
        <p className="text-muted-foreground leading-relaxed">
          {project.description}
        </p>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">Key Points</h2>
        <ul className="space-y-2 text-muted-foreground">
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
            <span>Handles end-to-end commerce operations including product catalog, cart management, and checkout</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
            <span>Multi-tenant architecture supporting multiple storefronts from a single codebase</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
            <span>Event-driven communication between services for loose coupling</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
            <span>Designed for horizontal scaling with stateless services</span>
          </li>
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">Core Domains</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {["Authentication & Authorization", "Product Catalog", "Order Management", "Payment Processing", "Inventory & Fulfillment", "Notifications"].map((domain) => (
            <div key={domain} className="rounded-lg border border-border bg-card p-4">
              <span className="font-medium text-sm">{domain}</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">Who Uses This</h2>
        <div className="flex flex-wrap gap-2">
          {["Product Team", "Engineering", "Customer Support", "Partners"].map((team) => (
            <span
              key={team}
              className="inline-flex items-center rounded-full bg-secondary px-3 py-1 text-sm text-secondary-foreground"
            >
              {team}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
};

export default OverviewTab;
