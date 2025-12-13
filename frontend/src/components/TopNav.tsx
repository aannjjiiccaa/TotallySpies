import { ArrowLeft } from "lucide-react";
import { mockUser } from "@/data/mockData";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

interface TopNavProps {
  onBack?: () => void;
  backLabel?: string;
}

const TopNav = ({ onBack, backLabel = "Back" }: TopNavProps) => {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-[1600px] items-center px-6">
        <div className="flex items-center gap-3">
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              {backLabel}
            </button>
          )}

          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#69FF47] text-white shadow-sm">
              <svg
                className="h-4 w-4 text-white"
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
            <span className="font-semibold">CodeAtlas</span>
          </div>
        </div>

        <div className="flex items-center gap-3 ml-auto">
          <span className="hidden sm:inline text-sm text-muted-foreground">{mockUser.email}</span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div
                className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-sm font-medium text-secondary-foreground cursor-pointer"
                title="Account menu"
              >
                {mockUser.name.charAt(0)}
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
