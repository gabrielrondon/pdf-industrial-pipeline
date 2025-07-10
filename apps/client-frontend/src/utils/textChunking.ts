
interface ChunkResult {
  content: string;
  wordCount: number;
  startIndex: number;
  endIndex: string;
  pageStart?: number;
  pageEnd?: number;
}

export class TextChunker {
  private readonly targetWords: number;
  private readonly overlapWords: number;

  constructor(targetWords = 450, overlapWords = 50) {
    this.targetWords = targetWords;
    this.overlapWords = overlapWords;
  }

  /**
   * Chunk text into overlapping segments
   */
  chunkText(text: string, pageNumber?: number): ChunkResult[] {
    const words = text.split(/\s+/).filter(word => word.length > 0);
    const chunks: ChunkResult[] = [];
    
    let startIdx = 0;
    let chunkIndex = 0;

    while (startIdx < words.length) {
      // Calculate end index for this chunk
      const endIdx = Math.min(startIdx + this.targetWords, words.length);
      
      // Extract chunk content
      const chunkWords = words.slice(startIdx, endIdx);
      const content = chunkWords.join(' ');
      
      chunks.push({
        content,
        wordCount: chunkWords.length,
        startIndex: startIdx,
        endIndex: `${endIdx - 1}`,
        pageStart: pageNumber,
        pageEnd: pageNumber
      });

      // Move start index forward, accounting for overlap
      // If this is the last chunk, break
      if (endIdx >= words.length) break;
      
      startIdx = endIdx - this.overlapWords;
      chunkIndex++;
    }

    return chunks;
  }

  /**
   * Chunk multiple pages with cross-page overlap
   */
  chunkPages(pages: { content: string; pageNumber: number }[]): ChunkResult[] {
    const allChunks: ChunkResult[] = [];
    
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const pageChunks = this.chunkText(page.content, page.pageNumber);
      
      // Add cross-page overlap if not the last page
      if (i < pages.length - 1) {
        const nextPage = pages[i + 1];
        const crossPageText = this.createCrossPageChunk(page.content, nextPage.content);
        
        if (crossPageText.wordCount >= this.overlapWords) {
          allChunks.push({
            ...crossPageText,
            pageStart: page.pageNumber,
            pageEnd: nextPage.pageNumber,
            startIndex: allChunks.length,
            endIndex: `cross-page-${i}-${i + 1}`
          });
        }
      }
      
      allChunks.push(...pageChunks);
    }

    return allChunks;
  }

  private createCrossPageChunk(page1: string, page2: string): Omit<ChunkResult, 'startIndex' | 'endIndex' | 'pageStart' | 'pageEnd'> {
    const words1 = page1.split(/\s+/).filter(word => word.length > 0);
    const words2 = page2.split(/\s+/).filter(word => word.length > 0);
    
    // Take last part of page1 and first part of page2
    const take1 = Math.min(this.overlapWords, words1.length);
    const take2 = Math.min(this.overlapWords, words2.length);
    
    const chunk1 = words1.slice(-take1);
    const chunk2 = words2.slice(0, take2);
    
    const combinedWords = [...chunk1, ...chunk2];
    
    return {
      content: combinedWords.join(' '),
      wordCount: combinedWords.length
    };
  }

  /**
   * Validate chunk quality
   */
  validateChunk(chunk: ChunkResult): boolean {
    // Check minimum word count
    if (chunk.wordCount < 10) return false;
    
    // Check for reasonable text structure
    const sentences = chunk.content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    if (sentences.length === 0) return false;
    
    // Check character to word ratio (filter out tables/lists)
    const avgWordsPerSentence = chunk.wordCount / sentences.length;
    if (avgWordsPerSentence < 2) return false;
    
    return true;
  }
}

export const defaultChunker = new TextChunker();
