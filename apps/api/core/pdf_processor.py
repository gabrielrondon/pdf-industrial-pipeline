import os
import hashlib
import asyncio
from typing import List, Dict, Tuple, Optional, AsyncGenerator
from pathlib import Path
import aiofiles
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass
from datetime import datetime

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class PDFChunk:
    """Represents a chunk of PDF pages"""
    chunk_id: str
    job_id: str
    chunk_number: int
    page_start: int
    page_end: int
    content: Optional[str] = None
    images: List[Dict] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PDFMetadata:
    """PDF document metadata"""
    filename: str
    file_size: int
    file_hash: str
    page_count: int
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    is_encrypted: bool = False
    is_form: bool = False
    has_images: bool = False
    has_tables: bool = False


class PDFProcessor:
    """Advanced PDF processor with intelligent chunking and streaming support"""
    
    def __init__(self, storage_backend=None):
        self.storage_backend = storage_backend
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def process_pdf_stream(
        self,
        file_path: str,
        job_id: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> AsyncGenerator[PDFChunk, None]:
        """
        Process PDF in streaming fashion, yielding chunks as they're ready
        """
        chunk_size = chunk_size or settings.pdf_chunk_size
        chunk_overlap = chunk_overlap or settings.pdf_chunk_overlap
        
        try:
            # Get PDF metadata first
            metadata = await self.extract_metadata(file_path)
            
            # Calculate chunking strategy
            chunks_info = self._calculate_chunks(
                metadata.page_count,
                chunk_size,
                chunk_overlap
            )
            
            # Process chunks in parallel
            tasks = []
            for chunk_info in chunks_info:
                task = asyncio.create_task(
                    self._process_chunk(
                        file_path,
                        job_id,
                        chunk_info['chunk_number'],
                        chunk_info['start'],
                        chunk_info['end']
                    )
                )
                tasks.append(task)
            
            # Yield chunks as they complete
            for coro in asyncio.as_completed(tasks):
                chunk = await coro
                if chunk:
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error processing PDF stream: {str(e)}")
            raise
    
    async def extract_metadata(self, file_path: str) -> PDFMetadata:
        """Extract comprehensive metadata from PDF"""
        def _extract():
            doc = fitz.open(file_path)
            
            # Basic metadata
            metadata = doc.metadata
            
            # File info
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Check for features
            has_images = False
            has_tables = False
            is_form = len(doc.get_widgets()) > 0
            
            for page in doc:
                if len(page.get_images()) > 0:
                    has_images = True
                # Simple table detection (can be enhanced)
                if "table" in page.get_text().lower():
                    has_tables = True
                    
                if has_images and has_tables:
                    break
            
            doc.close()
            
            return PDFMetadata(
                filename=os.path.basename(file_path),
                file_size=file_size,
                file_hash=file_hash,
                page_count=len(doc),
                title=metadata.get('title'),
                author=metadata.get('author'),
                subject=metadata.get('subject'),
                keywords=metadata.get('keywords'),
                creator=metadata.get('creator'),
                producer=metadata.get('producer'),
                creation_date=metadata.get('creationDate'),
                modification_date=metadata.get('modDate'),
                is_encrypted=doc.is_encrypted,
                is_form=is_form,
                has_images=has_images,
                has_tables=has_tables
            )
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)
    
    def _calculate_chunks(
        self,
        total_pages: int,
        chunk_size: int,
        overlap: int
    ) -> List[Dict]:
        """
        Calculate optimal chunking strategy with overlap
        """
        chunks = []
        chunk_number = 0
        
        # Adjust chunk size for very small documents
        if total_pages <= chunk_size:
            return [{
                'chunk_number': 0,
                'start': 0,
                'end': total_pages - 1
            }]
        
        current_page = 0
        while current_page < total_pages:
            start = current_page
            end = min(current_page + chunk_size - 1, total_pages - 1)
            
            chunks.append({
                'chunk_number': chunk_number,
                'start': start,
                'end': end
            })
            
            # Move to next chunk with overlap
            current_page = end + 1 - overlap if overlap > 0 else end + 1
            chunk_number += 1
        
        return chunks
    
    async def _process_chunk(
        self,
        file_path: str,
        job_id: str,
        chunk_number: int,
        start_page: int,
        end_page: int
    ) -> PDFChunk:
        """Process a single chunk of PDF pages"""
        def _extract_chunk():
            doc = fitz.open(file_path)
            
            chunk_text = []
            chunk_images = []
            
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text()
                chunk_text.append(f"--- Page {page_num + 1} ---\n{text}")
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = {
                            'page': page_num + 1,
                            'index': img_index,
                            'width': pix.width,
                            'height': pix.height,
                            'colorspace': pix.colorspace.name,
                            'size': len(pix.samples)
                        }
                        chunk_images.append(img_data)
                    
                    pix = None
            
            doc.close()
            
            return "\n\n".join(chunk_text), chunk_images
        
        try:
            loop = asyncio.get_event_loop()
            text, images = await loop.run_in_executor(
                self.executor,
                _extract_chunk
            )
            
            chunk_id = f"{job_id}_chunk_{chunk_number}"
            
            return PDFChunk(
                chunk_id=chunk_id,
                job_id=job_id,
                chunk_number=chunk_number,
                page_start=start_page + 1,  # 1-indexed for display
                page_end=end_page + 1,
                content=text,
                images=images,
                metadata={
                    'extraction_method': 'pymupdf',
                    'has_images': len(images) > 0,
                    'text_length': len(text)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_number}: {str(e)}")
            return None
    
    async def split_pdf_optimized(
        self,
        file_path: str,
        output_dir: str,
        job_id: str
    ) -> List[str]:
        """
        Split PDF into individual pages optimized for large files
        """
        output_files = []
        
        def _split_pages():
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                # Create new PDF with single page
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # Save page
                output_file = os.path.join(
                    output_dir,
                    f"{job_id}_page_{page_num + 1:04d}.pdf"
                )
                new_doc.save(output_file, garbage=4, deflate=True)
                new_doc.close()
                
                output_files.append(output_file)
            
            doc.close()
            return output_files
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _split_pages)
    
    async def extract_tables(self, file_path: str) -> List[Dict]:
        """Extract tables from PDF using advanced detection"""
        # This is a placeholder - in production, integrate with
        # libraries like camelot-py or tabula-py
        tables = []
        
        def _extract():
            try:
                import camelot
                tables_data = camelot.read_pdf(
                    file_path,
                    pages='all',
                    flavor='lattice',
                    line_scale=40
                )
                
                for i, table in enumerate(tables_data):
                    tables.append({
                        'page': table.page,
                        'data': table.df.to_dict('records'),
                        'accuracy': table.accuracy
                    })
                    
            except Exception as e:
                logger.warning(f"Table extraction failed: {str(e)}")
                
            return tables
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)
    
    async def validate_pdf(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate PDF file for processing
        Returns: (is_valid, error_message)
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > settings.max_pdf_size_bytes:
                return False, f"File size exceeds maximum allowed ({settings.max_pdf_size_mb}MB)"
            
            # Check if it's a valid PDF
            doc = fitz.open(file_path)
            
            # Check if encrypted and we can't decrypt
            if doc.is_encrypted and not doc.authenticate(""):
                doc.close()
                return False, "PDF is password protected"
            
            # Check page count
            if len(doc) == 0:
                doc.close()
                return False, "PDF has no pages"
            
            doc.close()
            return True, None
            
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
    
    def __del__(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=False)