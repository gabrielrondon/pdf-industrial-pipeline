
interface EmbeddingResult {
  embedding: number[];
  usage: {
    prompt_tokens: number;
    total_tokens: number;
  };
}

export class EmbeddingGenerator {
  private readonly apiKey: string;
  private readonly model: string;
  private readonly batchSize: number;

  constructor(apiKey: string, model = 'text-embedding-3-small', batchSize = 100) {
    this.apiKey = apiKey;
    this.model = model;
    this.batchSize = batchSize;
  }

  /**
   * Generate embedding for a single text
   */
  async generateEmbedding(text: string): Promise<EmbeddingResult> {
    const response = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: this.model,
        input: text,
        encoding_format: 'float'
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`OpenAI API error: ${errorData.error?.message || response.statusText}`);
    }

    const data = await response.json();
    
    return {
      embedding: data.data[0].embedding,
      usage: data.usage
    };
  }

  /**
   * Generate embeddings for multiple texts in batches
   */
  async generateBatchEmbeddings(texts: string[]): Promise<EmbeddingResult[]> {
    const results: EmbeddingResult[] = [];
    
    for (let i = 0; i < texts.length; i += this.batchSize) {
      const batch = texts.slice(i, i + this.batchSize);
      
      const response = await fetch('https://api.openai.com/v1/embeddings', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.model,
          input: batch,
          encoding_format: 'float'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`OpenAI API error: ${errorData.error?.message || response.statusText}`);
      }

      const data = await response.json();
      
      // Map results back to individual embeddings
      const batchResults = data.data.map((item: any, index: number) => ({
        embedding: item.embedding,
        usage: {
          prompt_tokens: Math.floor(data.usage.prompt_tokens / batch.length),
          total_tokens: Math.floor(data.usage.total_tokens / batch.length)
        }
      }));
      
      results.push(...batchResults);
      
      // Rate limiting - wait between batches
      if (i + this.batchSize < texts.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    
    return results;
  }

  /**
   * Calculate cosine similarity between two embeddings
   */
  static cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Embeddings must have the same dimension');
    }

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  /**
   * Find most similar embeddings using cosine similarity
   */
  static findSimilar(
    queryEmbedding: number[], 
    embeddings: { id: string; embedding: number[]; metadata?: any }[], 
    topK = 5,
    threshold = 0.7
  ): Array<{ id: string; similarity: number; metadata?: any }> {
    const similarities = embeddings.map(item => ({
      id: item.id,
      similarity: this.cosineSimilarity(queryEmbedding, item.embedding),
      metadata: item.metadata
    }));

    return similarities
      .filter(item => item.similarity >= threshold)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, topK);
  }
}

/**
 * Fallback local embedding using simple TF-IDF approach
 */
export class LocalEmbeddingGenerator {
  private vocabulary: Map<string, number> = new Map();
  private documentFrequency: Map<string, number> = new Map();
  private totalDocuments = 0;

  /**
   * Build vocabulary from documents
   */
  buildVocabulary(documents: string[]): void {
    this.totalDocuments = documents.length;
    
    // Count word frequencies across all documents
    documents.forEach(doc => {
      const words = new Set(this.tokenize(doc));
      words.forEach(word => {
        this.documentFrequency.set(word, (this.documentFrequency.get(word) || 0) + 1);
      });
    });

    // Build vocabulary index
    Array.from(this.documentFrequency.keys()).forEach((word, index) => {
      this.vocabulary.set(word, index);
    });
  }

  /**
   * Generate simple TF-IDF vector
   */
  generateLocalEmbedding(text: string): number[] {
    const words = this.tokenize(text);
    const termFreq = new Map<string, number>();
    
    // Calculate term frequency
    words.forEach(word => {
      termFreq.set(word, (termFreq.get(word) || 0) + 1);
    });

    // Create TF-IDF vector
    const vector = new Array(this.vocabulary.size).fill(0);
    
    termFreq.forEach((tf, word) => {
      const vocabIndex = this.vocabulary.get(word);
      if (vocabIndex !== undefined) {
        const df = this.documentFrequency.get(word) || 1;
        const idf = Math.log(this.totalDocuments / df);
        vector[vocabIndex] = tf * idf;
      }
    });

    // Normalize vector
    const norm = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
    return norm > 0 ? vector.map(val => val / norm) : vector;
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2);
  }
}
