import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Welcome = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
      {/* Gradient + blob backdrop */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,#c6fbc2,transparent_35%),radial-gradient(circle_at_80%_20%,#dedefe,transparent_35%),radial-gradient(circle_at_40%_80%,#e5e7eb,transparent_30%)] blur-[1px]" />
        <div
          className="absolute h-72 w-72 rounded-full bg-[#69FF47]/20 blur-3xl"
          style={{ top: "14%", left: "8%", animation: "float 8s ease-in-out infinite" }}
        />
        <div
          className="absolute h-80 w-80 rounded-full bg-[#dedefe]/30 blur-3xl"
          style={{ top: "46%", right: "6%", animation: "float 9s ease-in-out infinite" }}
        />
      </div>

      {/* Hero */}
      <main className="relative z-10 mx-auto flex max-w-[1600px] flex-col items-center text-center gap-8 px-8 py-24">
        <div className="flex items-center gap-3 animate-fade-in">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#69FF47] text-white shadow-sm animate-bounce">
            <svg
              className="h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
          </div>
          <span className="text-2xl font-semibold">CodeAtlas</span>
        </div>

        <div className="space-y-6 max-w-3xl animate-fade-in">
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Map your codebase and understand connections at a glance.
          </h1>
          <p className="text-lg text-muted-foreground leading-relaxed">
            Interactive system graphs, ownership clarity, and instant insights into how services, repos, and files relate.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Button size="lg" className="bg-[#69FF47] text-slate-900 hover:bg-[#52e32f]" onClick={() => navigate("/signup")}>
              Create free account
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate("/login")}>
              Sign in
            </Button>
          </div>
        </div>
      </main>

      
    </div>
  );
};

export default Welcome;
