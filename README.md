# PDF Industrial Pipeline

Pipeline para processamento industrial de arquivos PDF com divisão automática em páginas, detecção de necessidade de OCR e geração de manifests estruturados.

## 🚀 Funcionalidades

- ✅ **Upload de PDFs** via API REST
- ✅ **Divisão automática** em páginas usando qpdf
- ✅ **Validação de arquivos** PDF
- ✅ **Geração de manifest.json** com metadados completos
- ✅ **Detecção automática** de necessidade de OCR
- ✅ **API REST completa** com status e limpeza de jobs
- ✅ **Sistema de logs** estruturado

## 📁 Estrutura do Projeto

```
pdf-industrial-pipeline/
├── app/                 # FastAPI e lógica da API de ingestão
├── workers/             # Workers para OCR, split, etc.
│   └── split_worker.py  # Worker de divisão de PDF
├── utils/               # Funções auxiliares (hash, logs, etc.)
│   └── file_utils.py    # Utilitários de arquivo
├── tests/               # Testes unitários e de integração
├── uploads/             # Diretório temporário de uploads
├── temp_splits/         # Diretório temporário de páginas divididas
├── main.py              # Ponto de entrada (FastAPI)
├── test_pipeline.py     # Script de teste
├── requirements.txt     # Dependências
└── README.md
```

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd pdf-industrial-pipeline
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

### 3. Instale as dependências Python
```bash
pip install -r requirements.txt
```

### 4. Instale o qpdf
**macOS:**
```bash
brew install qpdf
```

**Ubuntu/Debian:**
```bash
sudo apt install qpdf
```

**Windows:**
- Baixe o instalador em: https://qpdf.sourceforge.net/
- Ou use chocolatey: `choco install qpdf`

### 5. Verifique a instalação
```bash
qpdf --version
```

## 🚀 Uso

### 1. Iniciar o servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Acessar a documentação interativa
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Verificar saúde do sistema
```bash
curl http://localhost:8000/health
```

## 📡 API Endpoints

### POST /upload
Upload e processamento de arquivo PDF

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@exemplo.pdf"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processed",
  "original_filename": "exemplo.pdf",
  "file_size": "2.5 MB",
  "page_count": 10,
  "output_directory": "temp_splits/550e8400-e29b-41d4-a716-446655440000",
  "manifest_path": "temp_splits/550e8400-e29b-41d4-a716-446655440000/manifest.json"
}
```

### GET /job/{job_id}/status
Consultar status de um job

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_info": {
    "processed_at": "2024-01-15T10:30:00",
    "processor": "qpdf",
    "status": "completed"
  },
  "original_file": {
    "filename": "exemplo.pdf",
    "file_size": 2621440
  },
  "output_info": {
    "total_pages": 10,
    "pages": [...]
  },
  "next_steps": {
    "ocr_required": false,
    "ready_for_processing": true
  }
}
```

### GET /job/{job_id}/manifest
Obter manifest completo

### DELETE /job/{job_id}
Limpar arquivos temporários de um job

### GET /health
Verificação de saúde do sistema

## 🧪 Teste Local

Execute o script de teste incluído:

```bash
# Coloque um arquivo PDF na pasta do projeto
python test_pipeline.py
```

O script irá:
1. Validar o PDF
2. Dividir em páginas
3. Gerar o manifest
4. Exibir informações detalhadas
5. Opcionalmente limpar os arquivos gerados

## 📋 Exemplo de Manifest

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_info": {
    "processed_at": "2024-01-15T10:30:00.123Z",
    "processor": "qpdf",
    "status": "completed"
  },
  "original_file": {
    "filename": "documento.pdf",
    "file_path": "uploads/550e8400-e29b-41d4-a716-446655440000.pdf",
    "file_size": 2621440,
    "created_at": "2024-01-15T10:29:45.123Z"
  },
  "output_info": {
    "output_directory": "temp_splits/550e8400-e29b-41d4-a716-446655440000",
    "total_pages": 5,
    "pages": [
      {
        "page_number": 1,
        "filename": "page-1.pdf",
        "file_path": "temp_splits/550e8400-e29b-41d4-a716-446655440000/page-1.pdf",
        "file_size": 524288,
        "created_at": "2024-01-15T10:30:00.456Z"
      }
    ]
  },
  "next_steps": {
    "ocr_required": false,
    "ready_for_processing": true
  }
}
```

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` (opcional):

```env
# Diretórios
UPLOAD_DIR=uploads
TEMP_SPLITS_DIR=temp_splits

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Limites de Arquivo
Por padrão, o FastAPI aceita arquivos até 16MB. Para arquivos maiores, configure:

```python
# Em main.py
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)
```

## 🐛 Troubleshooting

### Erro: "qpdf: command not found"
- Certifique-se que o qpdf está instalado e no PATH
- Teste: `qpdf --version`

### Erro: "PDF inválido"
- Verifique se o arquivo é realmente um PDF
- Teste com outro arquivo PDF

### Erro: "Permission denied"
- Verifique permissões das pastas uploads/ e temp_splits/
- Execute: `chmod 755 uploads temp_splits`

### Porta já em uso
```bash
# Matar processo na porta 8000
sudo lsof -t -i tcp:8000 | xargs kill -9

# Ou usar outra porta
uvicorn main:app --port 8001
```

## 🚧 Próximos Passos

- [ ] Integração com RabbitMQ/SQS para filas
- [ ] Worker de OCR com Tesseract
- [ ] Upload para S3/MinIO
- [ ] Interface web simples
- [ ] Testes automatizados
- [ ] Docker/Kubernetes
- [ ] Monitoramento com Prometheus

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request
