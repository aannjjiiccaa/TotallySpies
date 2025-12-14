export interface Repository {
  id: string;
  name: string;
  type: 'backend' | 'frontend' | 'infra' | 'library';
  url: string;
  responsibility: string;
  dependsOn: string[];
  usedBy: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  techStack: string[];
  repositories: Repository[];
  lastUpdated: string;
  collaborators: string[];
  // optional graph returned from backend when creating/importing a project
  graph?: {
    nodes: Array<{ id: string; name?: string; repo?: string }>;
    edges?: Array<{ id?: string; from: string; to: string; type?: string }>;
  } | null;
}

export interface User {
  id: string;
  email: string;
  name: string;
}
