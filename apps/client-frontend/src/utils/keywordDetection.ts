/**
 * Utilitários para detecção de palavras-chave importantes em documentos judiciais
 * Baseado nas sugestões do Pedro sobre [Edital] e [Laudo]
 */

export interface KeywordMatch {
  word: string;
  type: 'edital' | 'laudo' | 'prazo' | 'contato';
  importance: 'high' | 'medium' | 'low';
  description: string;
  color: string;
}

export const JUDICIAL_KEYWORDS: Record<string, KeywordMatch> = {
  // Palavras-chave principais identificadas pelo Pedro
  'edital': {
    word: 'Edital',
    type: 'edital',
    importance: 'high',
    description: 'Documento oficial do leilão',
    color: 'bg-blue-100 text-blue-800'
  },
  'laudo': {
    word: 'Laudo',
    type: 'laudo',
    importance: 'high', 
    description: 'Avaliação técnica do bem',
    color: 'bg-green-100 text-green-800'
  },
  
  // Palavras relacionadas a prazos (6 meses conforme Pedro)
  'prazo': {
    word: 'Prazo',
    type: 'prazo',
    importance: 'high',
    description: 'Prazo processual importante',
    color: 'bg-orange-100 text-orange-800'
  },
  'meses': {
    word: 'meses',
    type: 'prazo',
    importance: 'medium',
    description: 'Período temporal',
    color: 'bg-yellow-100 text-yellow-800'
  },
  'dias': {
    word: 'dias',
    type: 'prazo',
    importance: 'medium',
    description: 'Período temporal',
    color: 'bg-yellow-100 text-yellow-800'
  },
  
  // Palavras relacionadas a contatos/comunicação
  'contato': {
    word: 'Contato',
    type: 'contato',
    importance: 'medium',
    description: 'Informação de contato',
    color: 'bg-purple-100 text-purple-800'
  },
  'comunicação': {
    word: 'Comunicação',
    type: 'contato',
    importance: 'medium',
    description: 'Comunicação processual',
    color: 'bg-purple-100 text-purple-800'
  },
  'intimação': {
    word: 'Intimação',
    type: 'contato',
    importance: 'high',
    description: 'Intimação judicial',
    color: 'bg-red-100 text-red-800'
  }
};

/**
 * Detecta palavras-chave importantes em um texto
 */
export function detectKeywords(text: string): KeywordMatch[] {
  const foundKeywords: KeywordMatch[] = [];
  const normalizedText = text.toLowerCase();
  
  Object.keys(JUDICIAL_KEYWORDS).forEach(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
    if (regex.test(normalizedText)) {
      foundKeywords.push(JUDICIAL_KEYWORDS[keyword]);
    }
  });
  
  // Remove duplicados e ordena por importância
  const uniqueKeywords = foundKeywords.filter((keyword, index, self) => 
    index === self.findIndex(k => k.word === keyword.word)
  );
  
  return uniqueKeywords.sort((a, b) => {
    const importanceOrder = { high: 3, medium: 2, low: 1 };
    return importanceOrder[b.importance] - importanceOrder[a.importance];
  });
}

/**
 * Destaca palavras-chave em um texto HTML-safe
 */
export function highlightKeywords(text: string): string {
  let highlightedText = text;
  
  Object.keys(JUDICIAL_KEYWORDS).forEach(keyword => {
    const keywordInfo = JUDICIAL_KEYWORDS[keyword];
    const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
    
    highlightedText = highlightedText.replace(regex, (match) => {
      return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${keywordInfo.color} mx-1" title="${keywordInfo.description}">${match}</span>`;
    });
  });
  
  return highlightedText;
}

/**
 * Analisa um documento completo e retorna insights sobre palavras-chave
 */
export function analyzeDocument(content: string): {
  keywords: KeywordMatch[];
  hasEdital: boolean;
  hasLaudo: boolean;
  riskLevel: 'low' | 'medium' | 'high';
  suggestions: string[];
} {
  const keywords = detectKeywords(content);
  const hasEdital = keywords.some(k => k.type === 'edital');
  const hasLaudo = keywords.some(k => k.type === 'laudo');
  
  // Determina nível de risco baseado nas palavras-chave encontradas
  let riskLevel: 'low' | 'medium' | 'high' = 'low';
  const highImportanceCount = keywords.filter(k => k.importance === 'high').length;
  
  if (highImportanceCount >= 2) {
    riskLevel = 'high';
  } else if (highImportanceCount >= 1) {
    riskLevel = 'medium';
  }
  
  // Gera sugestões baseadas no que foi encontrado
  const suggestions: string[] = [];
  
  if (hasEdital) {
    suggestions.push('📋 Documento contém edital - revisar condições do leilão');
  }
  
  if (hasLaudo) {
    suggestions.push('🏠 Laudo encontrado - verificar avaliação do bem');
  }
  
  if (keywords.some(k => k.type === 'prazo')) {
    suggestions.push('⏰ Prazos identificados - criar lembretes (conforme prazo de 6 meses)');
  }
  
  if (keywords.some(k => k.type === 'contato')) {
    suggestions.push('📞 Informações de contato - organizar acompanhamentos repetidos');
  }
  
  if (!hasEdital && !hasLaudo) {
    suggestions.push('🔍 Documento não parece ser edital ou laudo - verificar tipo');
  }
  
  return {
    keywords,
    hasEdital,
    hasLaudo,
    riskLevel,
    suggestions
  };
}