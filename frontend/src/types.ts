export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

export interface Health {
  status: string;
  database: string;
  version: string;
}
