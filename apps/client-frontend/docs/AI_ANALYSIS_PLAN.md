# Plano de Melhoria da Inteligência para Análise de Editais

Este documento descreve as etapas para evoluir a análise de documentos, visando identificar riscos e irregularidades conforme solicitado.

## 1. Processamento de PDFs Pesados

1. **Extração página a página**
   - Utilizar bibliotecas como **pdf-parse** no ambiente de backend para extrair texto de cada página separadamente.
   - Permitir o envio segmentado para modelos de IA, reduzindo o impacto de limites de tokens.
2. **Pré-processamento**
   - Normalizar acentuação e pontuação.
   - Remover páginas repetidas ou em branco.

## 2. Análise Nativa Aprimorada

1. **Atualização do script `pdfAnalyzer.ts`**
   - Garantir que cada ponto a seguir seja verificado:
     - 1.1 Natureza do leilão (judicial/extrajudicial).
     - 1.2 Publicação correta no Diário Oficial e jornal.
     - 1.3 Intimação do executado conforme CPC art. 889, I.
     - 1.4 Intimação dos demais interessados (art. 889, II-VIII).
     - 1.5 Valores mínimos e comparação com avaliação (alerta se < 50%).
     - 1.6 Existência de débitos (IPTU, condomínio, hipotecas).
     - 1.7 Situação de ocupação do imóvel.
     - 1.8 Restrições legais ou judiciais.
   - Registrar em qual página cada evidência foi encontrada.
2. **Geração de sumário**
   - Informar número total de alertas e páginas afetadas.

## 3. Integração com Modelos de IA

1. **APIs suportadas**
   - OpenAI, Anthropic e Mistral.
   - Utilizar prompts específicos para cada ponto de verificação.
2. **Fluxo sugerido**
   - Dividir o texto por página ou por blocos de até 2.000 caracteres.
   - Enviar cada bloco ao modelo escolhido com o prompt adequado.
   - Consolidar as respostas em uma única estrutura de análise.
3. **Exemplo de Prompt**
   ```
   Você é um assistente jurídico. Analise o trecho a seguir do edital de leilão e responda:
   - Natureza do leilão (judicial/extrajudicial)
   - Confirmação de publicação (Diário Oficial e jornal)
   - Intimações exigidas pelo CPC art. 889
   - Valores mínimos e eventuais débitos
   - Ocupação do imóvel e restrições
   Responda em formato JSON.
   Trecho:
   "${TRECHO}"
   ```

## 4. Robo de Análise Próprio

1. **Orquestração**
   - Implementar fila de tarefas para processar documentos grandes sem travar a interface.
   - Armazenar resultados parciais (por página) e consolidar ao final.
2. **Monitoramento**
   - Registrar tempo de processamento e eventuais erros para ajuste dos prompts ou do parser.

## 5. Resultado Esperado

- Relatório detalhado com todos os itens de 1.1 a 1.8.
- Destaque de páginas com maior risco.
- Possibilidade de revisar cada página individualmente no aplicativo.

