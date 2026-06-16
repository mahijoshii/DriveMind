export type User = {
  id: number;
  email: string;
  name?: string | null;
};

export type IndexStatus = {
  status: string;
  message: string;
  total: number;
  processed: number;
};

export type DocumentItem = {
  id: number;
  title: string;
  web_url: string;
  indexed_at: string;
};

export type Citation = {
  document_title: string;
  document_url: string;
  excerpt: string;
  score: number;
};

export type QueryResponse = {
  answer: string;
  citations: Citation[];
};
