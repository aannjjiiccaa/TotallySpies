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
    {
      id: "repo-web",
      kind: "repo",
      label: "web-storefront",
      repo: "repo-web",
      description: "React storefront with checkout and product exploration.",
    },
    {
      id: "repo-admin",
      kind: "repo",
      label: "admin-dashboard",
      repo: "repo-admin",
      description: "Operational dashboard for support, merchandising, and catalog edits.",
    },
    {
      id: "repo-auth",
      kind: "repo",
      label: "auth-service",
      repo: "repo-auth",
      description: "Identity, sessions, and credential recovery.",
    },
    {
      id: "repo-order",
      kind: "repo",
      label: "order-service",
      repo: "repo-order",
      description: "Order lifecycle orchestration and status tracking.",
    },
    {
      id: "repo-payment",
      kind: "repo",
      label: "payment-service",
      repo: "repo-payment",
      description: "Payment, refund, and billing integrations.",
    },

    // services
    {
      id: "svc-gateway",
      kind: "service",
      label: "api-gateway",
      repo: "repo-web",
      description: "Edge router that authenticates users and routes traffic to downstream services.",
      meta: { entryPoint: true },
    },
    {
      id: "svc-auth",
      kind: "service",
      label: "auth",
      repo: "repo-auth",
      description: "Issues tokens, enforces auth, and integrates with third-party identity providers.",
      meta: { domain: "identity" },
    },
    {
      id: "svc-order",
      kind: "service",
      label: "orders",
      repo: "repo-order",
      description: "Creates orders, reserves inventory, and publishes order events.",
      meta: { domain: "orders" },
    },
    {
      id: "svc-payment",
      kind: "service",
      label: "payments",
      repo: "repo-payment",
      description: "Handles checkout sessions, payment intents, and billing webhooks.",
      meta: { domain: "billing" },
    },

    // infra
    {
      id: "db-postgres",
      kind: "db",
      label: "PostgreSQL",
      description: "Primary relational store for orders, payments, and users.",
      meta: { role: "primary store" },
    },
    {
      id: "db-redis",
      kind: "db",
      label: "Redis",
      description: "Cache for sessions, rate limiting, and hot product reads.",
      meta: { role: "cache/sessions" },
    },
    {
      id: "queue-events",
      kind: "queue",
      label: "event-bus",
      description: "Pub/Sub topics for order lifecycle and notification fan-out.",
      meta: { topics: ["order.created"] },
    },

    // files
    {
      id: "file-auth-controller",
      kind: "file",
      label: "auth.controller.ts",
      repo: "repo-auth",
      description: "HTTP handlers for login, signup, and password reset that call the auth service.",
      meta: { path: "src/auth/auth.controller.ts" },
    },
    {
      id: "file-order-handler",
      kind: "file",
      label: "order.handler.ts",
      repo: "repo-order",
      description: "Background worker that processes order events, updates status, and writes projections.",
      meta: { path: "src/orders/order.handler.ts" },
    },
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

const LANE_HEIGHT = 160;
const BASE_Y = 140;
const KIND_X: Record<NodeKind, number> = {
  repo: 120,
  service: 360,
  db: 620,
  queue: 880,
  file: 1140,
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
    description?: string;
    repoLabel?: string;
  } | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const graph = useMemo(() => getPlaceholderGraph(), []);
  const layoutPadding = 60;

  const repoNodes = useMemo(() => graph.nodes.filter((n) => n.kind === "repo"), [graph]);

  const repoColors = useMemo(() => {
    const palette = ["#dedefe", "#c6fbc2", "#e8f7ff", "#f2eefe", "#e7ffdb", "#d8e3ff"];
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

  const repoLegend = useMemo(
    () => repoNodes.map((repo) => ({ id: repo.id, label: repo.label, color: repoColors[repo.id] })),
    [repoNodes, repoColors]
  );

  const elements: ElementDefinition[] = useMemo(() => {
    const typeColor: Record<NodeKind, string> = {
      repo: "#dedefe", // lilac
      service: "#c6fbc2", // soft green
      file: "#f5f7fb",
      db: "#e8f7ff",
      queue: "#f2eefe",
    };

    // Pre-compute lane positions for a swimlane-style layout.
    const laneIds = [...repoNodes.map((r) => r.id), "infra"];
    const laneIndex = (node: GraphNode) => laneIds.indexOf(node.repo ?? "infra");

    const nodeElements: ElementDefinition[] = graph.nodes.map((n) => {
      const color = typeColor[n.kind] ?? "#f8fafc";
      const y = BASE_Y + laneIndex(n) * LANE_HEIGHT;
      const x = KIND_X[n.kind] ?? 200;

      return {
        data: {
          id: n.id,
          label: n.label,
          kind: n.kind,
          repo: n.repo,
          description: n.description ?? "",
          meta: n.meta ?? {},
          color,
        },
        position: { x, y },
      };
    });

    const edgeElements: ElementDefinition[] = graph.edges.map((e) => ({
      data: { id: e.id, source: e.source, target: e.target, kind: e.kind },
    }));

    return [...nodeElements, ...edgeElements];
  }, [graph, repoColors]);

  const selectNode = (node: any) => {
    const cy = cyRef.current;
    if (!cy || !node) return;

    cy.elements().removeClass("selected dim");
    node.addClass("selected");

    const neighborhood = node.closedNeighborhood();
    cy.elements().difference(neighborhood).addClass("dim");

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
        return `${e.data("kind")}: ${s} -> ${t}`;
      }),
    });
  };

  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current?.destroy();

    const ACCENT = "#69FF47"; // soft green accent
    const BORDER = "rgba(15, 23, 42, 0.14)"; // slate-900 at ~14%
    const EDGE = "rgba(15, 23, 42, 0.22)";
    const TEXT = "#0f172a";
    const TEXT_OUTLINE = "#ffffff";

    const style = [
      {
        selector: "node",
        style: {
          label: "data(label)",
          "font-family":
            'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
          "font-size": "13px",
          "font-weight": "700",
          color: TEXT,
          "text-wrap": "wrap",
          "text-max-width": "140px",
          "text-background-opacity": 0,
          "text-outline-width": 0,
          "text-outline-color": TEXT_OUTLINE,
          "background-color": "data(color)",
          shape: "roundrectangle",
          width: "160px",
          height: "52px",
          "border-radius": "14px",
          "border-width": "1px",
          "border-color": "rgba(15,23,42,0.14)",
          "text-valign": "center",
          "text-halign": "center",
          padding: "12px",
          "shadow-blur": 16,
          "shadow-color": "rgba(15,23,42,0.08)",
          "shadow-offset-x": 0,
          "shadow-offset-y": 8,
        },
      },

      {
        selector: 'node[kind="service"]',
        style: {
          width: "170px",
          height: "56px",
          "border-radius": "16px",
          "border-width": "2px",
          "border-color": "#69FF47",
          "font-size": "13px",
          "font-weight": "700",
          "text-max-width": "150px",
        },
      },

      {
        selector: 'node[kind="repo"]',
        style: {
          width: "170px",
          height: "56px",
          "border-radius": "16px",
          "border-width": "1.5px",
          "border-color": "rgba(15,23,42,0.2)",
          "text-max-width": "150px",
          "font-weight": "700",
        },
      },

      {
        selector: 'node[kind="file"]',
        style: {
          shape: "roundrectangle",
          width: "220px",
          height: "54px",
          "border-radius": "18px",
          "font-size": "12px",
          "font-weight": "600",
          "text-wrap": "wrap",
          "text-max-width": "200px",
          "border-width": "1px",
          "border-color": "rgba(15,23,42,0.16)",
          padding: "8px",
        },
      },
      {
        selector: 'node[kind="db"], node[kind="queue"]',
        style: {
          shape: "roundrectangle",
          width: "200px",
          height: "50px",
          "border-radius": "16px",
          "font-size": "12px",
          "font-weight": "600",
          "text-max-width": "170px",
          "border-width": "1px",
          "border-color": "rgba(15,23,42,0.16)",
          padding: "6px",
        },
      },

      {
        selector: "edge",
        style: {
          width: "1px",
          "line-color": "rgba(15,23,42,0.16)",
          "curve-style": "taxi",
          "taxi-direction": "auto",
          "taxi-turn": 10,
          "taxi-turn-min-distance": 12,
          "target-arrow-shape": "triangle",
          "target-arrow-color": "rgba(15,23,42,0.16)",
          "arrow-scale": 0.5,
          label: "data(kind)",
          "font-size": "9px",
          "text-opacity": 0,
          "text-background-opacity": 0,
          "text-rotation": "autorotate",
          "text-margin-y": "-4px",
        },
      },
      {
        selector: "edge:hover",
        style: {
          "text-opacity": 1,
          "text-background-opacity": 0.92,
          "text-background-color": "#ffffff",
          "text-background-shape": "roundrectangle",
          "text-background-padding": "2px",
          color: "#0f172a",
          "font-weight": "600",
          "z-index": 9999,
        },
      },
      {
        selector: ".show-label",
        style: {
          "text-opacity": 1,
          "text-background-opacity": 0.92,
          "text-background-color": "#ffffff",
          "text-background-shape": "roundrectangle",
          "text-background-padding": "2px",
          color: "#0f172a",
          "font-weight": "600",
          "z-index": 9999,
        },
      },
      { selector: 'edge[kind="DEPENDS_ON"]', style: { "line-style": "dashed" } },
      { selector: 'edge[kind="PUBLISHES"]', style: { "line-style": "dotted" } },

      { selector: ".selected", style: { "border-color": ACCENT, "border-width": "4px" } },
      { selector: ".dim", style: { opacity: 0.18 } },
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
        animationDuration: 380,
        animationEasing: "ease-out-cubic",
      },
      style,
    }) as Core;

    cyRef.current = cy;

    cy.nodes().ungrabify(); // lock positions; keep zoom/pan enabled
    cy.boxSelectionEnabled(false);

    cy.fit(undefined, layoutPadding);
    cy.zoom(cy.zoom() * 1.3);

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      selectNode(node);
    });

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const repoId = node.data("repo") as string | undefined;
      setHovered({
        id: node.data("id"),
        label: node.data("label"),
        description: node.data("description"),
        repoLabel: repoId ? repoLookup[repoId] ?? repoId : undefined,
      });
    });

    cy.on("mouseout", "node", () => setHovered(null));

    cy.on("mouseover", "edge", (evt) => {
      evt.target.addClass("show-label");
    });
    cy.on("mouseout", "edge", (evt) => {
      evt.target.removeClass("show-label");
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass("selected dim");
        setSelected(null);
      }
    });

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [elements, repoLookup, repoColors, layoutPadding]);

  const smoothZoom = (factor: number) => {
    if (!cyRef.current) return;
    const cy = cyRef.current;
    const targetZoom = cy.zoom() * factor;
    cy.animate({ zoom: targetZoom }, { duration: 140, easing: "ease-out" });
  };

  const zoomIn = () => smoothZoom(1.06);
  const zoomOut = () => smoothZoom(1 / 1.06);
  const fit = () => {
    cyRef.current?.fit(undefined, layoutPadding);
    if (cyRef.current) {
      cyRef.current.animate({ zoom: cyRef.current.zoom() * 1.3 }, { duration: 180, easing: "ease-out" });
    }
  };
  const resetView = () => {
    cyRef.current?.elements().removeClass("selected dim");
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
    if (match) {
      selectNode(match);
      cy.animate({ center: { eles: match }, zoom: Math.min(cy.zoom() * 1.08, 2.5) }, { duration: 200, easing: "ease-out" });
    }
  };

  return (
    <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_320px] min-h-[70vh]">
        <div className="relative bg-card">
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              backgroundImage:
                "radial-gradient(circle at 1px 1px, rgba(15,23,42,0.06) 1px, transparent 0)",
              backgroundSize: "26px 26px",
            }}
          />

          {hovered && (
            <div className="absolute left-3 top-3 z-10 rounded-md border border-border bg-background/90 px-3 py-2 shadow-sm backdrop-blur text-xs max-w-sm">
              <div className="font-semibold text-foreground">{hovered.label}</div>
              {hovered.repoLabel && <div className="text-muted-foreground">{hovered.repoLabel}</div>}
              {hovered.description && (
                <div className="text-muted-foreground mt-1 leading-snug max-h-20 overflow-hidden text-ellipsis">
                  {hovered.description}
                </div>
              )}
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
              className="rounded-full border border-border bg-card px-3 py-1 text-xs"
              onClick={handleSearch}
            >
              Search
            </button>
          </div>

          <div
            ref={containerRef}
            className="h-[74vh] min-h-[620px] max-h-[820px] w-full cursor-default"
          />

          <div className="absolute left-3 bottom-3 z-10 flex items-center gap-2">
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={zoomIn}>
              +
            </button>
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={zoomOut}>
              -
            </button>
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={fit}>
              Fit
            </button>
            <button className="rounded-full border border-border bg-background px-3 py-2 text-xs shadow-sm" onClick={resetView}>
              Reset
            </button>
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
                <div className="font-mono text-sm font-medium">{selected.label}</div>
                <div className="text-xs text-muted-foreground font-mono">{selected.id}</div>
                {selected.repo && (
                  <div className="flex items-center gap-2 text-xs">
                    <span
                      className="h-3 w-3 rounded-full border border-border"
                      style={{ backgroundColor: selected.repo.color }}
                    />
                    <span className="font-medium">{selected.repo.label}</span>
                  </div>
                )}
              </div>

              {selected.description && (
                <p className="text-sm text-muted-foreground leading-relaxed">{selected.description}</p>
              )}

              {selected.meta && Object.keys(selected.meta).length > 0 && (
                <div>
                  <div className="text-xs font-medium mb-1">Meta</div>
                  <pre className="text-xs bg-muted p-3 rounded font-mono whitespace-pre-wrap">
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
