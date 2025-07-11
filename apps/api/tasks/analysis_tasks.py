from celery import current_task
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime
import re
import json

from celery_app import app
from core.monitoring import track_job_metrics
from core.exceptions import PDFProcessingError
from database.connection import get_db
from database.models import Job, JobChunk

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=2, default_retry_delay=60)
@track_job_metrics(job_type='analysis', stage='judicial')
def start_analysis_pipeline(self, job_id: str) -> Dict[str, Any]:
    """
    Start comprehensive analysis pipeline for processed PDF
    """
    try:
        logger.info(f"Starting analysis pipeline for job {job_id}")
        
        # Get job and chunks
        with get_db() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise PDFProcessingError(f"Job {job_id} not found")
            
            chunks = db.query(JobChunk).filter(JobChunk.job_id == job_id).all()
            if not chunks:
                raise PDFProcessingError(f"No chunks found for job {job_id}")
            
            # Update job status
            job.status = "analyzing"
            db.commit()
        
        # Combine all text from chunks
        full_text = ""
        for chunk in chunks:
            if chunk.processed_text:
                full_text += f"\n\n{chunk.processed_text}"
            elif chunk.raw_text:
                full_text += f"\n\n{chunk.raw_text}"
        
        if not full_text.strip():
            raise PDFProcessingError("No text content found in document")
        
        # Run different analysis modules
        results = {
            'job_id': job_id,
            'filename': job.filename,
            'analysis_type': 'comprehensive',
            'total_pages': job.page_count or len(chunks),
            'analysis_date': datetime.utcnow().isoformat(),
            'points': []
        }
        
        # 1. Basic document analysis
        basic_analysis = analyze_document_structure(full_text, job.filename)
        results['points'].extend(basic_analysis)
        
        # 2. Judicial/Legal analysis (Brazilian focus)
        if is_judicial_document(full_text):
            judicial_analysis = analyze_judicial_content(full_text)
            results['points'].extend(judicial_analysis)
        
        # 3. Financial/Investment analysis
        financial_analysis = analyze_financial_opportunities(full_text)
        results['points'].extend(financial_analysis)
        
        # 4. Contact and deadline analysis
        contact_analysis = extract_contacts_and_deadlines(full_text)
        results['points'].extend(contact_analysis)
        
        # Update job with results
        with get_db() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "completed"
                job.processing_completed_at = datetime.utcnow()
                # Store results in job config
                if not job.config:
                    job.config = {}
                job.config['analysis_results'] = results
                job.config['analysis_summary'] = {
                    'total_points': len(results['points']),
                    'high_priority': len([p for p in results['points'] if p.get('priority') == 'high']),
                    'categories': list(set([p.get('category', 'geral') for p in results['points']]))
                }
                db.commit()
        
        logger.info(f"Analysis completed for job {job_id}: {len(results['points'])} points found")
        return results
        
    except Exception as exc:
        logger.error(f"Analysis failed for job {job_id}: {str(exc)}")
        
        # Update job status
        try:
            with get_db() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = "failed"
                    job.error_message = f"Analysis failed: {str(exc)}"
                    db.commit()
        except Exception:
            pass
        
        raise PDFProcessingError(f"Analysis failed: {str(exc)}", job_id)


def analyze_document_structure(text: str, filename: str) -> List[Dict[str, Any]]:
    """
    Analyze basic document structure and metadata
    """
    points = []
    
    # Document type detection
    doc_type = detect_document_type(text, filename)
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
    estimated_pages = max(1, len(text) // 2000)  # Rough estimate
    points.append({
        'id': f'doc_size_{len(points)}',
        'title': f'Tamanho do Documento: ~{estimated_pages} páginas',
        'comment': f'Documento contém aproximadamente {len(text):,} caracteres em ~{estimated_pages} páginas.',
        'status': 'confirmado',
        'category': 'geral',
        'priority': 'low'
    })
    
    return points


def is_judicial_document(text: str) -> bool:
    """
    Check if document appears to be judicial/legal
    """
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
    """
    Analyze judicial/legal document content
    """
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
            break  # Only add one property type
    
    # Legal compliance (CPC Article 889)
    cpc_indicators = ['art. 889', 'artigo 889', 'cpc 889', 'código de processo civil']
    if any(indicator in text_lower for indicator in cpc_indicators):
        points.append({
            'id': f'cpc_889_{len(points)}',
            'title': 'Referência ao CPC Art. 889',
            'comment': 'Documento faz referência ao Artigo 889 do Código de Processo Civil - verifique conformidade legal.',
            'status': 'alerta',
            'category': 'leilao',
            'priority': 'high'
        })
    
    return points


def analyze_financial_opportunities(text: str) -> List[Dict[str, Any]]:
    """
    Extract financial and investment information
    """
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
                # Clean and convert value
                clean_value = match.replace('.', '').replace(',', '.')
                value = float(clean_value)
                if value > 1000:  # Only significant values
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
    
    # Debt and encumbrance analysis
    debt_keywords = ['dívida', 'divida', 'débito', 'debito', 'ônus', 'onus', 'hipoteca', 'financiamento']
    if any(keyword in text.lower() for keyword in debt_keywords):
        points.append({
            'id': f'debt_{len(points)}',
            'title': 'Possíveis Ônus ou Dívidas',
            'comment': 'Documento menciona possíveis dívidas, ônus ou encargos. Verifique detalhadamente antes de investir.',
            'status': 'alerta',
            'category': 'financeiro',
            'priority': 'high'
        })
    
    return points


def extract_contacts_and_deadlines(text: str) -> List[Dict[str, Any]]:
    """
    Extract contact information and important deadlines
    """
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
    
    # Email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        points.append({
            'id': f'emails_{len(points)}',
            'title': f'E-mails: {len(emails)} encontrados',
            'comment': f'E-mails identificados: {", ".join(emails[:2])}{"..." if len(emails) > 2 else ""}',
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


def detect_document_type(text: str, filename: str) -> str:
    """
    Detect document type based on content and filename
    """
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