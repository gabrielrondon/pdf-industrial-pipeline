#!/usr/bin/env node

/**
 * 🔍 Architecture Linter - Detecta violações de arquitetura
 * Evita uso incorreto entre Railway API e Supabase
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Padrões que indicam violações de arquitetura
const ARCHITECTURE_VIOLATIONS = [
  {
    pattern: /SupabaseService\.uploadDocument/g,
    error: '❌ VIOLAÇÃO: SupabaseService.uploadDocument() está DEPRECATED. Use railwayApi.uploadDocument()',
    severity: 'error'
  },
  {
    pattern: /SupabaseService\.saveDocumentAnalysis/g,
    error: '❌ VIOLAÇÃO: SupabaseService.saveDocumentAnalysis() está DEPRECATED. Use Railway API',
    severity: 'error'
  },
  {
    pattern: /supabase\.from\(['"`]documents['"`]\)/g,
    error: '⚠️ AVISO: Acesso direto à tabela Supabase "documents" está deprecated',
    severity: 'warning'
  },
  {
    pattern: /supabase\.from\(['"`]analysis_points['"`]\)/g,
    error: '⚠️ AVISO: Acesso direto à tabela Supabase "analysis_points" está deprecated',
    severity: 'warning'
  },
  {
    pattern: /import.*railwayApi.*supabase/g,
    error: '🔄 REVISÃO: Arquivo mistura Railway API e Supabase - verificar responsabilidades',
    severity: 'info'
  }
];

// Padrões corretos que devem ser encorajados
const GOOD_PATTERNS = [
  {
    pattern: /railwayApi\.uploadDocument/g,
    message: '✅ BOM: Usando Railway API para upload'
  },
  {
    pattern: /getUserDocuments.*Railway API/g,
    message: '✅ BOM: Buscando documentos via Railway API'
  }
];

function lintFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const violations = [];
    const goodPractices = [];

    // Verificar violações
    ARCHITECTURE_VIOLATIONS.forEach(({ pattern, error, severity }) => {
      const matches = content.match(pattern);
      if (matches) {
        matches.forEach(match => {
          const lines = content.substring(0, content.indexOf(match)).split('\n');
          const lineNumber = lines.length;
          violations.push({
            file: filePath,
            line: lineNumber,
            error,
            severity,
            match
          });
        });
      }
    });

    // Verificar boas práticas
    GOOD_PATTERNS.forEach(({ pattern, message }) => {
      const matches = content.match(pattern);
      if (matches) {
        goodPractices.push({
          file: filePath,
          message,
          count: matches.length
        });
      }
    });

    return { violations, goodPractices };
  } catch (error) {
    console.error(`Erro ao ler arquivo ${filePath}:`, error.message);
    return { violations: [], goodPractices: [] };
  }
}

function runLint() {
  console.log('🔍 Executando Architecture Linter...\n');

  // Buscar arquivos TypeScript/JavaScript no frontend
  const files = glob.sync('apps/client-frontend/src/**/*.{ts,tsx,js,jsx}', {
    ignore: ['**/node_modules/**', '**/dist/**', '**/build/**']
  });

  let totalViolations = 0;
  let totalWarnings = 0;
  let totalGoodPractices = 0;

  files.forEach(file => {
    const { violations, goodPractices } = lintFile(file);
    
    if (violations.length > 0) {
      console.log(`📁 ${file}:`);
      violations.forEach(({ line, error, severity, match }) => {
        const icon = severity === 'error' ? '❌' : severity === 'warning' ? '⚠️' : 'ℹ️';
        console.log(`  ${icon} Linha ${line}: ${error}`);
        console.log(`     Código: ${match.trim()}`);
        
        if (severity === 'error') totalViolations++;
        if (severity === 'warning') totalWarnings++;
      });
      console.log('');
    }

    totalGoodPractices += goodPractices.length;
  });

  // Relatório final
  console.log('📊 RELATÓRIO FINAL:');
  console.log(`❌ Erros críticos: ${totalViolations}`);
  console.log(`⚠️ Avisos: ${totalWarnings}`);
  console.log(`✅ Boas práticas encontradas: ${totalGoodPractices}`);

  if (totalViolations > 0) {
    console.log('\n🚨 AÇÃO REQUERIDA: Corrija os erros críticos antes de continuar!');
    process.exit(1);
  } else if (totalWarnings > 0) {
    console.log('\n⚠️ Avisos encontrados. Considere revisar o código.');
  } else {
    console.log('\n🎉 Nenhuma violação de arquitetura encontrada!');
  }
}

// Verificar se está sendo executado diretamente
if (require.main === module) {
  runLint();
}

module.exports = { lintFile, runLint, ARCHITECTURE_VIOLATIONS };