
interface AnalysisPoint {
  id: string;
  title: string;
  comment: string;
  status: 'confirmado' | 'alerta' | 'não identificado';
  type: string;
  category: string;
  value?: string | null;
  priority: 'high' | 'medium' | 'low';
  legal_reference?: string | null;
  page?: number;
}

interface NativeAnalysisResult {
  points: AnalysisPoint[];
  summary: string;
  totalLeads: number;
  categories: string[];
  analyzer: 'native';
}

export class PDFAnalyzer {
  private static readonly LEGAL_REFERENCES = {
    CPC_889: 'CPC art. 889',
    CPC_889_I: 'CPC art. 889, I',
    CPC_889_II_VIII: 'CPC art. 889, II-VIII',
    LEI_8245: 'Lei 8.245/91',
    CC_1228: 'CC art. 1.228'
  };

  private static readonly KEYWORDS = {
    LEILAO: ['leilão', 'hasta pública', 'arrematação', 'praça'],
    JUDICIAL: ['judicial', 'execução', 'processo', 'juízo', 'vara'],
    EXTRAJUDICIAL: ['extrajudicial', 'cartório', 'tabelião', 'notas'],
    INTIMACAO: ['intimação', 'citação', 'notificação', 'edital'],
    DEBITOS: ['débito', 'iptu', 'condomínio', 'hipoteca', 'financiamento'],
    OCUPACAO: ['ocupado', 'inquilino', 'locação', 'posse', 'posseiro'],
    VALORES: ['avaliação', 'lance', 'praça', 'valor', 'preço'],
    PUBLICACAO: ['diário oficial', 'publicação', 'edital', 'jornal']
  };

  static analyzeText(text: string, fileName: string): NativeAnalysisResult {
    const normalizedText = this.normalizeText(text);
    const points: AnalysisPoint[] = [];
    
    // Análise da natureza do leilão
    points.push(...this.analyzeAuctionNature(normalizedText));
    
    // Análise de publicação
    points.push(...this.analyzePublication(normalizedText));
    
    // Análise de intimações
    points.push(...this.analyzeIntimations(normalizedText));
    
    // Análise de valores
    points.push(...this.analyzeValues(normalizedText));
    
    // Análise de débitos
    points.push(...this.analyzeDebts(normalizedText));
    
    // Análise de ocupação
    points.push(...this.analyzeOccupation(normalizedText));
    
    // Análise de restrições
    points.push(...this.analyzeRestrictions(normalizedText));
    
    // Análise de prazos
    points.push(...this.analyzeDeadlines(normalizedText));

    const categories = [...new Set(points.map(p => p.category))];
    
    return {
      points,
      summary: this.generateSummary(points, fileName),
      totalLeads: points.length,
      categories,
      analyzer: 'native'
    };
  }

  static analyzePages(pages: string[], fileName: string): NativeAnalysisResult {
    const allPoints: AnalysisPoint[] = [];
    pages.forEach((pageText, index) => {
      const result = this.analyzeText(pageText, fileName);
      result.points.forEach(p => p.page = index + 1);
      allPoints.push(...result.points);
    });
    const categories = [...new Set(allPoints.map(p => p.category))];
    return {
      points: allPoints,
      summary: this.generateSummary(allPoints, fileName),
      totalLeads: allPoints.length,
      categories,
      analyzer: 'native'
    };
  }

  private static normalizeText(text: string): string {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  private static containsKeywords(text: string, keywords: string[]): boolean {
    return keywords.some(keyword => text.includes(keyword.toLowerCase()));
  }

  private static analyzeAuctionNature(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    if (this.containsKeywords(text, this.KEYWORDS.JUDICIAL)) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Leilão Judicial Identificado',
        comment: 'Documento identificado como edital de leilão judicial. Verifique se todos os requisitos legais foram cumpridos.',
        status: 'confirmado',
        type: 'procedural',
        category: 'leilao',
        priority: 'medium',
        legal_reference: this.LEGAL_REFERENCES.CPC_889
      });
    } else if (this.containsKeywords(text, this.KEYWORDS.EXTRAJUDICIAL)) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Leilão Extrajudicial Identificado',
        comment: 'Leilão extrajudicial identificado. Verifique procedimentos específicos do cartório.',
        status: 'confirmado',
        type: 'procedural',
        category: 'leilao',
        priority: 'medium'
      });
    }

    return points;
  }

  private static analyzePublication(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    if (this.containsKeywords(text, ['diario oficial'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Publicação no Diário Oficial',
        comment: 'Encontrada referência à publicação no Diário Oficial. Verifique se os prazos legais foram respeitados.',
        status: 'confirmado',
        type: 'procedural',
        category: 'publicacao',
        priority: 'medium'
      });
    } else {
      points.push({
        id: crypto.randomUUID(),
        title: 'Verificar Publicação no Diário Oficial',
        comment: 'Não foi encontrada menção clara à publicação no Diário Oficial. Isso pode ser um risco para a validade do leilão.',
        status: 'alerta',
        type: 'risk',
        category: 'publicacao',
        priority: 'high'
      });
    }

    if (this.containsKeywords(text, ['jornal', 'grande circulacao'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Publicação em Jornal',
        comment: 'Encontrada referência à publicação em jornal de grande circulação.',
        status: 'confirmado',
        type: 'procedural',
        category: 'publicacao',
        priority: 'low'
      });
    }

    return points;
  }

  private static analyzeIntimations(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    if (this.containsKeywords(text, ['intimacao', 'executado'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Intimação do Executado',
        comment: 'Encontrada referência à intimação do executado. Verifique se foi realizada conforme o CPC.',
        status: 'confirmado',
        type: 'procedural',
        category: 'intimacao',
        priority: 'medium',
        legal_reference: this.LEGAL_REFERENCES.CPC_889_I
      });
    } else {
      points.push({
        id: crypto.randomUUID(),
        title: 'Verificar Intimação do Executado',
        comment: 'Não foi encontrada menção clara à intimação do executado. Isso é obrigatório pelo CPC art. 889, I.',
        status: 'alerta',
        type: 'risk',
        category: 'intimacao',
        priority: 'high',
        legal_reference: this.LEGAL_REFERENCES.CPC_889_I
      });
    }

    return points;
  }

  private static analyzeValues(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    // Buscar valores monetários
    const valueRegex = /r\$\s*[\d.,]+/gi;
    const values = text.match(valueRegex);
    
    if (values && values.length >= 2) {
      const numericValues = values.map(v => {
        return parseFloat(v.replace(/[^\d,]/g, '').replace(',', '.'));
      }).filter(v => !isNaN(v) && v > 0);

      if (numericValues.length >= 2) {
        const minValue = Math.min(...numericValues);
        const maxValue = Math.max(...numericValues);
        
        if (minValue < maxValue * 0.5) {
          points.push({
            id: crypto.randomUUID(),
            title: 'Valor Abaixo de 50% da Avaliação',
            comment: `Identificado valor de arrematação significativamente abaixo da avaliação. Isso pode gerar pedido de anulação do leilão.`,
            status: 'alerta',
            type: 'risk',
            category: 'avaliacao',
            priority: 'high',
            value: `Menor valor: R$ ${minValue.toLocaleString('pt-BR')}`
          });
        }
      }
    }

    if (this.containsKeywords(text, ['primeira praca', '1a praca'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Primeira Praça Identificada',
        comment: 'Encontrada referência à primeira praça do leilão.',
        status: 'confirmado',
        type: 'financial',
        category: 'avaliacao',
        priority: 'low'
      });
    }

    return points;
  }

  private static analyzeDebts(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    if (this.containsKeywords(text, ['iptu'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Débitos de IPTU Mencionados',
        comment: 'Encontrada menção a débitos de IPTU. Verifique se serão quitados pelo valor da arrematação ou se são de responsabilidade do arrematante.',
        status: 'alerta',
        type: 'financial',
        category: 'debitos',
        priority: 'medium'
      });
    }

    if (this.containsKeywords(text, ['condominio'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Débitos Condominiais',
        comment: 'Encontrada menção a débitos condominiais. Verifique a responsabilidade do arrematante.',
        status: 'alerta',
        type: 'financial',
        category: 'debitos',
        priority: 'medium'
      });
    }

    if (this.containsKeywords(text, ['hipoteca', 'financiamento'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Garantias Reais Identificadas',
        comment: 'Encontradas referências a hipoteca ou financiamento. Verifique se serão quitadas com o valor da arrematação.',
        status: 'alerta',
        type: 'financial',
        category: 'debitos',
        priority: 'high'
      });
    }

    return points;
  }

  private static analyzeOccupation(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    if (this.containsKeywords(text, ['ocupado', 'inquilino'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Imóvel Ocupado',
        comment: 'O imóvel aparenta estar ocupado. Isso pode gerar dificuldades para a imissão na posse.',
        status: 'alerta',
        type: 'risk',
        category: 'ocupacao',
        priority: 'high',
        legal_reference: this.LEGAL_REFERENCES.LEI_8245
      });
    }

    if (this.containsKeywords(text, ['posseiro', 'posse'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Questões de Posse',
        comment: 'Encontradas referências a questões de posse. Verifique disputas que possam afetar a arrematação.',
        status: 'alerta',
        type: 'risk',
        category: 'ocupacao',
        priority: 'high'
      });
    }

    return points;
  }

  private static analyzeRestrictions(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    if (this.containsKeywords(text, ['indisponibilidade', 'restricao judicial'])) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Restrições Judiciais',
        comment: 'Encontradas menções a restrições ou indisponibilidade judicial. Isso pode afetar a transferência do imóvel.',
        status: 'alerta',
        type: 'risk',
        category: 'risco',
        priority: 'high'
      });
    }

    return points;
  }

  private static analyzeDeadlines(text: string): AnalysisPoint[] {
    const points: AnalysisPoint[] = [];
    
    // Buscar datas
    const dateRegex = /\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}\s+de\s+\w+\s+de\s+\d{4}/gi;
    const dates = text.match(dateRegex);
    
    if (dates && dates.length > 0) {
      points.push({
        id: crypto.randomUUID(),
        title: 'Prazos Identificados',
        comment: `Encontradas ${dates.length} datas no documento. Verifique se todos os prazos legais estão sendo respeitados.`,
        status: 'confirmado',
        type: 'procedural',
        category: 'prazo',
        priority: 'medium'
      });
    }

    return points;
  }

  private static generateSummary(points: AnalysisPoint[], fileName: string): string {
    const alertCount = points.filter(p => p.status === 'alerta').length;
    const confirmedCount = points.filter(p => p.status === 'confirmado').length;
    const highPriorityCount = points.filter(p => p.priority === 'high').length;
    const uniquePages = [...new Set(points.map(p => p.page).filter(Boolean))].length;

    return `Análise nativa concluída para ${fileName}. Encontrados ${points.length} pontos relevantes em ${uniquePages} página(s): ${confirmedCount} confirmados e ${alertCount} alertas. ${highPriorityCount} itens requerem atenção prioritária. Análise focada em requisitos legais para leilões judiciais.`;
  }
}
