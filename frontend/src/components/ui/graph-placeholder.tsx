import { useEffect, useMemo, useRef, useState } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";

/** input */
type RawGraph = {
  nodes?: Array<{ id: string; name: string; repo: string; description?: string }>;
  edges?: Array<{ from: string; to: string; type: string }>;
};

type NodeKind = "file";
type EdgeKind = string;

interface GraphNode {
  id: string; // full path
  kind: NodeKind;
  label: string; // name
  repo: string;
  description?: string;
  meta?: Record<string, any>;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  kind: EdgeKind;
}

/** repo theme palette (kao tvoj KIND_COLORS vibe) */
const REPO_THEMES = [
  { bg: "#93C5FD", border: "#2563EB", text: "#0B1220" }, // blue
  { bg: "#86EFAC", border: "#16A34A", text: "#0B1220" }, // green
  { bg: "#FDE68A", border: "#D97706", text: "#0B1220" }, // yellow
  { bg: "#C4B5FD", border: "#7C3AED", text: "#0B1220" }, // purple
  { bg: "#F9A8D4", border: "#DB2777", text: "#0B1220" }, // pink
];

const BASE_X = 140;

/** horizontal swimlanes */
const LANE_Y_START = 140;
const LANE_Y_GAP = 500;

/** spacing inside lanes */
const LEVEL_H = 110;         // ✅ visina nivoa unutar repo-a (manje -> zbijenije)
const COL_W = 150;           // ✅ razmak po X
const MAX_COLS_PER_LEVEL = 9; // ✅ posle ovoga ide novi “sub-row” u istom level-u
const SUBROW_H = 84;

function safeParseGraphData(graphData: any): RawGraph | undefined {
  if (!graphData) return undefined;
  try {
    return typeof graphData === "string" ? (JSON.parse(graphData) as RawGraph) : (graphData as RawGraph);
  } catch {
    return undefined;
  }
}

/** helper: stabilan sort po putanji */
function byPath(a: GraphNode, b: GraphNode) {
  return a.id.localeCompare(b.id);
}

/**
 * ✅ Compute "levels" inside a repo based on import edges:
 * - level[target] = max(level[src] + 1) for import edges src->target
 * - cycles: fallback keeps them at something stable (based on path depth)
 */
function computeLevelsForRepo(nodes: GraphNode[], edges: GraphEdge[]) {
  const ids = new Set(nodes.map((n) => n.id));

  // consider only import edges inside this repo
  const importEdges = edges.filter((e) => e.kind === "import" && ids.has(e.source) && ids.has(e.target));

  const indeg = new Map<string, number>();
  const out = new Map<string, string[]>();

  for (const n of nodes) {
    indeg.set(n.id, 0);
    out.set(n.id, []);
  }
  for (const e of importEdges) {
    out.get(e.source)!.push(e.target);
    indeg.set(e.target, (indeg.get(e.target) ?? 0) + 1);
  }

  // base fallback: path depth groups (keeps stable even with cycles)
  const depthFallback = (id: string) => id.split("/").filter(Boolean).length;

  // Kahn queue
  const q: string[] = [];
  for (const [id, d] of indeg.entries()) if (d === 0) q.push(id);
  q.sort((a, b) => a.localeCompare(b));

  const level = new Map<string, number>();
  for (const n of nodes) level.set(n.id, 0);

  let processed = 0;
  while (q.length) {
    const u = q.shift()!;
    processed++;

    const lu = level.get(u) ?? 0;
    for (const v of out.get(u) ?? []) {
      const next = lu + 1;
      if ((level.get(v) ?? 0) < next) level.set(v, next);

      indeg.set(v, (indeg.get(v) ?? 0) - 1);
      if ((indeg.get(v) ?? 0) === 0) {
        q.push(v);
        q.sort((a, b) => a.localeCompare(b));
      }
    }
  }

  // cycle nodes (not processed) -> give them a reasonable level using fallback depth + 1
  if (processed < nodes.length) {
    // find max computed level so far
    let maxL = 0;
    for (const v of level.values()) maxL = Math.max(maxL, v);

    for (const n of nodes) {
      // nodes still with indeg>0 are in a cycle
      if ((indeg.get(n.id) ?? 0) > 0) {
        // keep them near bottom but stable
        const l = Math.min(maxL + 1, 6) + (depthFallback(n.id) % 2);
        level.set(n.id, l);
      }
    }
  }

  return level;
}

export default function ProjectGraphPlaceholder({ graphData }: { graphData?: any } = {}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [selected, setSelected] = useState<{
    id: string;
    label: string;
    kind: NodeKind;
    repo?: { id: string; label: string; colorBg: string; colorBorder: string };
    meta?: Record<string, any>;
    description?: string;
    neighbors: string[];
    edges: string[];
  } | null>(null);

  const [hovered, setHovered] = useState<{
    id: string;
    label: string;
    repoLabel?: string;
    repoId?: string;
  } | null>(null);

  const [searchTerm, setSearchTerm] = useState("");

  const graph = useMemo(() => {
    const raw = safeParseGraphData(graphData);

    const nodes: GraphNode[] = (raw?.nodes ?? []).map((n) => ({
      id: n.id,
      kind: "file",
      label: n.name, // ✅ label = name
      repo: n.repo ?? "unknown",
      description: n.description ?? "",
      meta: { path: n.id, repo: n.repo, name: n.name, description: n.description ?? "" },
    }));

    const edges: GraphEdge[] = (raw?.edges ?? []).map((e, idx) => ({
      id: `e-${idx}-${e.type}`,
      source: e.from,
      target: e.to,
      kind: e.type,
    }));

    return { nodes, edges };
  }, [graphData]);

  const layoutPadding = 60;

  const repoIds = useMemo(() => {
    const set = new Set<string>();
    graph.nodes.forEach((n) => set.add(n.repo ?? "unknown"));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [graph.nodes]);

  const repoLookup = useMemo(() => {
    return repoIds.reduce<Record<string, string>>((acc, r) => {
      acc[r] = r;
      return acc;
    }, {});
  }, [repoIds]);

  const repoTheme = useMemo(() => {
    return repoIds.reduce<Record<string, { bg: string; border: string; text: string }>>((acc, repoId, idx) => {
      acc[repoId] = REPO_THEMES[idx % REPO_THEMES.length];
      return acc;
    }, {});
  }, [repoIds]);

  /** ✅ NEW: multi-level layout inside each repo to reduce edge mess */
  const elements: ElementDefinition[] = useMemo(() => {
    const grouped: Record<string, GraphNode[]> = {};
    for (const n of graph.nodes) (grouped[n.repo ?? "unknown"] ??= []).push(n);

    for (const repo of Object.keys(grouped)) grouped[repo].sort(byPath);

    const nodeElements: ElementDefinition[] = [];

    repoIds.forEach((repoId, laneIdx) => {
      const laneY = LANE_Y_START + laneIdx * LANE_Y_GAP;
      const theme = repoTheme[repoId] ?? REPO_THEMES[0];
      const nodesInRepo = grouped[repoId] ?? [];

      // compute levels for this repo using import edges
      const levels = computeLevelsForRepo(nodesInRepo, graph.edges);

      // group nodes by level
      const byLevel = new Map<number, GraphNode[]>();
      let maxLevel = 0;

      for (const n of nodesInRepo) {
        const l = levels.get(n.id) ?? 0;
        maxLevel = Math.max(maxLevel, l);
        if (!byLevel.has(l)) byLevel.set(l, []);
        byLevel.get(l)!.push(n);
      }

      // stable sort inside each level
      for (const [l, arr] of byLevel.entries()) arr.sort(byPath);

      // place: each level is a horizontal "row" inside the repo lane
      // if a level has too many nodes, wrap into subrows (still within same level band)
      for (let level = 0; level <= maxLevel; level++) {
        const arr = byLevel.get(level) ?? [];
        arr.forEach((n, i) => {
          const col = i % MAX_COLS_PER_LEVEL;
          const subRow = Math.floor(i / MAX_COLS_PER_LEVEL);

          const x = BASE_X + col * COL_W;
          const y = laneY + level * LEVEL_H + subRow * SUBROW_H;

          nodeElements.push({
            data: {
              id: n.id,
              label: n.label,
              kind: n.kind,
              repo: repoId,
              description: n.description ?? "",
              meta: n.meta ?? {},
              bgColor: theme.bg,
              borderColor: theme.border,
              textColor: theme.text,
            },
            position: { x, y },
          });
        });
      }
    });

    const edgeElements: ElementDefinition[] = graph.edges.map((e) => ({
      data: { id: e.id, source: e.source, target: e.target, kind: e.kind },
    }));

    return [...nodeElements, ...edgeElements];
  }, [graph.nodes, graph.edges, repoIds, repoTheme]);

  const selectNode = (node: any) => {
    const cy = cyRef.current;
    if (!cy || !node) return;

    cy.elements().removeClass("selected dimmed");
    node.addClass("selected");

    const neighborhood = node.closedNeighborhood();
    cy.elements().difference(neighborhood).addClass("dimmed");

    const repoId = node.data("repo") as string | undefined;
    const t = repoId ? repoTheme[repoId] : undefined;

    setSelected({
      id: node.data("id"),
      label: node.data("label"),
      kind: node.data("kind"),
      repo: repoId
        ? { id: repoId, label: repoLookup[repoId] ?? repoId, colorBg: t?.bg ?? "#E2E8F0", colorBorder: t?.border ?? "#334155" }
        : undefined,
      // ensure description from the original graph node is available separately
      meta: { ...(node.data("meta") ?? {}), description: node.data("description") ?? (node.data("meta")?.description ?? "") },
      description: node.data("description") ?? (node.data("meta")?.description ?? ""),
      neighbors: node.neighborhood("node").map((n: any) => n.data("label")),
      edges: node.connectedEdges().map((e: any) => {
        const s = e.source().data("label");
        const t2 = e.target().data("label");
        return `${e.data("kind")}: ${s} → ${t2}`;
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

          "shadow-opacity": 0.18,
          "shadow-blur": 8,
          "shadow-offset-x": 0,
          "shadow-offset-y": 4,
          "shadow-color": "rgba(15, 23, 42, 0.35)",

          "transition-property": "border-width, width, height, opacity, shadow-opacity, shadow-blur, shadow-offset-y",
          "transition-duration": 150,
        } as any,
      },
      {
        selector: "node.hovered",
        style: { "shadow-opacity": 0.32, "shadow-blur": 10, "shadow-offset-y": 6 } as any,
      },
      {
        selector: "node.selected",
        style: { "border-width": 3, width: 64, height: 64, opacity: 1 } as any,
      },
      { selector: "node.dimmed", style: { opacity: 0.22 } as any },

      // ✅ pravi uglovi
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

      { selector: 'edge[kind="import"]', style: { "line-style": "solid" } as any },
      {
        selector: 'edge[kind="http"]',
        style: { "line-style": "dashed", "line-color": "#0EA5E9", "target-arrow-color": "#0EA5E9" } as any,
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
    cy.zoom(cy.zoom() * 1.15);

    cy.on("tap", "node", (evt) => selectNode(evt.target));

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      node.addClass("hovered");

      const repoId = node.data("repo") as string | undefined;
      setHovered({
        id: node.data("id"),
        label: node.data("label"),
        repoId,
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
  }, [elements, repoLookup, repoTheme, layoutPadding]);

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
    cy.animate({ zoom: cy.zoom() * 1.15 }, { duration: 160, easing: "ease-out" as any });
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
                <span
                  className="inline-block h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: hovered.repoId ? repoTheme[hovered.repoId]?.border : "#334155" }}
                />
                <div className="font-semibold text-foreground">{hovered.label}</div>
              </div>
              {hovered.repoLabel && <div className="text-muted-foreground mt-0.5">{hovered.repoLabel}</div>}
              <div className="text-muted-foreground mt-1 leading-snug max-h-20 overflow-hidden text-ellipsis">{hovered.id}</div>
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

          {/* Legend */}
          <div className="absolute right-3 bottom-3 z-10">
            <div className="bg-background/90 border border-border rounded-xl p-3 shadow-sm backdrop-blur">
              <p className="text-xs font-medium text-muted-foreground mb-2">Repos</p>
              <div className="flex flex-wrap gap-2">
                {repoIds.map((repoId) => {
                  const c = repoTheme[repoId] ?? REPO_THEMES[0];
                  return (
                    <div key={repoId} className="flex items-center gap-2 px-2 py-1 rounded-md text-xs font-medium" style={{ backgroundColor: c.bg, color: "#0B1220" }}>
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: c.border }} />
                      {repoLookup[repoId] ?? repoId}
                    </div>
                  );
                })}
                {!repoIds.length && <div className="text-xs text-muted-foreground">No repos</div>}
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
                  <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: selected.repo?.colorBorder ?? "#334155" }} />
                  <div className="font-mono text-sm font-medium">{selected.label}</div>
                </div>

                <div className="text-xs text-muted-foreground font-mono break-words">{selected.id}</div>
                <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{selected.kind}</div>

                {selected.repo && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: selected.repo.colorBg }} />
                    <span className="font-medium">{selected.repo.label}</span>
                  </div>
                )}
              </div>

              {selected.description && selected.description.trim() !== "" && (
                <div>
                  <div className="text-xs font-medium mb-1">Description</div>
                  <div className="text-sm text-muted-foreground whitespace-pre-wrap">{selected.description}</div>
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
