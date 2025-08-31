export interface Document {
  id: string;
  content: string;
  embedding?: number[];
  metadata: {
    source?: string;
    title?: string;
    section?: string;
    position?: number;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}

export interface Chunk {
  content: string;
  metadata: {
    source: string;
    title: string;
    section?: string;
    position: number;
  };
}

export interface RetrievalResult {
  document: Document;
  similarity: number;
  rerank_score?: number;
}

export interface QueryResponse {
  answer: string;
  citations: Array<{
    id: number;
    content: string;
    source: string;
    title: string;
    section?: string;
  }>;
  sources: Array<{
    title: string;
    source: string;
  }>;
  timings: {
    embedding: number;
    retrieval: number;
    reranking: number;
    generation: number;
    total: number;
  };
  token_estimate: number;
}

export interface UploadResponse {
  success: boolean;
  chunks_processed: number;
  message: string;
}