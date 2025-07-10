export async function extractTextByPage(arrayBuffer: ArrayBuffer): Promise<string[]> {
  const pdfParse = (await import('pdf-parse')).default;
  const pageTexts: string[] = [];
  await pdfParse(Buffer.from(arrayBuffer), {
    pagerender: (pageData: any) => {
      return pageData.getTextContent().then((textContent: any) => {
        const pageText = textContent.items.map((item: any) => item.str).join(' ');
        pageTexts.push(pageText);
        return '';
      });
    },
  });
  return pageTexts;
}

export function chunkText(text: string, size: number = 2000): string[] {
  const chunks: string[] = [];
  for (let i = 0; i < text.length; i += size) {
    chunks.push(text.slice(i, i + size));
  }
  return chunks;
}
