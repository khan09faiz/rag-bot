import { createClient } from '@supabase/supabase-js';
import type { Document, RetrievalResult } from '@/types';

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

export class SupabaseVectorStore {
  async insertDocuments(documents: Omit<Document, 'id' | 'created_at' | 'updated_at'>[]): Promise<void> {
    const { error } = await supabase
      .from('documents')
      .insert(documents);

    if (error) {
      throw new Error(`Failed to insert documents: ${error.message}`);
    }
  }

  async similaritySearch(
    embedding: number[],
    topK: number = 20,
    threshold: number = 0.7
  ): Promise<RetrievalResult[]> {
    const { data, error } = await supabase.rpc('similarity_search', {
      query_embedding: embedding,
      match_threshold: threshold,
      match_count: topK
    });

    if (error) {
      throw new Error(`Similarity search failed: ${error.message}`);
    }

    return data.map((item: any) => ({
      document: {
        id: item.id,
        content: item.content,
        metadata: item.metadata,
        created_at: item.created_at,
        updated_at: item.updated_at
      },
      similarity: item.similarity
    }));
  }
}

// Add this function to Supabase via SQL
/*
CREATE OR REPLACE FUNCTION similarity_search(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  created_at timestamptz,
  updated_at timestamptz,
  similarity float
)
LANGUAGE sql
AS $$
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    documents.created_at,
    documents.updated_at,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;
*/