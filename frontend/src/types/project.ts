export interface Repository {
  id: string;
  name: string;
  type: 'backend' | 'frontend' | 'infra' | 'library';
  url: string;
  responsibility: string;
  dependsOn: string[];
  usedBy: string[];
}

export interface Flow {
  id: string;
  name: string;
  description: string;
  steps: {
    step: number;
    action: string;
    service: string;
  }[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  techStack: string[];
  repositories: Repository[];
  flows: Flow[];
  lastUpdated: string;
  collaborators: string[];
}

export interface User {
  id: string;
  email: string;
  name: string;
}
