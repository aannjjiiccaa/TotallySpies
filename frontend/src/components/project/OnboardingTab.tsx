import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Project } from "@/types/project";

interface OnboardingTabProps {
  project: Project;
}

const OnboardingTab = ({ project }: OnboardingTabProps) => {
  return (
    <div className="animate-fade-in">
      <p className="text-sm text-muted-foreground mb-6">
        Role-based guides to get you productive quickly.
      </p>

      <Accordion type="single" collapsible className="space-y-2">
        <AccordionItem value="backend" className="border border-border rounded-lg px-4">
          <AccordionTrigger className="hover:no-underline py-4">
            <span className="font-medium">Backend Developer</span>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="font-medium mb-2">Starter Repos</h4>
                <ul className="space-y-1 text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span className="font-mono">api-gateway</span> — Start here to understand request flow
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span className="font-mono">auth-service</span> — Core authentication patterns
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Core Services to Understand</h4>
                <p className="text-muted-foreground">
                  Focus on order-service and payment-service for business logic. These handle most customer-facing operations.
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-2">Common Pitfalls</h4>
                <ul className="space-y-1 text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-destructive" />
                    Don't bypass the gateway for service-to-service calls in dev
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-destructive" />
                    Always use the shared event types from @company/events
                  </li>
                </ul>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="frontend" className="border border-border rounded-lg px-4">
          <AccordionTrigger className="hover:no-underline py-4">
            <span className="font-medium">Frontend Developer</span>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="font-medium mb-2">UI Repository Structure</h4>
                <p className="text-muted-foreground">
                  <span className="font-mono">web-storefront</span> uses Next.js with the app router. 
                  <span className="font-mono">admin-dashboard</span> is a Vite + React SPA.
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-2">API Dependencies</h4>
                <p className="text-muted-foreground">
                  All API calls go through the gateway. Use the generated TypeScript client from <span className="font-mono">@company/api-client</span>.
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-2">Shared Components</h4>
                <p className="text-muted-foreground">
                  Check <span className="font-mono">shared-ui</span> before building new components. It contains the design system and common patterns.
                </p>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="devops" className="border border-border rounded-lg px-4">
          <AccordionTrigger className="hover:no-underline py-4">
            <span className="font-medium">DevOps / Infrastructure</span>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="font-medium mb-2">CI/CD Pipelines</h4>
                <p className="text-muted-foreground">
                  GitHub Actions for CI. ArgoCD for Kubernetes deployments. Each repo has its own workflow in <span className="font-mono">.github/workflows</span>.
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-2">Deployment Flow</h4>
                <p className="text-muted-foreground">
                  Staging deploys on merge to main. Production requires manual approval in ArgoCD. Rollbacks are automatic on health check failures.
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-2">Infrastructure as Code</h4>
                <p className="text-muted-foreground">
                  All cloud resources defined in <span className="font-mono">infrastructure</span> repo using Terraform. 
                  Environments: dev, staging, prod with separate state files.
                </p>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

export default OnboardingTab;
