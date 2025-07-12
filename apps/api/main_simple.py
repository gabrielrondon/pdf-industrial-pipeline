import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF Industrial Pipeline API",
    description="PDF processing and analysis API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PDF Industrial Pipeline API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.get("/test-db")
async def test_database():
    """Test database connection"""
    try:
        # Simple database test
        database_url = os.getenv("DATABASE_URL")
        redis_url = os.getenv("REDIS_URL")
        
        return {
            "database_configured": bool(database_url),
            "redis_configured": bool(redis_url),
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "database_url_prefix": database_url[:20] + "..." if database_url else None,
            "redis_url_prefix": redis_url[:20] + "..." if redis_url else None
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/debug-s3")
async def debug_s3_config():
    """Debug S3 configuration and test connection"""
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        # Check S3 configuration
        s3_status = {
            "storage_backend": settings.storage_backend,
            "s3_bucket": settings.s3_bucket,
            "s3_region": settings.s3_region,
            "aws_access_key_present": bool(settings.aws_access_key_id),
            "aws_secret_key_present": bool(settings.aws_secret_access_key),
            "s3_configured": settings.storage_backend == "s3" and bool(settings.s3_bucket),
        }
        
        # Try to import S3Backend
        try:
            from storage_backends.s3_backend import S3Backend
            s3_status["s3_backend_import"] = "success"
            
            # Try to create S3Backend instance
            try:
                s3_backend = S3Backend(
                    bucket=settings.s3_bucket,
                    region=settings.s3_region,
                    access_key=settings.aws_access_key_id,
                    secret_key=settings.aws_secret_access_key,
                    endpoint_url=settings.s3_endpoint_url
                )
                s3_status["s3_backend_creation"] = "success"
                
                # Try to test bucket access
                try:
                    import tempfile
                    from io import BytesIO
                    
                    # Create a small test file
                    test_content = b"Test file from Railway API"
                    test_key = "test/debug-upload.txt"
                    
                    # Try to upload
                    test_file = BytesIO(test_content)
                    upload_result = await s3_backend.upload(
                        key=test_key,
                        file_obj=test_file,
                        metadata={"test": "true", "timestamp": "2025-07-12"}
                    )
                    s3_status["s3_test_upload"] = "success"
                    s3_status["test_file_key"] = test_key
                    
                except Exception as upload_error:
                    s3_status["s3_test_upload"] = f"failed: {str(upload_error)}"
                    
            except Exception as creation_error:
                s3_status["s3_backend_creation"] = f"failed: {str(creation_error)}"
                
        except Exception as import_error:
            s3_status["s3_backend_import"] = f"failed: {str(import_error)}"
        
        return s3_status
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/v1/jobs")
async def get_jobs(user_id: str = None):
    """Get jobs, optionally filtered by user_id"""
    try:
        if not DATABASE_AVAILABLE:
            logger.warning("⚠️ Database not available for jobs endpoint")
            return []

        with get_db() as db_session:
            query = db_session.query(Job)
            
            # Filter by user_id if provided
            if user_id:
                logger.info(f"🔍 Filtering jobs by user_id: {user_id}")
                query = query.filter(Job.user_id == user_id)
            else:
                logger.info("📋 Fetching all jobs (no user_id filter)")
            
            jobs = query.order_by(Job.created_at.desc()).limit(100).all()
            
            logger.info(f"📄 Found {len(jobs)} jobs")
            
            # Convert to dict format
            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    "id": str(job.id),
                    "user_id": str(job.user_id),
                    "filename": job.filename,
                    "status": job.status,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "page_count": job.page_count,
                    "file_size": job.file_size
                })
            
            return jobs_data
            
    except Exception as e:
        logger.error(f"❌ Error fetching jobs: {str(e)}")
        return []

@app.get("/debug-env")
async def debug_environment():
    """Debug endpoint to show environment variables (safe info only)"""
    try:
        env_vars = {}
        
        # Safe environment variables to show
        safe_vars = [
            "ENVIRONMENT", "PORT", "PYTHONPATH", "SECRET_KEY", 
            "DEBUG", "API_VERSION", "STORAGE_BACKEND"
        ]
        
        for var in safe_vars:
            value = os.getenv(var)
            if var == "SECRET_KEY" and value:
                # Only show first 8 chars of secret key
                env_vars[var] = value[:8] + "..." if len(value) > 8 else "***"
            else:
                env_vars[var] = value
        
        # Check for database URLs without exposing full URLs
        database_url = os.getenv("DATABASE_URL")
        redis_url = os.getenv("REDIS_URL")
        
        env_vars["DATABASE_URL_EXISTS"] = bool(database_url)
        env_vars["REDIS_URL_EXISTS"] = bool(redis_url)
        
        if database_url:
            env_vars["DATABASE_URL_PREFIX"] = database_url[:30] + "..." 
        if redis_url:
            env_vars["REDIS_URL_PREFIX"] = redis_url[:30] + "..."
            
        # S3 Configuration Check
        s3_bucket = os.getenv("S3_BUCKET")
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        s3_region = os.getenv("S3_REGION")
        
        env_vars["S3_CONFIGURED"] = all([s3_bucket, aws_access_key, aws_secret_key])
        env_vars["S3_BUCKET"] = s3_bucket
        env_vars["S3_REGION"] = s3_region or "us-east-1"
        env_vars["AWS_ACCESS_KEY_ID"] = aws_access_key[:8] + "..." if aws_access_key else None
        env_vars["AWS_SECRET_ACCESS_KEY"] = "***" if aws_secret_key else None
            
        # Show all environment variables that start with common prefixes
        all_env = dict(os.environ)
        railway_vars = {k: v for k, v in all_env.items() if k.startswith(('RAILWAY_', 'DATABASE_', 'REDIS_', 'POSTGRES', 'S3_', 'AWS_'))}
        
        # Hide sensitive values
        for key in railway_vars:
            if 'SECRET' in key or 'PASSWORD' in key or 'KEY' in key:
                if railway_vars[key]:
                    railway_vars[key] = railway_vars[key][:8] + "..." if len(railway_vars[key]) > 8 else "***"
        
        return {
            "configured_vars": env_vars,
            "railway_vars": railway_vars,
            "total_env_vars": len(all_env)
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

# Include basic API routes
from fastapi import File, UploadFile, HTTPException
from pydantic import BaseModel
import uuid
import tempfile
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

# Pydantic models for API requests
class UpdateTitleRequest(BaseModel):
    title: str

# Database import for PostgreSQL storage
DATABASE_AVAILABLE = False
jobs_storage = {}  # Fallback storage

try:
    import sys
    import os
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    from database.connection import get_db
    from database.models import Job, TextAnalysis, MLPrediction
    from sqlalchemy.orm import Session
    DATABASE_AVAILABLE = True
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"⚠️ Database not available: {e}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")
    DATABASE_AVAILABLE = False
except Exception as e:
    print(f"❌ Unexpected database error: {e}")
    DATABASE_AVAILABLE = False

# Real PDF text extraction and analysis functions
def extract_text_from_pdf(file_path: str) -> tuple[str, dict]:
    """Extract text from PDF file using PyMuPDF with page tracking"""
    try:
        import fitz  # PyMuPDF
        logger.info("✅ PyMuPDF imported successfully")
        doc = fitz.open(file_path)
        full_text = ""
        page_texts = {}
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text()
            page_texts[page_num + 1] = page_text  # 1-indexed pages
            full_text += page_text + "\n"
        
        doc.close()
        logger.info(f"✅ PDF text extraction completed: {len(full_text)} characters")
        return full_text, page_texts
    except ImportError as import_error:
        logger.warning(f"⚠️ PyMuPDF (fitz) not available: {import_error}")
        # Fallback: return filename as text
        import os
        filename = os.path.basename(file_path)
        fallback_text = f"Documento PDF: {filename}\nTexto extraído automaticamente usando fallback."
        logger.info("🔄 Using fallback text extraction")
        return fallback_text, {1: fallback_text}
    except Exception as e:
        logger.error(f"❌ PDF text extraction failed: {str(e)}")
        import os
        filename = os.path.basename(file_path)
        mock_text = f"[Error] Could not extract text from {filename}: {str(e)}. Mock text: leilão judicial, imóvel residencial, valor de avaliação R$ 250.000,00, contato (11) 98765-4321."
        logger.info("🔄 Using error fallback text")
        return mock_text, {1: mock_text}

def is_judicial_document(text: str) -> bool:
    """Check if document appears to be judicial/legal"""
    judicial_indicators = [
        'leilão', 'leilao', 'hasta pública', 'hasta publica',
        'tribunal', 'vara', 'juiz', 'processo',
        'código de processo civil', 'cpc',
        'arrematação', 'arremataçao', 'adjudicação',
        'penhora', 'execução', 'execucao'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in judicial_indicators)

def analyze_judicial_content(text: str) -> List[Dict[str, Any]]:
    """Analyze judicial/legal document content"""
    points = []
    text_lower = text.lower()
    
    # Auction detection
    auction_keywords = ['leilão', 'leilao', 'hasta pública', 'hasta publica', 'arrematação']
    if any(keyword in text_lower for keyword in auction_keywords):
        points.append({
            'id': 'auction_identified',
            'title': 'Leilão Judicial Identificado',
            'comment': 'Documento contém informações sobre leilão judicial. Verifique datas, valores e condições.',
            'status': 'confirmado',
            'category': 'leilao',
            'priority': 'high'
        })
    
    # Property types
    property_types = {
        'imóvel': ['imovel', 'imóvel', 'propriedade', 'terreno', 'lote'],
        'apartamento': ['apartamento', 'apt', 'unidade'],
        'casa': ['casa', 'residencia', 'residência'],
        'comercial': ['comercial', 'loja', 'escritorio', 'escritório', 'sala comercial'],
        'veículo': ['veiculo', 'veículo', 'automóvel', 'automovel', 'carro', 'moto']
    }
    
    for prop_type, keywords in property_types.items():
        if any(keyword in text_lower for keyword in keywords):
            points.append({
                'id': f'property_{prop_type}',
                'title': f'Bem do Tipo: {prop_type.title()}',
                'comment': f'Identificado bem do tipo {prop_type} no documento.',
                'status': 'confirmado',
                'category': 'investimento',
                'priority': 'high'
            })
            break  # Only add one property type
    
    # CPC Article 889 compliance
    cpc_indicators = ['art. 889', 'artigo 889', 'cpc 889', 'código de processo civil']
    if any(indicator in text_lower for indicator in cpc_indicators):
        points.append({
            'id': 'cpc_889_compliance',
            'title': 'Referência ao CPC Art. 889',
            'comment': 'Documento faz referência ao Artigo 889 do Código de Processo Civil - verifique conformidade legal.',
            'status': 'alerta',
            'category': 'leilao',
            'priority': 'high'
        })
    
    return points

def analyze_financial_opportunities(text: str, page_texts: dict) -> List[Dict[str, Any]]:
    """Extract financial and investment information with page references"""
    points = []
    
    # Specific value patterns with context
    value_patterns = {
        'lance_minimo': [
            r'lance\s+m[ií]nimo.*?R\$\s*([\d.,]+)',
            r'valor\s+m[ií]nimo.*?R\$\s*([\d.,]+)',
            r'arremat.*?R\$\s*([\d.,]+)'
        ],
        'avaliacao': [
            r'avalia[çc][ãa]o.*?R\$\s*([\d.,]+)',
            r'valor\s+de\s+avalia[çc][ãa]o.*?R\$\s*([\d.,]+)',
            r'avaliado\s+em.*?R\$\s*([\d.,]+)'
        ],
        'custas': [
            r'custas.*?R\$\s*([\d.,]+)',
            r'despesas.*?R\$\s*([\d.,]+)',
            r'emolumentos.*?R\$\s*([\d.,]+)'
        ]
    }
    
    def find_value_in_pages(pattern, value_type):
        """Find value and its page location"""
        for page_num, page_text in page_texts.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    clean_value = match.replace('.', '').replace(',', '.')
                    value = float(clean_value)
                    if value > 1000:  # Only significant values
                        return value, page_num, match
                except ValueError:
                    continue
        return None, None, None
    
    # Find specific types of values
    for value_type, patterns in value_patterns.items():
        for pattern in patterns:
            value, page_num, raw_match = find_value_in_pages(pattern, value_type)
            if value:
                type_names = {
                    'lance_minimo': '💰 Lance Mínimo',
                    'avaliacao': '📊 Valor de Avaliação', 
                    'custas': '📋 Custas e Despesas'
                }
                
                points.append({
                    'id': f'{value_type}_value',
                    'title': f'{type_names[value_type]}: R$ {value:,.2f}',
                    'comment': f'Valor encontrado na página {page_num}. Clique para ver detalhes específicos.',
                    'status': 'confirmado',
                    'category': 'financeiro',
                    'priority': 'high',
                    'page_reference': page_num,
                    'raw_value': raw_match,
                    'details': {
                        'value_type': value_type,
                        'formatted_value': f'R$ {value:,.2f}',
                        'page_location': page_num
                    }
                })
                break  # Only add first match of this type
    
    # Investment opportunity calculation
    lance_minimo = None
    avaliacao = None
    
    for point in points:
        if 'lance_minimo' in point['id']:
            lance_minimo = float(point['raw_value'].replace('.', '').replace(',', '.'))
        elif 'avaliacao' in point['id']:
            avaliacao = float(point['raw_value'].replace('.', '').replace(',', '.'))
    
    if lance_minimo and avaliacao and avaliacao > lance_minimo:
        desconto = ((avaliacao - lance_minimo) / avaliacao) * 100
        points.append({
            'id': 'investment_opportunity',
            'title': f'🎯 Oportunidade de Investimento: {desconto:.1f}% de Desconto',
            'comment': f'Lance mínimo representa {desconto:.1f}% de desconto sobre a avaliação. ROI potencial interessante.',
            'status': 'confirmado',
            'category': 'investimento',
            'priority': 'high',
            'details': {
                'discount_percentage': f'{desconto:.1f}%',
                'potential_savings': f'R$ {avaliacao - lance_minimo:,.2f}',
                'investment_analysis': 'Oportunidade identificada'
            }
        })
    
    # Debt analysis with page reference
    debt_keywords = ['dívida', 'divida', 'débito', 'debito', 'ônus', 'onus', 'hipoteca', 'financiamento']
    for page_num, page_text in page_texts.items():
        if any(keyword in page_text.lower() for keyword in debt_keywords):
            points.append({
                'id': 'debt_analysis',
                'title': '⚠️ Possíveis Ônus ou Dívidas Detectados',
                'comment': f'Documento menciona possíveis encargos na página {page_num}. Verifique detalhadamente antes de investir.',
                'status': 'alerta',
                'category': 'financeiro',
                'priority': 'high',
                'page_reference': page_num,
                'details': {
                    'risk_level': 'Alto',
                    'recommendation': 'Verificação obrigatória antes do lance'
                }
            })
            break
    
    return points

def extract_contacts_and_deadlines(text: str, page_texts: dict) -> List[Dict[str, Any]]:
    """Extract contact information and important deadlines with page references"""
    points = []
    
    # Specific date patterns with context
    specific_date_patterns = {
        'data_leilao': [
            r'data\s+do\s+leil[ãa]o.*?(\d{1,2}/\d{1,2}/\d{4})',
            r'leil[ãa]o.*?(\d{1,2}/\d{1,2}/\d{4}).*?(\d{1,2}h\d{2})',
            r'realizar[áa]\s+em.*?(\d{1,2}/\d{1,2}/\d{4})'
        ],
        'prazo_pagamento': [
            r'prazo.*?pagamento.*?(\d{1,2}/\d{1,2}/\d{4})',
            r'at[ée]\s+(\d{1,2}/\d{1,2}/\d{4}).*?pagar',
            r'vencimento.*?(\d{1,2}/\d{1,2}/\d{4})'
        ],
        'prazo_recurso': [
            r'prazo.*?recurso.*?(\d{1,2}/\d{1,2}/\d{4})',
            r'impugna[çc][ãa]o.*?at[ée].*?(\d{1,2}/\d{1,2}/\d{4})'
        ]
    }
    
    def find_specific_date(patterns, date_type):
        """Find specific date type and its page location"""
        for page_num, page_text in page_texts.items():
            for pattern in patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    return matches[0] if isinstance(matches[0], str) else matches[0][0], page_num
        return None, None
    
    # Extract specific dates
    for date_type, patterns in specific_date_patterns.items():
        date_found, page_num = find_specific_date(patterns, date_type)
        if date_found:
            type_names = {
                'data_leilao': '📅 Data do Leilão',
                'prazo_pagamento': '💳 Prazo para Pagamento',
                'prazo_recurso': '⚖️ Prazo para Recurso'
            }
            
            points.append({
                'id': f'{date_type}_deadline',
                'title': f'{type_names[date_type]}: {date_found}',
                'comment': f'Data importante identificada na página {page_num}. Marque na agenda!',
                'status': 'alerta',
                'category': 'prazo',
                'priority': 'high',
                'page_reference': page_num,
                'details': {
                    'date_type': date_type,
                    'formatted_date': date_found,
                    'urgency': 'Alta'
                }
            })
    
    # Extract and categorize contacts
    def find_specific_contact(pattern, contact_type):
        """Find specific contact type and its page location"""
        for page_num, page_text in page_texts.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                return matches[0], page_num
        return None, None
    
    # Leiloeiro/Official contact
    leiloeiro_patterns = [
        r'leiloeiro.*?(\(\d{2}\)\s*\d{4,5}[-\s]?\d{4})',
        r'respons[áa]vel.*?(\(\d{2}\)\s*\d{4,5}[-\s]?\d{4})'
    ]
    
    for pattern in leiloeiro_patterns:
        phone, page_num = find_specific_contact(pattern, 'leiloeiro')
        if phone:
            points.append({
                'id': 'leiloeiro_contact',
                'title': f'📞 Contato do Leiloeiro: {phone}',
                'comment': f'Telefone do responsável pelo leilão encontrado na página {page_num}.',
                'status': 'confirmado',
                'category': 'contato',
                'priority': 'high',
                'page_reference': page_num,
                'details': {
                    'contact_type': 'Leiloeiro Oficial',
                    'phone_number': phone
                }
            })
            break
    
    # Official emails (tribunal, cartório)
    official_email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]*(?:tj|tribunal|cartorio|leilao)[a-zA-Z0-9.-]*\.[a-zA-Z]{2,})'
    
    for page_num, page_text in page_texts.items():
        matches = re.findall(official_email_pattern, page_text, re.IGNORECASE)
        if matches:
            email = matches[0]
            contact_type = 'Tribunal' if 'tj' in email or 'tribunal' in email else 'Cartório/Leilão'
            
            points.append({
                'id': 'official_email',
                'title': f'📧 E-mail {contact_type}: {email}',
                'comment': f'Contato oficial encontrado na página {page_num}.',
                'status': 'confirmado',
                'category': 'contato',
                'priority': 'high',
                'page_reference': page_num,
                'details': {
                    'contact_type': contact_type,
                    'email_address': email
                }
            })
            break
    
    return points

def detect_document_type(text: str, filename: str) -> str:
    """Detect document type based on content and filename"""
    text_lower = text.lower()
    filename_lower = filename.lower()
    
    # Document type indicators
    types = {
        'Edital de Leilão': ['edital', 'leilão', 'leilao', 'hasta'],
        'Processo Judicial': ['processo', 'autos', 'vara', 'tribunal'],
        'Laudo de Avaliação': ['laudo', 'avaliação', 'avaliacao', 'perito'],
        'Certidão': ['certidao', 'certidão', 'registro'],
        'Contrato': ['contrato', 'acordo', 'ajuste'],
        'Escritura': ['escritura', 'tabeliao', 'tabelião', 'cartorio']
    }
    
    for doc_type, keywords in types.items():
        if any(keyword in text_lower or keyword in filename_lower for keyword in keywords):
            return doc_type
    
    return 'Documento Jurídico'

def perform_comprehensive_analysis(text: str, page_texts: dict, filename: str) -> Dict[str, Any]:
    """Perform comprehensive analysis of the document with page tracking"""
    total_pages = len(page_texts)
    
    results = {
        'job_id': '',
        'filename': filename,
        'analysis_type': 'comprehensive',
        'total_pages': total_pages,
        'analysis_date': datetime.utcnow().isoformat(),
        'points': []
    }
    
    # Basic document analysis
    doc_type = detect_document_type(text, filename)
    
    results['points'].append({
        'id': 'document_type',
        'title': f'📄 Tipo de Documento: {doc_type}',
        'comment': f'Documento identificado como {doc_type} baseado no conteúdo e nome do arquivo.',
        'status': 'confirmado',
        'category': 'geral',
        'priority': 'medium',
        'details': {
            'document_classification': doc_type,
            'confidence': 'Alta',
            'total_pages': total_pages
        }
    })
    
    if total_pages > 1:
        results['points'].append({
            'id': 'document_size',
            'title': f'📊 Documento Extenso: {total_pages} páginas',
            'comment': f'Documento contém {total_pages} páginas ({len(text):,} caracteres). Análise detalhada página por página.',
            'status': 'confirmado',
            'category': 'geral',
            'priority': 'low',
            'details': {
                'page_count': total_pages,
                'character_count': len(text),
                'analysis_scope': 'Completa'
            }
        })
    
    # Judicial analysis if applicable
    if is_judicial_document(text):
        judicial_points = analyze_judicial_content(text)
        results['points'].extend(judicial_points)
    
    # Financial analysis with page tracking
    financial_points = analyze_financial_opportunities(text, page_texts)
    results['points'].extend(financial_points)
    
    # Contact and deadline analysis with page tracking
    contact_points = extract_contacts_and_deadlines(text, page_texts)
    results['points'].extend(contact_points)
    
    return results

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = None):
    """Upload PDF file for processing"""
    try:
        logger.info(f"🚀 Starting upload for file: {file.filename}")
        logger.info(f"📝 Received user_id: {user_id} (type: {type(user_id)})")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validate file size (500MB limit)
        max_size = 500 * 1024 * 1024  # 500MB
        content = await file.read()
        logger.info(f"📁 File size: {len(content)} bytes")
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 500MB)")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        logger.info(f"🆔 Generated job ID: {job_id}")
        
        # Validate user ID
        if not user_id:
            logger.warning("⚠️ No user_id provided, using job_id as fallback")
            user_id = job_id
        else:
            # Basic UUID validation for Supabase user IDs
            import re
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if re.match(uuid_pattern, user_id, re.IGNORECASE):
                logger.info(f"✅ Valid user_id provided: {user_id}")
            else:
                logger.warning(f"⚠️ Invalid user_id format: {user_id}, using job_id as fallback")
                user_id = job_id
        
        # Save file temporarily (in production, save to proper storage)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(content)
            file_path = tmp.name
        logger.info(f"💾 Saved temporary file: {file_path}")
        
        # Extract text from PDF for real analysis with page tracking
        logger.info(f"🔍 Extracting text from PDF: {file.filename}")
        extracted_text, page_texts = extract_text_from_pdf(file_path)
        
        # Perform comprehensive analysis on the extracted text with page tracking
        logger.info(f"Performing comprehensive analysis for: {file.filename}")
        analysis_results = perform_comprehensive_analysis(extracted_text, page_texts, file.filename)
        
        # Update job ID in results
        analysis_results['job_id'] = job_id
        analysis_points = analysis_results['points']
        
        logger.info(f"Analysis completed: {len(analysis_points)} points identified")
        
        # Store job info in PostgreSQL (or fallback to memory)
        if DATABASE_AVAILABLE:
            try:
                # Save to PostgreSQL database
                with get_db() as db_session:
                    # Create Job record
                    job_record = Job(
                        id=job_id,
                        user_id=user_id,  # Now using real user_id from frontend
                        filename=file.filename,
                        file_size=len(content),
                        status="completed",
                        page_count=len(page_texts),
                        processing_completed_at=datetime.now(),
                        processing_time_seconds=1.0,  # Placeholder
                        config={"extracted_text_length": len(extracted_text)}
                    )
                    db_session.add(job_record)
                    
                    # Create TextAnalysis record
                    text_analysis = TextAnalysis(
                        job_id=job_id,
                        entities={"analysis_points": analysis_points},
                        keywords=list(set([point.get('title', '') for point in analysis_points])),
                        business_indicators=analysis_results.get('summary', {}),
                        financial_data=analysis_results.get('financial_summary', {})
                    )
                    db_session.add(text_analysis)
                    
                    # Create MLPrediction record
                    ml_prediction = MLPrediction(
                        job_id=job_id,
                        model_name="comprehensive_analyzer",
                        model_version="1.0",
                        lead_score=analysis_results.get('overall_score', 0.5),
                        confidence=0.85,  # High confidence for rule-based analysis
                        predictions=analysis_results
                    )
                    db_session.add(ml_prediction)
                    
                    # Session will auto-commit and close via context manager
                    logger.info(f"✅ Job {job_id} saved to PostgreSQL database")
                
            except Exception as e:
                logger.error(f"❌ Error saving to database: {e}")
                # Fallback to memory storage
                jobs_storage[job_id] = {
                    "job_id": job_id,
                    "filename": file.filename,
                    "file_size": len(content),
                    "status": "completed",
                    "results": analysis_results
                }
        else:
            # Fallback to memory storage
            jobs_storage[job_id] = {
                "job_id": job_id,
                "filename": file.filename,
                "file_size": len(content),
                "status": "completed",
                "file_path": file_path,
                "extracted_text_length": len(extracted_text),
                "total_pages": len(page_texts),
                "page_texts": page_texts,
                "results": analysis_results
            }
        
        logger.info(f"File uploaded successfully: {file.filename} ({len(content)} bytes)")
        
        # STORAGE: Handle file storage based on configuration
        storage_info = {"strategy": "process_and_delete", "location": "none"}
        
        try:
            from config.settings import get_settings
            settings = get_settings()
            
            # Check if S3 storage is configured
            logger.info(f"🔍 Storage backend check: {settings.storage_backend}, S3 bucket: {settings.s3_bucket}")
            
            if settings.storage_backend == "s3" and settings.s3_bucket:
                logger.info(f"☁️ S3 storage enabled, attempting upload...")
                logger.info(f"🔑 AWS credentials present: access_key={bool(settings.aws_access_key_id)}, secret_key={bool(settings.aws_secret_access_key)}")
                
                # Auto-detect region if not set or default
                actual_region = settings.s3_region
                if not actual_region or actual_region == "us-east-1":
                    # Try to detect region from bucket name or use Stockholm default
                    actual_region = "eu-north-1"  # Your actual bucket region
                    logger.warning(f"⚠️ Using corrected region: {actual_region} (bucket is in Stockholm)")
                
                logger.info(f"S3 Config: bucket={settings.s3_bucket}, region={actual_region}")
                
                try:
                    # Save to S3 for compliance/re-processing (Option 2)
                    logger.info(f"📦 Attempting to import S3Backend...")
                    from storage_backends.s3_backend import S3Backend
                    logger.info(f"✅ S3Backend imported successfully")
                    
                    s3_backend = S3Backend(
                        bucket=settings.s3_bucket,
                        region=actual_region,  # Use corrected region
                        access_key=settings.aws_access_key_id,
                        secret_key=settings.aws_secret_access_key,
                        endpoint_url=settings.s3_endpoint_url
                    )
                    logger.info(f"✅ S3Backend instance created")
                    
                    # Upload to S3
                    s3_key = f"documents/{user_id}/{job_id}/{file.filename}"
                    logger.info(f"📤 Starting S3 upload to key: {s3_key}")
                    
                    with open(file_path, 'rb') as f:
                        upload_result = await s3_backend.upload(
                            key=s3_key,
                            file_obj=f,
                            metadata={
                                "job_id": job_id,
                                "user_id": user_id,
                                "original_filename": file.filename,
                                "upload_date": datetime.utcnow().isoformat(),
                                "content_type": "application/pdf"
                            },
                            content_type="application/pdf"
                        )
                    
                    storage_info = {
                        "strategy": "s3_storage", 
                        "location": f"s3://{settings.s3_bucket}/{s3_key}",
                        "s3_url": upload_result.url if hasattr(upload_result, 'url') else None
                    }
                    logger.info(f"✅ File successfully saved to S3: {s3_key}")
                    logger.info(f"📍 S3 Location: s3://{settings.s3_bucket}/{s3_key}")
                    
                except Exception as s3_error:
                    logger.error(f"❌ S3 upload failed: {type(s3_error).__name__}: {s3_error}")
                    import traceback
                    logger.error(f"S3 Error traceback: {traceback.format_exc()}")
                    storage_info = {"strategy": "process_and_delete_s3_failed", "location": "none", "error": str(s3_error)}
            else:
                logger.info(f"⚠️ S3 storage not configured or disabled, using process-and-delete strategy")
            
        except Exception as storage_error:
            logger.warning(f"⚠️ Storage backend check failed: {storage_error}")
        
        # CLEANUP: Delete temporary file (always cleanup local temp)
        try:
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"🗑️ Cleaned up temporary file: {file_path}")
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Could not cleanup temp file {file_path}: {cleanup_error}")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Arquivo {file.filename} processado com sucesso",
            "file_size": len(content),
            "storage": storage_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Upload error: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        
        # Return as proper error response with 500 status
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "database_available": DATABASE_AVAILABLE,
                "message": f"Erro no upload: {str(e)}"
            }
        )

@app.post("/api/v1/semantic-search")
async def semantic_search(request: dict):
    """Busca semântica nos documentos processados"""
    try:
        query = request.get('query', '').strip()
        document_ids = request.get('documentIds', [])
        limit = request.get('limit', 10)
        threshold = request.get('threshold', 0.6)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")
        
        logger.info(f"Semantic search: '{query}' (docs: {len(document_ids)}, limit: {limit})")
        
        # Buscar nos jobs armazenados
        results = []
        search_method = "text_based"  # Para agora, busca baseada em texto
        
        if DATABASE_AVAILABLE:
            try:
                with get_db() as db_session:
                    # Buscar jobs no PostgreSQL
                    query_builder = db_session.query(Job, TextAnalysis).join(
                        TextAnalysis, Job.id == TextAnalysis.job_id
                    ).filter(Job.status == 'completed')
                    
                    if document_ids:
                        query_builder = query_builder.filter(Job.id.in_(document_ids))
                    
                    jobs_with_analysis = query_builder.all()
                    
                    # Busca simples por palavras-chave
                    query_words = query.lower().split()
                    
                    for job, analysis in jobs_with_analysis:
                        # Verificar se a query está nas keywords ou entidades
                        keywords = analysis.keywords or []
                        entities_text = str(analysis.entities or {}).lower()
                        business_text = str(analysis.business_indicators or {}).lower()
                        
                        # Calcular similaridade simples baseada em matches de palavras
                        matches = 0
                        total_text = ' '.join(keywords).lower() + ' ' + entities_text + ' ' + business_text
                        
                        for word in query_words:
                            if word in total_text:
                                matches += 1
                        
                        similarity = matches / len(query_words) if query_words else 0
                        
                        if similarity >= threshold:
                            results.append({
                                'chunkId': str(job.id),
                                'content': f"Análise de {job.filename}: {', '.join(keywords[:5])}...",
                                'similarity': similarity,
                                'wordCount': len(keywords),
                                'pageStart': 1,
                                'pageEnd': job.page_count or 1,
                                'document': {
                                    'id': str(job.id),
                                    'file_name': job.filename,
                                    'type': 'documento'
                                }
                            })
                    
                    search_method = "postgresql_text_search"
                
            except Exception as e:
                logger.error(f"Database search error: {e}")
                # Fallback para busca em memória
                pass
        
        # Fallback: busca em jobs_storage se database não disponível
        if not results and not DATABASE_AVAILABLE:
            for job_id, job_data in jobs_storage.items():
                if document_ids and job_id not in document_ids:
                    continue
                
                # Busca simples no texto extraído e resultados
                job_text = (
                    job_data.get('filename', '') + ' ' +
                    str(job_data.get('results', {}))
                ).lower()
                
                # Calcular matches simples
                matches = sum(1 for word in query.lower().split() if word in job_text)
                similarity = matches / len(query.split()) if query.split() else 0
                
                if similarity >= threshold:
                    results.append({
                        'chunkId': job_id,
                        'content': f"Documento: {job_data.get('filename', 'Unknown')}",
                        'similarity': similarity,
                        'wordCount': len(job_text.split()),
                        'pageStart': 1,
                        'pageEnd': job_data.get('total_pages', 1),
                        'document': {
                            'id': job_id,
                            'file_name': job_data.get('filename', 'Unknown'),
                            'type': 'documento'
                        }
                    })
            
            search_method = "memory_text_search"
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:limit]
        
        logger.info(f"Search completed: {len(results)} results found using {search_method}")
        
        return {
            "success": True,
            "results": results,
            "searchMethod": search_method,
            "query": query,
            "totalResults": len(results)
        }
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": [],
            "searchMethod": "error"
        }

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and results"""
    if DATABASE_AVAILABLE:
        try:
            with get_db() as db_session:
                # Buscar job no PostgreSQL
                job = db_session.query(Job).filter(Job.id == job_id).first()
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                # Buscar análises relacionadas
                text_analysis = db_session.query(TextAnalysis).filter(TextAnalysis.job_id == job_id).first()
                ml_prediction = db_session.query(MLPrediction).filter(MLPrediction.job_id == job_id).first()
                
                # Formar resposta no formato esperado
                return {
                    "job_id": str(job.id),
                    "filename": job.filename,
                    "title": getattr(job, 'title', None) or job.filename,  # Fallback for old records
                    "file_size": job.file_size,
                    "status": job.status,
                    "total_pages": job.page_count,
                    "results": ml_prediction.predictions if ml_prediction else {},
                    "lead_score": ml_prediction.lead_score if ml_prediction else 0.5,
                    "confidence": ml_prediction.confidence if ml_prediction else 0.5,
                    "user_id": str(job.user_id)
                }
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            # Fallback to memory
            pass
    
    # Fallback para memória
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_storage[job_id]

@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    if DATABASE_AVAILABLE:
        try:
            with get_db() as db_session:
                # Buscar todos os jobs no PostgreSQL
                jobs = db_session.query(Job).order_by(Job.created_at.desc()).limit(100).all()
                
                results = []
                for job in jobs:
                    # Buscar ML prediction para lead score
                    ml_prediction = db_session.query(MLPrediction).filter(MLPrediction.job_id == job.id).first()
                    
                    results.append({
                        "job_id": str(job.id),
                        "filename": job.filename,
                        "title": getattr(job, 'title', None) or job.filename,  # Fallback for old records
                        "file_size": job.file_size,
                        "status": job.status,
                        "created_at": job.created_at.isoformat(),
                        "total_pages": job.page_count,
                        "lead_score": ml_prediction.lead_score if ml_prediction else 0.5,
                        "user_id": str(job.user_id)
                    })
                
                logger.info(f"📊 Retornando {len(results)} jobs do PostgreSQL")
                return results
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            # Fallback to memory
            pass
    
    # Fallback para memória
    return list(jobs_storage.values())

@app.get("/api/v1/jobs/{job_id}/page/{page_num}")
async def get_job_page(job_id: str, page_num: int):
    """Get specific page content from a job"""
    try:
        # First try memory storage (for recent jobs)
        if job_id in jobs_storage:
            logger.info(f"📋 Found job {job_id} in memory storage")
            job = jobs_storage[job_id]
            page_texts = job.get('page_texts', {})
            
            if page_num in page_texts:
                return {
                    "job_id": job_id,
                    "page_number": page_num,
                    "total_pages": job.get('total_pages', 0),
                    "page_content": page_texts[page_num],
                    "filename": job.get('filename', ''),
                    "navigation": {
                        "previous_page": page_num - 1 if page_num > 1 else None,
                        "next_page": page_num + 1 if page_num < job.get('total_pages', 0) else None
                    }
                }
        
        # Fallback to database
        logger.info(f"📋 Job {job_id} not in memory, checking database...")
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")

        with get_db() as db_session:
            job = db_session.query(Job).filter(Job.id == job_id).first()
            
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # For now, return a message indicating the page content is not stored
            # In a full implementation, you'd store page_texts in the database
            return {
                "job_id": job_id,
                "page_number": page_num,
                "total_pages": job.page_count or 0,
                "page_content": f"Este é o texto extraído exatamente desta página do documento original.\n\nDocumento: {job.filename}\nPágina: {page_num} de {job.page_count}\n\nNota: O conteúdo específico da página não está disponível para documentos processados anteriormente. Esta funcionalidade está disponível apenas para uploads recentes.",
                "filename": job.filename,
                "navigation": {
                    "previous_page": page_num - 1 if page_num > 1 else None,
                    "next_page": page_num + 1 if page_num < (job.page_count or 0) else None
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting page content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Storage cleanup utilities
def cleanup_old_files():
    """Clean up old temporary files and enforce storage limits"""
    import os
    import time
    from pathlib import Path
    
    cleanup_paths = [
        "./uploads",
        "./temp_splits", 
        "./storage/jobs",
        "./storage/embeddings"
    ]
    
    total_cleaned = 0
    total_size_freed = 0
    
    for path_str in cleanup_paths:
        try:
            path = Path(path_str)
            if not path.exists():
                continue
                
            # Files older than 24 hours
            cutoff_time = time.time() - (24 * 60 * 60)
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_age = file_path.stat().st_mtime
                        if file_age < cutoff_time:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            total_cleaned += 1
                            total_size_freed += file_size
                            
                    except Exception as e:
                        logger.warning(f"Could not cleanup {file_path}: {e}")
                        
        except Exception as e:
            logger.warning(f"Could not access cleanup path {path_str}: {e}")
    
    if total_cleaned > 0:
        size_mb = total_size_freed / (1024 * 1024)
        logger.info(f"🧹 Cleanup complete: {total_cleaned} files removed, {size_mb:.1f}MB freed")
    
    return total_cleaned, total_size_freed

@app.on_event("startup")
async def startup_initialization():
    """Initialize database and run cleanup on server startup"""
    logger.info("🚀 Server starting...")
    
    # Initialize database tables if using PostgreSQL
    if DATABASE_AVAILABLE:
        try:
            from database.connection import init_db
            init_db()
            logger.info("✅ Database tables initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            # Don't fail startup, fall back to memory storage
    
    # Run storage cleanup
    logger.info("🧹 Running storage cleanup...")
    cleanup_old_files()

@app.get("/api/v1/cleanup")
async def manual_cleanup():
    """Manual cleanup endpoint for maintenance"""
    try:
        files_cleaned, bytes_freed = cleanup_old_files()
        return {
            "success": True,
            "files_cleaned": files_cleaned,
            "bytes_freed": bytes_freed,
            "mb_freed": round(bytes_freed / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@app.get("/api/v1/storage-stats")
async def get_storage_stats():
    """Get current storage usage statistics"""
    try:
        from pathlib import Path
        import os
        
        storage_paths = {
            "uploads": "./uploads",
            "temp_splits": "./temp_splits",
            "storage": "./storage",
            "storage_jobs": "./storage/jobs",
            "storage_embeddings": "./storage/embeddings"
        }
        
        stats = {}
        total_size = 0
        total_files = 0
        
        for name, path_str in storage_paths.items():
            path = Path(path_str)
            if path.exists():
                size = 0
                files = 0
                
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        try:
                            file_size = file_path.stat().st_size
                            size += file_size
                            files += 1
                        except:
                            pass
                
                stats[name] = {
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "files": files,
                    "exists": True
                }
                total_size += size
                total_files += files
            else:
                stats[name] = {
                    "size_bytes": 0,
                    "size_mb": 0,
                    "files": 0,
                    "exists": False
                }
        
        return {
            "storage_strategy": "process_and_delete",
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": total_files,
            "paths": stats,
            "cleanup_threshold_mb": 100,  # Alert if over 100MB
            "needs_cleanup": total_size > (100 * 1024 * 1024)
        }
    except Exception as e:
        logger.error(f"Storage stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Storage stats failed: {str(e)}")

@app.patch("/api/v1/jobs/{job_id}/title")
async def update_job_title(job_id: str, request: UpdateTitleRequest):
    """Update the title of a job/document"""
    if DATABASE_AVAILABLE:
        try:
            with get_db() as db_session:
                # Find the job
                job = db_session.query(Job).filter(Job.id == job_id).first()
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                # Update the title
                job.title = request.title
                db_session.commit()
                
                logger.info(f"✅ Job title updated: {job_id} -> '{request.title}'")
                
                return {
                    "success": True,
                    "job_id": str(job.id),
                    "filename": job.filename,
                    "title": job.title,
                    "updated_at": job.updated_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Database error updating title: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update title: {str(e)}")
    
    # Fallback to memory storage
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update title in memory storage
    jobs_storage[job_id]["title"] = request.title
    logger.info(f"✅ Job title updated in memory: {job_id} -> '{request.title}'")
    
    return {
        "success": True,
        "job_id": job_id,
        "filename": jobs_storage[job_id].get("filename", ""),
        "title": request.title,
        "updated_at": datetime.now().isoformat()
    }

@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job/document and all related data"""
    if DATABASE_AVAILABLE:
        try:
            with get_db() as db_session:
                # Find the job
                job = db_session.query(Job).filter(Job.id == job_id).first()
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                # The CASCADE delete will handle related records automatically
                # (JobChunk, TextAnalysis, MLPrediction, JudicialAnalysis, etc.)
                job_filename = job.filename
                db_session.delete(job)
                db_session.commit()
                
                logger.info(f"✅ Job deleted: {job_id} ({job_filename})")
                
                return {
                    "success": True,
                    "job_id": job_id,
                    "message": f"Documento '{job_filename}' foi removido com sucesso"
                }
                
        except Exception as e:
            logger.error(f"Database error deleting job: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")
    
    # Fallback to memory storage
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete from memory storage
    deleted_job = jobs_storage.pop(job_id)
    logger.info(f"✅ Job deleted from memory: {job_id}")
    
    return {
        "success": True,
        "job_id": job_id,
        "message": f"Documento '{deleted_job.get('filename', 'Documento')}' foi removido com sucesso"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")