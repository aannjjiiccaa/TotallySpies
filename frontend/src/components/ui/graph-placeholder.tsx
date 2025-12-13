import { useEffect, useMemo, useRef, useState } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";

type NodeKind = "repo" | "service" | "file" | "db" | "queue";
type EdgeKind = "CONTAINS" | "DEPENDS_ON" | "CALLS" | "READS_WRITES" | "PUBLISHES";

interface GraphNode {
  id: string;
  kind: NodeKind;
  label: string;
  repo?: string;
  description?: string;
  meta?: Record<string, any>;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  kind: EdgeKind;
}

function getPlaceholderGraph(): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = [
    // repos
    { id: "repo-web", kind: "repo", label: "web-storefront", repo: "repo-web", description: "React storefront with checkout and product exploration." },
    { id: "repo-admin", kind: "repo", label: "admin-dashboard", repo: "repo-admin", description: "Operational dashboard for support, merchandising, and catalog edits." },
    { id: "repo-auth", kind: "repo", label: "auth-service", repo: "repo-auth", description: "Identity, sessions, and credential recovery." },
    { id: "repo-order", kind: "repo", label: "order-service", repo: "repo-order", description: "Order lifecycle orchestration and status tracking." },
    { id: "repo-payment", kind: "repo", label: "payment-service", repo: "repo-payment", description: "Payment, refund, and billing integrations." },

    // services
    { id: "svc-gateway", kind: "service", label: "api-gateway", repo: "repo-web", description: "Edge router that authenticates users and routes traffic to downstream services.", meta: { entryPoint: true } },
    { id: "svc-auth", kind: "service", label: "auth", repo: "repo-auth", description: "Issues tokens, enforces auth, and integrates with third-party identity providers.", meta: { domain: "identity" } },
    { id: "svc-order", kind: "service", label: "orders", repo: "repo-order", description: "Creates orders, reserves inventory, and publishes order events.", meta: { domain: "orders" } },
    { id: "svc-payment", kind: "service", label: "payments", repo: "repo-payment", description: "Handles checkout sessions, payment intents, and billing webhooks.", meta: { domain: "billing" } },

    // infra
    { id: "db-postgres", kind: "db", label: "PostgreSQL", description: "Primary relational store for orders, payments, and users.", meta: { role: "primary store" } },
    { id: "db-redis", kind: "db", label: "Redis", description: "Cache for sessions, rate limiting, and hot product reads.", meta: { role: "cache/sessions" } },
    { id: "queue-events", kind: "queue", label: "event-bus", description: "Pub/Sub topics for order lifecycle and notification fan-out.", meta: { topics: ["order.created"] } },

    // files
    { id: "file-auth-controller", kind: "file", label: "auth.controller.ts", repo: "repo-auth", description: "HTTP handlers for login, signup, and password reset that call the auth service.", meta: { path: "src/auth/auth.controller.ts" } },
    { id: "file-order-handler", kind: "file", label: "order.handler.ts", repo: "repo-order", description: "Background worker that processes order events, updates status, and writes projections.", meta: { path: "src/orders/order.handler.ts" } },
  ];

  const edges: GraphEdge[] = [
    { id: "e1", source: "repo-web", target: "svc-gateway", kind: "CALLS" },
    { id: "e2", source: "repo-admin", target: "svc-gateway", kind: "CALLS" },

    { id: "e3", source: "svc-gateway", target: "svc-auth", kind: "CALLS" },
    { id: "e4", source: "svc-gateway", target: "svc-order", kind: "CALLS" },
    { id: "e5", source: "svc-gateway", target: "svc-payment", kind: "CALLS" },

    { id: "e6", source: "repo-auth", target: "svc-auth", kind: "DEPENDS_ON" },
    { id: "e7", source: "repo-order", target: "svc-order", kind: "DEPENDS_ON" },
    { id: "e8", source: "repo-payment", target: "svc-payment", kind: "DEPENDS_ON" },

    { id: "e9", source: "svc-auth", target: "db-postgres", kind: "READS_WRITES" },
    { id: "e10", source: "svc-order", target: "db-postgres", kind: "READS_WRITES" },
    { id: "e11", source: "svc-payment", target: "db-postgres", kind: "READS_WRITES" },

    { id: "e12", source: "svc-auth", target: "db-redis", kind: "READS_WRITES" },
    { id: "e13", source: "svc-gateway", target: "db-redis", kind: "READS_WRITES" },

    { id: "e14", source: "svc-order", target: "queue-events", kind: "PUBLISHES" },

    { id: "e15", source: "svc-auth", target: "file-auth-controller", kind: "CONTAINS" },
    { id: "e16", source: "svc-order", target: "file-order-handler", kind: "CONTAINS" },
  ];

  return { nodes, edges };
}

// Swimlanes layout
const BASE_X = 140;
const LANE_WIDTH = 260;

const KIND_Y: Record<NodeKind, number> = {
  repo: 140,
  service: 320,
  db: 500,
  queue: 680,
  file: 860,
};

// ✅ vesele boje: bg = border-ish, border = malo tamnije, text = čitljiv
const KIND_COLORS: Record<NodeKind, { bg: string; border: string; text: string }> = {
  repo: { bg: "#93C5FD", border: "#2563EB", text: "#0B1220" },     // blue
  service: { bg: "#86EFAC", border: "#16A34A", text: "#0B1220" },  // green
  file: { bg: "#FDE68A", border: "#D97706", text: "#0B1220" },     // yellow
  db: { bg: "#C4B5FD", border: "#7C3AED", text: "#0B1220" },       // purple
  queue: { bg: "#F9A8D4", border: "#DB2777", text: "#0B1220" },    // pink
};

export default function ProjectGraphPlaceholder() {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [selected, setSelected] = useState<{
    id: string;
    label: string;
    kind: NodeKind;
    description?: string;
    repo?: { id: string; label: string; color?: string };
    meta?: Record<string, any>;
    neighbors: string[];
    edges: string[];
  } | null>(null);

  const [hovered, setHovered] = useState<{
    id: string;
    label: string;
    kind: NodeKind;
    description?: string;
    repoLabel?: string;
  } | null>(null);

  const [searchTerm, setSearchTerm] = useState("");

  const graph = useMemo(() => getPlaceholderGraph(), []);
  const layoutPadding = 60;

  const repoNodes = useMemo(() => graph.nodes.filter((n) => n.kind === "repo"), [graph]);

  const repoColors = useMemo(() => {
    const palette = ["#E0E7FF", "#DCFCE7", "#FEF9C3", "#F3E8FF", "#FCE7F3", "#E2E8F0"];
    return repoNodes.reduce<Record<string, string>>((acc, repo, idx) => {
      acc[repo.id] = palette[idx % palette.length];
      return acc;
    }, {});
  }, [repoNodes]);

  const repoLookup = useMemo(
    () =>
      repoNodes.reduce<Record<string, string>>((acc, repo) => {
        acc[repo.id] = repo.label;
        return acc;
      }, {}),
    [repoNodes]
  );

  // pozicioniranje bez preklapanja (infra db/queue širi po X)
  const elements: ElementDefinition[] = useMemo(() => {
    const laneIds = [...repoNodes.map((r) => r.id), "infra"];
    const laneIndex = (node: GraphNode) => laneIds.indexOf(node.repo ?? "infra");

    const counters: Record<string, number> = {};
    const nextOffsetIndex = (lane: number, kind: NodeKind) => {
      const key = `${lane}:${kind}`;
      counters[key] = (counters[key] ?? 0) + 1;
      return counters[key] - 1;
    };

    const spread = (k: number) => (k === 0 ? 0 : (k % 2 === 1 ? 1 : -1) * Math.ceil(k / 2));

    const nodeElements: ElementDefinition[] = graph.nodes.map((n) => {
      const c = KIND_COLORS[n.kind];

      const lane = laneIndex(n);
      const baseX = BASE_X + lane * LANE_WIDTH;
      const baseY = KIND_Y[n.kind] ?? 200;

      const i = nextOffsetIndex(lane, n.kind);

      const STEP_X = n.kind === "db" || n.kind === "queue" ? 160 : 95;
      const STEP_Y = n.kind === "file" ? 28 : 20;

      const dx = spread(i) * STEP_X;
      const dy = n.repo ? i * STEP_Y : 0;

      return {
        data: {
          id: n.id,
          label: n.label,
          kind: n.kind,
          repo: n.repo,
          description: n.description ?? "",
          meta: n.meta ?? {},
          bgColor: c.bg,
          borderColor: c.border,
          textColor: c.text,
        },
        position: { x: baseX + dx, y: baseY + dy },
      };
    });

    const edgeElements: ElementDefinition[] = graph.edges.map((e) => ({
      data: { id: e.id, source: e.source, target: e.target, kind: e.kind },
    }));

    return [...nodeElements, ...edgeElements];
  }, [graph, repoNodes]);

  const selectNode = (node: any) => {
    const cy = cyRef.current;
    if (!cy || !node) return;

    cy.elements().removeClass("selected dimmed");
    node.addClass("selected");

    const neighborhood = node.closedNeighborhood();
    cy.elements().difference(neighborhood).addClass("dimmed");

    const repoId = node.data("repo") as string | undefined;

    setSelected({
      id: node.data("id"),
      label: node.data("label"),
      kind: node.data("kind"),
      description: node.data("description"),
      repo: repoId ? { id: repoId, label: repoLookup[repoId] ?? repoId, color: repoColors[repoId] } : undefined,
      meta: node.data("meta") ?? {},
      neighbors: node.neighborhood("node").map((n: any) => n.data("label")),
      edges: node.connectedEdges().map((e: any) => {
        const s = e.source().data("label");
        const t = e.target().data("label");
        return `${e.data("kind")}: ${s} → ${t}`;
      }),
    });
  };

  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current?.destroy();

    const style = [
      {
        selector: "node",
        style: {
          label: "data(label)",
          "font-family": "DM Sans, system-ui, sans-serif",
          "font-size": "13px",
          "font-weight": 650,
          color: "data(textColor)",
          "text-valign": "bottom",
          "text-halign": "center",
          "text-margin-y": 8,
          "text-wrap": "wrap",
          "text-max-width": "120px",
          "background-color": "data(bgColor)",
          "border-width": 2,
          "border-color": "data(borderColor)",
          shape: "round-rectangle",
          width: 56,
          height: 56,
          "overlay-opacity": 0,

          // ✅ shadow default (blaga) + hover jača
          "shadow-opacity": 0.18,
          "shadow-blur": 8,
          "shadow-offset-x": 0,
          "shadow-offset-y": 4,
          "shadow-color": "rgba(15, 23, 42, 0.35)",

          "transition-property": "border-width, width, height, opacity, shadow-opacity, shadow-blur, shadow-offset-y",
          "transition-duration": 150,
        } as any,
      },

      // jači shadow na hover (vidljiv!)
      {
        selector: "node.hovered",
        style: {
          "shadow-opacity": 0.32,
          "shadow-blur": 10,
          "shadow-offset-y": 6,
        } as any,
      },

      {
        selector: "node.selected",
        style: {
          "border-width": 3,
          width: 64,
          height: 64,
          opacity: 1,
        } as any,
      },
      {
        selector: "node.dimmed",
        style: { opacity: 0.22 } as any,
      },

      // edge: orto + rounded corners, bez labela, bez “click thicken”
      {
        selector: "edge",
        style: {
          width: 2,
          "line-color": "#94a3b8",
          "curve-style": "taxi",
          "taxi-direction": "auto",
          "taxi-turn": 24,
          "taxi-turn-min-distance": 16,
          "taxi-radius": 18,

          "target-arrow-shape": "triangle",
          "target-arrow-color": "#94a3b8",
          "arrow-scale": 0.9,
          opacity: 0.7,

          label: "",
          "text-opacity": 0,

          "transition-property": "opacity, line-color, target-arrow-color",
          "transition-duration": 150,
        } as any,
      },

      { selector: "edge.dimmed", style: { opacity: 0.12 } as any },
      { selector: 'edge[kind="DEPENDS_ON"]', style: { "line-style": "dashed" } as any },
      {
        selector: 'edge[kind="PUBLISHES"]',
        style: {
          "line-style": "dotted",
          "line-color": "#DB2777",
          "target-arrow-color": "#DB2777",
        } as any,
      },
    ] as any;

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      pixelRatio: Math.max(2, window.devicePixelRatio || 1),
      wheelSensitivity: 0.12,
      layout: {
        name: "preset",
        fit: true,
        padding: layoutPadding,
        animate: true,
        animationDuration: 320,
        animationEasing: "ease-out",
      },
      style,
    }) as Core;

    cyRef.current = cy;
    cy.nodes().ungrabify();
    cy.boxSelectionEnabled(false);

    cy.fit(undefined, layoutPadding);
    cy.zoom(cy.zoom() * 1.2);

    cy.on("tap", "node", (evt) => selectNode(evt.target));

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      node.addClass("hovered");

      const repoId = node.data("repo") as string | undefined;
      setHovered({
        id: node.data("id"),
        label: node.data("label"),
        kind: node.data("kind"),
        description: node.data("description"),
        repoLabel: repoId ? repoLookup[repoId] ?? repoId : undefined,
      });
    });

    cy.on("mouseout", "node", (evt) => {
      evt.target.removeClass("hovered");
      setHovered(null);
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass("selected dimmed");
        setSelected(null);
      }
    });

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [elements, repoLookup, repoColors, layoutPadding]);

  const smoothZoom = (factor: number) => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.animate({ zoom: cy.zoom() * factor }, { duration: 140, easing: "ease-out" as any });
  };

  const zoomIn = () => smoothZoom(1.06);
  const zoomOut = () => smoothZoom(1 / 1.06);

  const fit = () => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.fit(undefined, layoutPadding);
    cy.animate({ zoom: cy.zoom() * 1.2 }, { duration: 160, easing: "ease-out" as any });
  };

  const resetView = () => {
    cyRef.current?.elements().removeClass("selected dimmed");
    setSelected(null);
    setHovered(null);
    fit();
  };

  const handleSearch = () => {
    const cy = cyRef.current;
    if (!cy) return;
    const term = searchTerm.trim().toLowerCase();
    if (!term) return;

    const match = cy
      .nodes()
      .filter((n) => (n.data("label") as string)?.toLowerCase().includes(term) || n.id().toLowerCase().includes(term))
      .first();

    if (match && match.length > 0) {
      selectNode(match);
      cy.animate({ center: { eles: match }, zoom: Math.min(cy.zoom() * 1.08, 2.5) }, { duration: 200, easing: "ease-out" as any });
    }
  };

  return (
    <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_320px] min-h-[70vh]">
        <div className="relative bg-card">
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              backgroundImage: "radial-gradient(circle at 1px 1px, rgba(15,23,42,0.06) 1px, transparent 0)",
              backgroundSize: "26px 26px",
            }}
          />

          {hovered && (
            <div className="absolute left-3 top-3 z-10 rounded-md border border-border bg-background/90 px-3 py-2 shadow-sm backdrop-blur text-xs max-w-sm">
              <div className="flex items-center gap-2">
                <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: KIND_COLORS[hovered.kind].border }} />
                <div className="font-semibold text-foreground">{hovered.label}</div>
              </div>
              {hovered.repoLabel && <div className="text-muted-foreground mt-0.5">{hovered.repoLabel}</div>}
              {hovered.description && <div className="text-muted-foreground mt-1 leading-snug max-h-20 overflow-hidden text-ellipsis">{hovered.description}</div>}
            </div>
          )}

          <div className="absolute right-3 top-3 z-10 flex items-center gap-2 rounded-full border border-border bg-background px-2 py-1 shadow-sm">
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="h-8 w-44 rounded-full border border-border bg-background px-3 text-xs outline-none"
              placeholder="Search nodes..."
            />
            <button
              className="rounded-full border px-3 py-1 text-xs transition-colors"
              style={{ backgroundColor: "#69ff47", color: "#fff", borderColor: "#69ff47" }}
              onClick={handleSearch}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = "#fff";
                e.currentTarget.style.color = "#69ff47";
                e.currentTarget.style.borderColor = "#69ff47";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = "#69ff47";
                e.currentTarget.style.color = "#fff";
                e.currentTarget.style.borderColor = "#69ff47";
              }}
            >
              Search
            </button>
          </div>

          <div ref={containerRef} className="h-[74vh] min-h-[620px] max-h-[820px] w-full cursor-default" />

          <div className="absolute left-3 bottom-3 z-10 flex items-center gap-2">
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={zoomIn}>+</button>
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={zoomOut}>-</button>
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={fit}>Fit</button>
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={resetView}>Reset</button>
          </div>

          {/* Legend */}
          <div className="absolute right-3 bottom-3 z-10">
            <div className="bg-background/90 border border-border rounded-xl p-3 shadow-sm backdrop-blur">
              <p className="text-xs font-medium text-muted-foreground mb-2">Node Types</p>
              <div className="flex flex-wrap gap-2">
                {(Object.keys(KIND_COLORS) as NodeKind[]).map((kind) => {
                  const c = KIND_COLORS[kind];
                  return (
                    <div
                      key={kind}
                      className="flex items-center gap-2 px-2 py-1 rounded-md text-xs font-medium capitalize"
                      style={{ backgroundColor: c.bg, color: "#0B1220" }}
                    >
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: c.border }} />
                      {kind}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        <aside className="border-l border-border bg-card px-4 py-4 xl:sticky xl:top-20 h-full space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Details</h3>
            <span className="text-[11px] text-muted-foreground uppercase">Inspector</span>
          </div>

          {!selected ? (
            <p className="text-sm text-muted-foreground">Click a node to see details.</p>
          ) : (
            <div className="space-y-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: KIND_COLORS[selected.kind].border }} />
                  <div className="font-mono text-sm font-medium">{selected.label}</div>
                </div>

                <div className="text-xs text-muted-foreground font-mono">{selected.id}</div>
                <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{selected.kind}</div>

                {selected.repo && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: selected.repo.color }} />
                    <span className="font-medium">{selected.repo.label}</span>
                  </div>
                )}
              </div>

              {selected.description && <p className="text-sm text-muted-foreground leading-relaxed">{selected.description}</p>}

              {selected.meta && Object.keys(selected.meta).length > 0 && (
                <div>
                  <div className="text-xs font-medium mb-1">Meta</div>
                  <pre className="text-xs bg-muted p-3 rounded font-mono whitespace-pre-wrap overflow-x-auto">
                    {JSON.stringify(selected.meta, null, 2)}
                  </pre>
                </div>
              )}

              {selected.neighbors?.length > 0 && (
                <div>
                  <div className="text-xs font-medium mb-1">Neighbors</div>
                  <ul className="list-disc ml-5 text-xs text-muted-foreground space-y-0.5">
                    {selected.neighbors.slice(0, 12).map((n) => (
                      <li key={n}>{n}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selected.edges?.length > 0 && (
                <div>
                  <div className="text-xs font-medium mb-1">Edges</div>
                  <ul className="list-disc ml-5 text-xs text-muted-foreground space-y-0.5">
                    {selected.edges.slice(0, 12).map((e) => (
                      <li key={e}>{e}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
