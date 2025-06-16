#!/usr/bin/env python3
"""
Script de teste para o PDF Industrial Pipeline
Demonstra como usar as funções de divisão de PDF e geração de manifest
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workers.split_worker import split_pdf_task, pdf_split_worker
from utils.file_utils import validate_pdf_file, calculate_file_hash, format_file_size

def test_pdf_split(pdf_path: str):
    """
    Testa a divisão de um PDF
    """
    print(f"🔍 Testando divisão do PDF: {pdf_path}")
    
    # Verificar se arquivo existe
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        return False
    
    # Validar PDF
    print("📋 Validando arquivo PDF...")
    validation = validate_pdf_file(pdf_path)
    
    if not validation["is_valid"]:
        print(f"❌ PDF inválido: {validation['error']}")
        return False
    
    print(f"✅ PDF válido - Tamanho: {format_file_size(validation['file_size'])}")
    
    # Calcular hash do arquivo
    print("🔐 Calculando hash do arquivo...")
    file_hash = calculate_file_hash(pdf_path)
    print(f"📝 Hash SHA256: {file_hash}")
    
    # Gerar job_id de teste
    job_id = f"test-{file_hash[:8]}"
    print(f"🆔 Job ID: {job_id}")
    
    # Processar divisão
    print("⚙️ Iniciando divisão do PDF...")
    result = split_pdf_task(pdf_path, job_id)
    
    if result["status"] == "error":
        print(f"❌ Erro na divisão: {result['error']}")
        return False
    
    print(f"✅ PDF dividido com sucesso!")
    print(f"📄 Páginas geradas: {result['page_count']}")
    print(f"📁 Diretório de saída: {result['output_dir']}")
    print(f"📋 Manifest: {result['manifest_path']}")
    
    # Exibir informações do manifest
    print("\n📋 Informações do Manifest:")
    manifest = pdf_split_worker.get_job_status(job_id)
    
    if manifest:
        print(f"   • Job ID: {manifest['job_id']}")
        print(f"   • Processado em: {manifest['processing_info']['processed_at']}")
        print(f"   • Total de páginas: {manifest['output_info']['total_pages']}")
        print(f"   • OCR necessário: {manifest['next_steps']['ocr_required']}")
        print(f"   • Pronto para processamento: {manifest['next_steps']['ready_for_processing']}")
        
        print("\n📄 Páginas geradas:")
        for page in manifest['output_info']['pages'][:3]:  # Mostrar apenas primeiras 3
            print(f"   • Página {page['page_number']}: {page['filename']} ({format_file_size(page['file_size'])})")
        
        if manifest['output_info']['total_pages'] > 3:
            print(f"   • ... e mais {manifest['output_info']['total_pages'] - 3} páginas")
    
    return True

def test_cleanup(job_id: str):
    """
    Testa a limpeza de arquivos
    """
    print(f"\n🧹 Testando limpeza do job: {job_id}")
    
    success = pdf_split_worker.cleanup_job(job_id)
    
    if success:
        print("✅ Arquivos removidos com sucesso!")
    else:
        print("❌ Erro na remoção dos arquivos")
    
    return success

def main():
    """
    Função principal de teste
    """
    print("🚀 PDF Industrial Pipeline - Teste de Divisão")
    print("=" * 50)
    
    # Procurar por PDFs de exemplo na pasta atual
    pdf_files = list(Path(".").glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado na pasta atual")
        print("💡 Dica: Coloque um arquivo PDF na pasta e execute novamente")
        return
    
    # Usar o primeiro PDF encontrado
    test_pdf = str(pdf_files[0])
    print(f"📄 Usando PDF de teste: {test_pdf}")
    
    # Executar teste de divisão
    success = test_pdf_split(test_pdf)
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        
        # Perguntar se quer limpar os arquivos
        response = input("\n❓ Deseja remover os arquivos gerados? (s/N): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            # Extrair job_id do hash do arquivo
            file_hash = calculate_file_hash(test_pdf)
            job_id = f"test-{file_hash[:8]}"
            test_cleanup(job_id)
    else:
        print("\n❌ Teste falhou!")

if __name__ == "__main__":
    main() 