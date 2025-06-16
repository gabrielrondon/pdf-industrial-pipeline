#!/usr/bin/env python3
"""
Script para criar um PDF de teste com múltiplas páginas
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf(filename="test_document.pdf", num_pages=5):
    """
    Cria um PDF de teste com múltiplas páginas
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    for page in range(1, num_pages + 1):
        # Título da página
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 100, f"Página {page} de {num_pages}")
        
        # Conteúdo simulado
        c.setFont("Helvetica", 12)
        y = height - 150
        
        # Simular conteúdo de documento industrial
        content = [
            f"RELATÓRIO INDUSTRIAL - PÁGINA {page}",
            "",
            "1. INFORMAÇÕES GERAIS:",
            f"   • Data: Janeiro 2024",
            f"   • Seção: {page}/A-{page:03d}",
            f"   • Status: Processamento Pipeline",
            "",
            "2. DADOS TÉCNICOS:",
            f"   • Temperatura: {20 + page}°C",
            f"   • Pressão: {1000 + page * 10} Pa",
            f"   • Eficiência: {85 + page}%",
            "",
            "3. OBSERVAÇÕES:",
            f"   Esta é uma página de teste gerada automaticamente.",
            f"   Contém texto suficiente para análise OCR.",
            f"   Pipeline PDF Industrial - Etapa 1 Testing",
            "",
            "4. PRÓXIMOS PASSOS:",
            f"   • Dividir em páginas individuais",
            f"   • Analisar necessidade de OCR",
            f"   • Gerar manifest.json",
            f"   • Processar pipeline completo",
            "",
            "5. CONTATOS:",
            f"   Engenheiro: João Silva - joao@empresa.com",
            f"   Supervisor: Maria Santos - maria@empresa.com",
            f"   Telefone: (11) 9999-{page:04d}",
        ]
        
        for line in content:
            c.drawString(70, y, line)
            y -= 20
            if y < 100:  # Se não há espaço, parar
                break
        
        # Rodapé
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, f"PDF Industrial Pipeline - Teste | Página {page}")
        c.drawString(width - 150, 50, "Confidencial")
        
        # Nova página (exceto na última)
        if page < num_pages:
            c.showPage()
    
    c.save()
    print(f"✅ PDF criado: {filename} ({num_pages} páginas)")
    return filename

if __name__ == "__main__":
    # Criar PDF de teste
    pdf_file = create_test_pdf("test_document.pdf", 5)
    
    # Mostrar informações
    size = os.path.getsize(pdf_file)
    print(f"📄 Arquivo: {pdf_file}")
    print(f"📏 Tamanho: {size:,} bytes ({size/1024:.1f} KB)")
    print(f"📋 Pronto para testar o pipeline!") 