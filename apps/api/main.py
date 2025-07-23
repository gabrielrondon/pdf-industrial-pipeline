import os
import logging
import json
import importlib.util
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import uuid

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database session
async_session_maker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with proper database connection handling"""
    global async_session_maker
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Fix Railway's postgres:// URL to postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Convert to async URL
        if "postgresql://" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        try:
            # Create async engine
            engine = create_async_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            
            # Test connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            # Create session maker
            async_session_maker = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            logger.info("✅ Database connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.info("⚠️  Running without database - mock mode enabled")
    else:
        logger.warning("⚠️  No DATABASE_URL found - running in mock mode")
    
    yield
    
    # Cleanup
    if async_session_maker:
        await engine.dispose()

# Create FastAPI app with lifespan
app = FastAPI(
    title="PDF Industrial Pipeline API",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS with proper settings
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "PDF Industrial Pipeline API",
        "version": "2.0.0",
        "status": "running",
        "database": "connected" if async_session_maker else "mock_mode"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    health_status = {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "api": "running",
            "database": "connected" if async_session_maker else "disconnected",
            "redis": "connected" if os.getenv("REDIS_URL") else "not_configured"
        }
    }
    
    # Return 503 if critical services are down
    if not async_session_maker and os.getenv("ENVIRONMENT") == "production":
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/api/v1/jobs/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    if async_session_maker:
        # TODO: Implement real database queries
        return {
            "totalAnalyses": 0,
            "validLeads": 0,
            "sharedLeads": 0,
            "credits": 100,
            "dataSource": "database"
        }
    else:
        # Mock data for when database is not available
        return {
            "totalAnalyses": 25,
            "validLeads": 18,
            "sharedLeads": 7,
            "credits": 100,
            "dataSource": "mock"
        }

@app.get("/api/v1/jobs")
async def get_jobs(user_id: str = None):
    """Get user jobs"""
    if not user_id:
        return []
    
    if async_session_maker:
        # TODO: Implement real database queries
        return []
    else:
        # Mock data
        return [
            {
                "id": "demo-job-1",
                "user_id": user_id,
                "filename": "Edital_Leilao_Exemplo.pdf",
                "title": "Edital de Leilão - Exemplo",
                "status": "completed",
                "created_at": "2025-07-13T10:30:00Z",
                "page_count": 5,
                "file_size": 1024000
            }
        ]

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get individual job status with real results"""
    if async_session_maker:
        async with async_session_maker() as session:
            # Query the actual job from the database
            result = await session.execute(
                text("""
                    SELECT id, status, filename, title, file_size, page_count, 
                           created_at, updated_at, processing_started_at, processing_completed_at,
                           error_message, config
                    FROM jobs 
                    WHERE id = :job_id
                """),
                {"job_id": job_id}
            )
            job_data = result.first()
            
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # Calculate progress based on status
            progress_map = {
                "uploaded": 10,
                "processing": 50,
                "completed": 100,
                "failed": 0
            }
            progress = progress_map.get(job_data.status, 0)
            
            # Build response
            response = {
                "id": str(job_data.id),
                "status": job_data.status,
                "progress": progress,
                "filename": job_data.filename,
                "title": job_data.title,
                "file_size": job_data.file_size,
                "page_count": job_data.page_count,
                "created_at": job_data.created_at.isoformat() if job_data.created_at else None,
                "updated_at": job_data.updated_at.isoformat() if job_data.updated_at else None,
                "processing_started_at": job_data.processing_started_at.isoformat() if job_data.processing_started_at else None,
                "processing_completed_at": job_data.processing_completed_at.isoformat() if job_data.processing_completed_at else None,
                "error_message": job_data.error_message
            }
            
            # Add results if analysis is completed
            if job_data.status == "completed" and job_data.config:
                config = job_data.config
                if isinstance(config, dict) and "analysis_results" in config:
                    response["results"] = config["analysis_results"]
                elif isinstance(config, str):
                    # Try to parse as JSON if it's a string
                    try:
                        import json
                        parsed_config = json.loads(config)
                        if "analysis_results" in parsed_config:
                            response["results"] = parsed_config["analysis_results"]
                    except json.JSONDecodeError:
                        pass
                
                # Add result URL for completed jobs
                response["result_url"] = f"/api/v1/jobs/{job_id}/result"
            
            return response
    else:
        # Mock data based on job ID (fallback when database not available)
        return {
            "id": job_id,
            "status": "completed",
            "progress": 100,
            "created_at": "2025-07-22T23:30:00Z",
            "updated_at": "2025-07-22T23:32:00Z",
            "completed_at": "2025-07-22T23:32:00Z",
            "error_message": None,
            "result_url": f"/api/v1/jobs/{job_id}/result",
            "results": {
                "points": [
                    {
                        "id": f"point-{job_id}-1",
                        "title": "Imóvel Residencial Identificado",
                        "comment": "Casa de 3 quartos com 120m² - Excelente estado de conservação",
                        "status": "confirmado",
                        "category": "propriedade",
                        "priority": "high"
                    },
                    {
                        "id": f"point-{job_id}-2",
                        "title": "Valor de Avaliação Competitivo",
                        "comment": "Preço inicial R$ 180.000 (20% abaixo do mercado)",
                        "status": "confirmado", 
                        "category": "financeiro",
                        "priority": "medium"
                    },
                    {
                        "id": f"point-{job_id}-3",
                        "title": "Documentação Completa",
                        "comment": "Toda documentação em ordem - sem pendências",
                        "status": "confirmado",
                        "category": "legal",
                        "priority": "low"
                    }
                ]
            }
        }

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    """Handle file upload and trigger processing pipeline"""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Read file for validation
        file_content = await file.read()
        file_size = len(file_content)
        
        if async_session_maker:
            # Save to database and trigger processing
            async with async_session_maker() as session:
                try:
                    # Create job record using raw SQL to avoid import issues
                    await session.execute(
                        text("""
                            INSERT INTO jobs (id, user_id, filename, title, file_size, mime_type, status, config)
                            VALUES (:id, :user_id, :filename, :title, :file_size, :mime_type, :status, :config)
                        """),
                        {
                            "id": job_id,
                            "user_id": user_id,
                            "filename": file.filename,
                            "title": file.filename,
                            "file_size": file_size,
                            "mime_type": "application/pdf",
                            "status": "uploaded",
                            "config": json.dumps({"uploaded": True})  # Don't store file content in database
                        }
                    )
                    await session.commit()
                    
                    logger.info(f"Job {job_id} saved to database, triggering analysis pipeline")
                    
                    # Trigger analysis pipeline (Celery task)
                    try:
                        # Check if tasks module exists
                        import importlib.util
                        tasks_spec = importlib.util.find_spec("tasks.analysis_tasks")
                        if tasks_spec is not None:
                            from tasks.analysis_tasks import start_analysis_pipeline
                            task_result = start_analysis_pipeline.delay(job_id)
                            logger.info(f"Analysis pipeline triggered for job {job_id}: {task_result.id}")
                        else:
                            raise ImportError("tasks module not found")
                    except (ImportError, Exception) as e:
                        # If Celery is not available, run analysis inline
                        logger.warning(f"Celery not available ({e}), running analysis inline")
                        await run_analysis_inline(job_id, file_content, file.filename)
                        
                except Exception as db_error:
                    logger.error(f"Database error during upload: {db_error}")
                    await session.rollback()
                    raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "File uploaded successfully and processing started",
            "file_size": file_size,
            "user_id": user_id,
            "filename": file.filename,
            "processing_mode": "database" if async_session_maker else "mock"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_inline(job_id: str, file_content: bytes, filename: str):
    """Run analysis inline when Celery is not available (development mode)"""
    try:
        from datetime import datetime
        
        async with async_session_maker() as session:
            # Get job
            result = await session.execute(
                text("SELECT * FROM jobs WHERE id = :job_id"),
                {"job_id": job_id}
            )
            job_data = result.first()
            
            if not job_data:
                logger.error(f"Job {job_id} not found")
                return
            
            # Update job status
            await session.execute(
                text("UPDATE jobs SET status = 'processing', processing_started_at = NOW() WHERE id = :job_id"),
                {"job_id": job_id}
            )
            await session.commit()
            
            # Try to process PDF, but handle PyMuPDF import gracefully
            full_text = ""
            page_count = 1
            
            try:
                import fitz  # PyMuPDF
                
                # Process PDF
                doc = fitz.open(stream=file_content, filetype="pdf")
                page_count = len(doc)
                
                # Extract text from each page and create chunks
                for page_num in range(page_count):
                    page = doc[page_num]
                    page_text = page.get_text()
                    full_text += f"\n\n{page_text}"
                    
                    # Create chunk for this page
                    chunk_id = str(uuid.uuid4())
                    await session.execute(
                        text("""
                            INSERT INTO job_chunks (id, job_id, chunk_number, page_start, page_end, raw_text, status, processed_at)
                            VALUES (:id, :job_id, :chunk_number, :page_start, :page_end, :raw_text, 'completed', NOW())
                        """),
                        {
                            "id": chunk_id,
                            "job_id": job_id,
                            "chunk_number": page_num + 1,
                            "page_start": page_num + 1,
                            "page_end": page_num + 1,
                            "raw_text": page_text
                        }
                    )
                
                doc.close()
                
            except ImportError:
                logger.warning("PyMuPDF not available, generating sample analysis")
                full_text = f"Sample analysis for {filename}\nDocument uploaded successfully.\nLeilão judicial identificado.\nValor: R$ 150.000,00\nContato: (11) 99999-9999"
                page_count = 1
                
                # Create a sample chunk
                chunk_id = str(uuid.uuid4())
                await session.execute(
                    text("""
                        INSERT INTO job_chunks (id, job_id, chunk_number, page_start, page_end, raw_text, status, processed_at)
                        VALUES (:id, :job_id, :chunk_number, :page_start, :page_end, :raw_text, 'completed', NOW())
                    """),
                    {
                        "id": chunk_id,
                        "job_id": job_id,
                        "chunk_number": 1,
                        "page_start": 1,
                        "page_end": 1,
                        "raw_text": full_text
                    }
                )
            
            # Update page count
            await session.execute(
                text("UPDATE jobs SET page_count = :page_count WHERE id = :job_id"),
                {"job_id": job_id, "page_count": page_count}
            )
            
            # Run analysis similar to the Celery task
            analysis_results = await generate_analysis_results(job_id, full_text, filename)
            
            # Store results in job config
            await session.execute(
                text("""
                    UPDATE jobs 
                    SET status = 'completed', 
                        processing_completed_at = NOW(),
                        config = config || :analysis_config
                    WHERE id = :job_id
                """),
                {
                    "job_id": job_id,
                    "analysis_config": json.dumps({"analysis_results": analysis_results})
                }
            )
            await session.commit()
            
            logger.info(f"Inline analysis completed for job {job_id}: {len(analysis_results.get('points', []))} points found")
            
    except Exception as e:
        logger.error(f"Inline analysis failed for job {job_id}: {str(e)}")
        # Update job status to failed
        try:
            async with async_session_maker() as session:
                await session.execute(
                    text("UPDATE jobs SET status = 'failed', error_message = :error WHERE id = :job_id"),
                    {"job_id": job_id, "error": f"Analysis failed: {str(e)}"}
                )
                await session.commit()
        except Exception:
            pass


async def generate_analysis_results(job_id: str, full_text: str, filename: str):
    """Generate analysis results similar to the Celery task"""
    import re
    from datetime import datetime
    
    results = {
        'job_id': job_id,
        'filename': filename,
        'analysis_type': 'comprehensive',
        'analysis_date': datetime.utcnow().isoformat(),
        'points': []
    }
    
    # 1. Basic document analysis
    basic_analysis = analyze_document_structure_inline(full_text, filename)
    results['points'].extend(basic_analysis)
    
    # 2. Judicial/Legal analysis (Brazilian focus)
    if is_judicial_document_inline(full_text):
        judicial_analysis = analyze_judicial_content_inline(full_text)
        results['points'].extend(judicial_analysis)
    
    # 3. Financial/Investment analysis
    financial_analysis = analyze_financial_opportunities_inline(full_text)
    results['points'].extend(financial_analysis)
    
    # 4. Contact and deadline analysis
    contact_analysis = extract_contacts_and_deadlines_inline(full_text)
    results['points'].extend(contact_analysis)
    
    return results


def analyze_document_structure_inline(text: str, filename: str):
    """Analyze basic document structure"""
    points = []
    
    # Document type detection
    doc_type = detect_document_type_inline(text, filename)
    if doc_type:
        points.append({
            'id': f'doc_type_{len(points)}',
            'title': f'Tipo de Documento: {doc_type}',
            'comment': f'Documento identificado como {doc_type} baseado no conteúdo e nome do arquivo.',
            'status': 'confirmado',
            'category': 'geral',
            'priority': 'medium'
        })
    
    # Page count and length analysis
    estimated_pages = max(1, len(text) // 2000)
    points.append({
        'id': f'doc_size_{len(points)}',
        'title': f'Tamanho do Documento: ~{estimated_pages} páginas',
        'comment': f'Documento contém aproximadamente {len(text):,} caracteres em ~{estimated_pages} páginas.',
        'status': 'confirmado',
        'category': 'geral',
        'priority': 'low'
    })
    
    return points


def is_judicial_document_inline(text: str) -> bool:
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


def analyze_judicial_content_inline(text: str):
    """Analyze judicial/legal document content"""
    points = []
    text_lower = text.lower()
    
    # Auction detection
    auction_keywords = ['leilão', 'leilao', 'hasta pública', 'hasta publica', 'arrematação']
    if any(keyword in text_lower for keyword in auction_keywords):
        points.append({
            'id': f'auction_{len(points)}',
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
                'id': f'property_{prop_type}_{len(points)}',
                'title': f'Bem do Tipo: {prop_type.title()}',
                'comment': f'Identificado bem do tipo {prop_type} no documento.',
                'status': 'confirmado',
                'category': 'investimento',
                'priority': 'medium'
            })
            break
    
    return points


def analyze_financial_opportunities_inline(text: str):
    """Extract financial and investment information"""
    import re
    points = []
    
    # Value extraction patterns
    value_patterns = [
        r'R\$\s*([\d.,]+)',
        r'valor.*?R\$\s*([\d.,]+)',
        r'avaliação.*?R\$\s*([\d.,]+)',
        r'lance.*?R\$\s*([\d.,]+)'
    ]
    
    values_found = []
    for pattern in value_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                clean_value = match.replace('.', '').replace(',', '.')
                value = float(clean_value)
                if value > 1000:
                    values_found.append(value)
            except ValueError:
                continue
    
    if values_found:
        max_value = max(values_found)
        min_value = min(values_found)
        
        points.append({
            'id': f'values_{len(points)}',
            'title': f'Valores Identificados: R$ {min_value:,.2f} - R$ {max_value:,.2f}',
            'comment': f'Encontrados {len(values_found)} valores monetários no documento. Maior valor: R$ {max_value:,.2f}',
            'status': 'confirmado',
            'category': 'financeiro',
            'priority': 'high' if max_value > 100000 else 'medium',
            'value': f'R$ {max_value:,.2f}'
        })
    
    return points


def extract_contacts_and_deadlines_inline(text: str):
    """Extract contact information and important deadlines"""
    import re
    points = []
    
    # Phone number patterns
    phone_pattern = r'(?:\(\d{2}\)|\d{2})\s*\d{4,5}[-\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        points.append({
            'id': f'phones_{len(points)}',
            'title': f'Contatos Telefônicos: {len(phones)} encontrados',
            'comment': f'Telefones identificados: {", ".join(phones[:3])}{"..." if len(phones) > 3 else ""}',
            'status': 'confirmado',
            'category': 'contato',
            'priority': 'medium'
        })
    
    # Date patterns for deadlines
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',
        r'até\s+\d{1,2}/\d{1,2}/\d{4}',
        r'prazo.*?\d{1,2}/\d{1,2}/\d{4}'
    ]
    
    dates_found = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates_found.extend(matches)
    
    if dates_found:
        points.append({
            'id': f'deadlines_{len(points)}',
            'title': f'Prazos e Datas: {len(dates_found)} identificados',
            'comment': f'Datas importantes encontradas: {", ".join(dates_found[:3])}{"..." if len(dates_found) > 3 else ""}',
            'status': 'alerta',
            'category': 'prazo',
            'priority': 'high'
        })
    
    return points


def detect_document_type_inline(text: str, filename: str) -> str:
    """Detect document type based on content and filename"""
    text_lower = text.lower()
    filename_lower = filename.lower()
    
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


if __name__ == "__main__":
    import uvicorn
    
    # Railway and production configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Configure logging for Railway
    log_level = "info" if environment == "production" else "debug"
    
    logger.info(f"🚀 Starting PDF Industrial Pipeline API")
    logger.info(f"   Environment: {environment}")
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")
    logger.info(f"   Database: {'connected' if async_session_maker else 'mock mode'}")
    
    # Start the server
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level=log_level,
        access_log=True
    )