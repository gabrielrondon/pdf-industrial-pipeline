import hashlib
import os
import mimetypes
from typing import Optional, Dict
from pathlib import Path

def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calcula hash de um arquivo
    
    Args:
        file_path: Caminho para o arquivo
        algorithm: Algoritmo de hash (sha256, md5, sha1)
    
    Returns:
        String do hash calculado
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        # Ler arquivo em chunks para economizar memória
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def validate_pdf_file(file_path: str) -> Dict[str, any]:
    """
    Valida se um arquivo é um PDF válido
    
    Args:
        file_path: Caminho para o arquivo
    
    Returns:
        Dict com informações de validação
    """
    result = {
        "is_valid": False,
        "file_exists": False,
        "is_pdf": False,
        "file_size": 0,
        "mime_type": None,
        "error": None
    }
    
    try:
        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            result["error"] = "Arquivo não encontrado"
            return result
        
        result["file_exists"] = True
        result["file_size"] = os.path.getsize(file_path)
        
        # Verificar MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        result["mime_type"] = mime_type
        
        # Verificar extensão
        if not file_path.lower().endswith('.pdf'):
            result["error"] = "Arquivo não possui extensão .pdf"
            return result
        
        # Verificar MIME type
        if mime_type != 'application/pdf':
            result["error"] = f"MIME type inválido: {mime_type}"
            return result
        
        # Verificar header do PDF
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                result["error"] = "Header do PDF inválido"
                return result
        
        result["is_pdf"] = True
        result["is_valid"] = True
        
    except Exception as e:
        result["error"] = f"Erro na validação: {str(e)}"
    
    return result

def ensure_directory(directory: str) -> bool:
    """
    Garante que um diretório existe, criando se necessário
    
    Args:
        directory: Caminho do diretório
    
    Returns:
        True se diretório existe ou foi criado com sucesso
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"Erro ao criar diretório {directory}: {e}")
        return False

def get_file_info(file_path: str) -> Optional[Dict]:
    """
    Obtém informações detalhadas de um arquivo
    
    Args:
        file_path: Caminho para o arquivo
    
    Returns:
        Dict com informações do arquivo ou None se erro
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        stats = os.stat(file_path)
        path_obj = Path(file_path)
        
        return {
            "filename": path_obj.name,
            "file_path": file_path,
            "file_size": stats.st_size,
            "created_at": stats.st_ctime,
            "modified_at": stats.st_mtime,
            "extension": path_obj.suffix.lower(),
            "mime_type": mimetypes.guess_type(file_path)[0],
            "is_file": os.path.isfile(file_path),
            "is_readable": os.access(file_path, os.R_OK)
        }
    
    except Exception as e:
        print(f"Erro ao obter informações do arquivo {file_path}: {e}")
        return None

def clean_filename(filename: str) -> str:
    """
    Limpa nome de arquivo removendo caracteres problemáticos
    
    Args:
        filename: Nome do arquivo original
    
    Returns:
        Nome do arquivo limpo
    """
    # Caracteres problemáticos em nomes de arquivo
    problematic_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    clean_name = filename
    for char in problematic_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Remover espaços duplos e trim
    clean_name = ' '.join(clean_name.split())
    
    return clean_name

def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em formato legível
    
    Args:
        size_bytes: Tamanho em bytes
    
    Returns:
        String formatada (ex: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def is_safe_path(path: str, base_path: str) -> bool:
    """
    Verifica se um caminho é seguro (não sai do diretório base)
    
    Args:
        path: Caminho a ser verificado
        base_path: Diretório base
    
    Returns:
        True se caminho é seguro
    """
    try:
        # Resolver caminhos relativos
        abs_path = os.path.realpath(path)
        abs_base = os.path.realpath(base_path)
        
        # Verificar se caminho está dentro do base
        return abs_path.startswith(abs_base)
    
    except Exception:
        return False
