#!/usr/bin/env python3
"""
Cria um PDF com imagens que requer OCR para teste
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import os

def create_image_pdf(filename="test_image_document.pdf"):
    """
    Cria um PDF com imagens que necessitam de OCR
    """
    # Criar documento
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Página 1: Título e informações de empresa
    # Criar imagem temporária com texto
    img1 = Image.new('RGB', (400, 300), color='white')
    draw1 = ImageDraw.Draw(img1)
    
    # Tentar usar fonte padrão
    try:
        font_title = ImageFont.truetype("Arial.ttf", 24)
        font_text = ImageFont.truetype("Arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Título
    draw1.text((20, 20), "OPORTUNIDADE DE NEGÓCIO", fill='black', font=font_title)
    draw1.text((20, 70), "Empresa: TechSolutions Brasil Ltda", fill='black', font=font_text)
    draw1.text((20, 100), "CNPJ: 12.345.678/0001-90", fill='black', font=font_text)
    draw1.text((20, 130), "Contato: João Silva", fill='black', font=font_text)
    draw1.text((20, 160), "Telefone: (11) 99999-8888", fill='black', font=font_text)
    draw1.text((20, 190), "Email: joao@techsolutions.com.br", fill='black', font=font_text)
    
    # Salvar imagem temporária
    img1.save("/tmp/page1.png")
    c.drawImage("/tmp/page1.png", 100, 400, width=400, height=300)
    c.showPage()
    
    # Página 2: Descrição do projeto
    img2 = Image.new('RGB', (400, 350), color='white')
    draw2 = ImageDraw.Draw(img2)
    
    draw2.text((20, 20), "PROJETO: Sistema de Gestão", fill='black', font=font_title)
    draw2.text((20, 70), "Descrição: Desenvolvimento de sistema", fill='black', font=font_text)
    draw2.text((20, 100), "de gestão empresarial completo", fill='black', font=font_text)
    draw2.text((20, 130), "Valor: R$ 250.000,00", fill='black', font=font_text)
    draw2.text((20, 160), "Prazo: 6 meses", fill='black', font=font_text)
    draw2.text((20, 190), "Tecnologias: Python, React, PostgreSQL", fill='black', font=font_text)
    draw2.text((20, 220), "Equipe: 4 desenvolvedores", fill='black', font=font_text)
    
    img2.save("/tmp/page2.png")
    c.drawImage("/tmp/page2.png", 100, 350, width=400, height=350)
    c.showPage()
    
    # Página 3: Dados de faturamento
    img3 = Image.new('RGB', (400, 300), color='white')
    draw3 = ImageDraw.Draw(img3)
    
    draw3.text((20, 20), "DADOS FINANCEIROS", fill='black', font=font_title)
    draw3.text((20, 70), "Faturamento anual: R$ 2.500.000", fill='black', font=font_text)
    draw3.text((20, 100), "Margem de lucro: 15%", fill='black', font=font_text)
    draw3.text((20, 130), "Funcionários: 25", fill='black', font=font_text)
    draw3.text((20, 160), "Setor: Tecnologia", fill='black', font=font_text)
    draw3.text((20, 190), "Localização: São Paulo - SP", fill='black', font=font_text)
    
    img3.save("/tmp/page3.png")
    c.drawImage("/tmp/page3.png", 100, 400, width=400, height=300)
    c.showPage()
    
    # Finalizar PDF
    c.save()
    
    # Limpar arquivos temporários
    for f in ["/tmp/page1.png", "/tmp/page2.png", "/tmp/page3.png"]:
        if os.path.exists(f):
            os.remove(f)
    
    print(f"PDF criado: {filename}")
    print(f"Tamanho: {os.path.getsize(filename)} bytes")
    
    return filename

if __name__ == "__main__":
    create_image_pdf() 