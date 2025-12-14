import { useEffect, useState } from "react";
import { Project } from "@/types/project";
import { getSumarry, getKeyPoints, getWhoUses } from "@/services/api.service";

interface OverviewTabProps {
  project: Project;
}

const linesToList = (text: string) =>
  text
    .split("\n")
    .map((l) => l.replace(/^[-•\d.)\s]+/, "").trim())
    .filter(Boolean);

const OverviewTab = ({ project }: OverviewTabProps) => {
  const [summary, setSummary] = useState("");
  const [keyPoints, setKeyPoints] = useState<string[]>([]);
  const [whoUses, setWhoUses] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setLoading(true);
        setError(null);

        const summaryData = await getSumarry();
        if (!cancelled) setSummary(summaryData?.summary ?? "");

        const kpText = await getKeyPoints();
        if (!cancelled) setKeyPoints(linesToList(kpText));

        const whoText = await getWhoUses();
        if (!cancelled) setWhoUses(linesToList(whoText));
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load overview");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="animate-fade-in space-y-8">
      {/* WHAT IS THIS */}
      <section>
        <h2 className="text-lg font-medium mb-3">What is this?</h2>
        <p className="text-muted-foreground leading-relaxed">
          {project.description}
        </p>

        <div className="mt-4 rounded-lg border border-border bg-card p-4">
          <div className="text-sm font-medium mb-2">System Summary</div>

          {loading && (
            <div className="text-sm text-muted-foreground">
              Generating summary…
            </div>
          )}

          {error && <div className="text-sm text-destructive">{error}</div>}

          {!loading && !error && (
            <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
              {summary || "No summary available."}
            </p>
          )}
        </div>
      </section>

      {/* KEY POINTS */}
      <section>
        <h2 className="text-lg font-medium mb-3">Key Points</h2>

        {loading && (
          <div className="text-sm text-muted-foreground">
            Generating key points…
          </div>
        )}

        {!loading && !error && keyPoints.length > 0 && (
          <ul className="space-y-2 text-muted-foreground">
            {keyPoints.map((point, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* WHO USES THIS */}
      <section>
        <h2 className="text-lg font-medium mb-3">Who Uses This</h2>

        {loading && (
          <div className="text-sm text-muted-foreground">
            Generating user groups…
          </div>
        )}

        {!loading && !error && whoUses.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {whoUses.map((team) => (
              <span
                key={team}
                className="inline-flex items-center rounded-full bg-secondary px-3 py-1 text-sm text-secondary-foreground"
              >
                {team}
              </span>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default OverviewTab;
