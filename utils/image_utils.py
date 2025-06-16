"""
Utilitários para processamento de imagem - Etapa 2 OCR
Funções para melhorar qualidade de imagens antes do OCR
"""

import os
import logging
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import tempfile

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    import cv2
    import numpy as np
    from pdf2image import convert_from_path
    PIL_AVAILABLE = True
    CV2_AVAILABLE = True
    PDF2IMAGE_AVAILABLE = True
except ImportError as e:
    PIL_AVAILABLE = False
    CV2_AVAILABLE = False
    PDF2IMAGE_AVAILABLE = False
    logging.warning(f"Image processing libraries not available: {e}")

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Processador de imagens para melhorar qualidade antes do OCR"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    def pdf_to_images(self, pdf_path: str, output_dir: str, 
                     dpi: int = 300, format: str = 'PNG') -> List[str]:
        """
        Converte páginas PDF em imagens
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            output_dir: Diretório de saída para as imagens
            dpi: Resolução das imagens (padrão: 300 DPI)
            format: Formato das imagens (PNG, JPEG)
            
        Returns:
            Lista com caminhos das imagens geradas
        """
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError("pdf2image não está disponível")
            
        try:
            # Criar diretório de saída se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Converter PDF para imagens
            logger.info(f"Convertendo PDF para imagens: {pdf_path}")
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                output_folder=output_dir,
                fmt=format.lower(),
                thread_count=2  # Usar 2 threads para não sobrecarregar
            )
            
            # Salvar imagens e retornar caminhos
            image_paths = []
            base_name = Path(pdf_path).stem
            
            for i, image in enumerate(images, 1):
                image_path = os.path.join(output_dir, f"{base_name}_page_{i:03d}.{format.lower()}")
                image.save(image_path, format=format, quality=95 if format.upper() == 'JPEG' else None)
                image_paths.append(image_path)
                logger.debug(f"Imagem salva: {image_path}")
                
            logger.info(f"Convertidas {len(image_paths)} páginas para imagens")
            return image_paths
            
        except Exception as e:
            logger.error(f"Erro ao converter PDF para imagens: {e}")
            raise
    
    def preprocess_image(self, image_path: str, output_path: str = None,
                        enhance_contrast: bool = True,
                        enhance_sharpness: bool = True,
                        remove_noise: bool = True,
                        binarize: bool = False,
                        auto_rotate: bool = True) -> str:
        """
        Pré-processa imagem para melhorar qualidade do OCR
        
        Args:
            image_path: Caminho da imagem original
            output_path: Caminho de saída (opcional)
            enhance_contrast: Melhorar contraste
            enhance_sharpness: Melhorar nitidez
            remove_noise: Remover ruído
            binarize: Converter para preto e branco
            auto_rotate: Correção automática de rotação
            
        Returns:
            Caminho da imagem processada
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow não está disponível")
            
        try:
            # Abrir imagem
            image = Image.open(image_path)
            logger.debug(f"Processando imagem: {image_path} ({image.size})")
            
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Correção automática de rotação (usando OpenCV se disponível)
            if auto_rotate and CV2_AVAILABLE:
                image = self._auto_rotate_image(image)
            
            # Melhorar contraste
            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)  # Aumentar contraste em 20%
                
            # Melhorar nitidez
            if enhance_sharpness:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.1)  # Aumentar nitidez em 10%
            
            # Remover ruído
            if remove_noise:
                image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Binarização (preto e branco)
            if binarize:
                image = ImageOps.grayscale(image)
                # Aplicar threshold adaptativo
                if CV2_AVAILABLE:
                    image = self._adaptive_threshold(image)
                else:
                    # Threshold simples se OpenCV não estiver disponível
                    image = ImageOps.autocontrast(image)
            
            # Definir caminho de saída
            if output_path is None:
                base_name = Path(image_path).stem
                output_path = os.path.join(
                    os.path.dirname(image_path),
                    f"{base_name}_processed.png"
                )
            
            # Salvar imagem processada
            image.save(output_path, 'PNG', quality=95)
            logger.debug(f"Imagem processada salva: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            raise
    
    def _auto_rotate_image(self, image: Image.Image) -> Image.Image:
        """
        Detecta e corrige rotação da imagem usando OpenCV
        """
        try:
            # Converter PIL para OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Detectar linhas usando Hough Transform
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calcular ângulo médio das linhas
                angles = []
                for rho, theta in lines[:10]:  # Usar apenas as 10 primeiras linhas
                    angle = theta * 180 / np.pi
                    if angle > 90:
                        angle = angle - 180
                    angles.append(angle)
                
                if angles:
                    median_angle = np.median(angles)
                    
                    # Rotacionar apenas se o ângulo for significativo
                    if abs(median_angle) > 0.5:
                        logger.debug(f"Rotacionando imagem em {median_angle:.2f} graus")
                        image = image.rotate(-median_angle, expand=True, fillcolor='white')
            
            return image
            
        except Exception as e:
            logger.warning(f"Erro na correção automática de rotação: {e}")
            return image
    
    def _adaptive_threshold(self, image: Image.Image) -> Image.Image:
        """
        Aplica threshold adaptativo usando OpenCV
        """
        try:
            # Converter PIL para OpenCV
            cv_image = np.array(image)
            
            # Aplicar threshold adaptativo
            adaptive_thresh = cv2.adaptiveThreshold(
                cv_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Converter de volta para PIL
            return Image.fromarray(adaptive_thresh)
            
        except Exception as e:
            logger.warning(f"Erro no threshold adaptativo: {e}")
            return image
    
    def batch_preprocess(self, image_paths: List[str], output_dir: str,
                        **preprocessing_options) -> List[str]:
        """
        Processa múltiplas imagens em lote
        
        Args:
            image_paths: Lista de caminhos das imagens
            output_dir: Diretório de saída
            **preprocessing_options: Opções de pré-processamento
            
        Returns:
            Lista com caminhos das imagens processadas
        """
        os.makedirs(output_dir, exist_ok=True)
        processed_paths = []
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                base_name = Path(image_path).stem
                output_path = os.path.join(output_dir, f"{base_name}_processed.png")
                
                processed_path = self.preprocess_image(
                    image_path, output_path, **preprocessing_options
                )
                processed_paths.append(processed_path)
                
                logger.info(f"Processada imagem {i}/{len(image_paths)}: {base_name}")
                
            except Exception as e:
                logger.error(f"Erro ao processar {image_path}: {e}")
                # Continuar com as outras imagens
                continue
        
        logger.info(f"Processamento em lote concluído: {len(processed_paths)}/{len(image_paths)} imagens")
        return processed_paths
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre uma imagem
        
        Returns:
            Dicionário com informações da imagem
        """
        try:
            with Image.open(image_path) as image:
                return {
                    'path': image_path,
                    'size': image.size,
                    'mode': image.mode,
                    'format': image.format,
                    'file_size': os.path.getsize(image_path),
                    'dpi': image.info.get('dpi', (72, 72))
                }
        except Exception as e:
            logger.error(f"Erro ao obter informações da imagem: {e}")
            return {'path': image_path, 'error': str(e)}

# Instância global do processador
image_processor = ImageProcessor() 