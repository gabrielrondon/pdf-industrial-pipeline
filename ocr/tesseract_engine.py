"""
Engine de OCR usando Tesseract - Etapa 2
Extração de texto de imagens com suporte a múltiplos idiomas
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError as e:
    TESSERACT_AVAILABLE = False
    logging.warning(f"Tesseract não está disponível: {e}")

logger = logging.getLogger(__name__)

class TesseractEngine:
    """Engine de OCR usando Tesseract com configurações otimizadas"""
    
    # Configurações de idiomas suportados
    SUPPORTED_LANGUAGES = {
        'por': 'Português',
        'eng': 'English', 
        'spa': 'Español',
        'fra': 'Français',
        'deu': 'Deutsch'
    }
    
    # Configurações PSM (Page Segmentation Mode)
    PSM_MODES = {
        'auto': 3,          # Automatic page segmentation (default)
        'single_column': 4, # Single column of text
        'single_block': 6,  # Single uniform block
        'single_line': 7,   # Single text line
        'single_word': 8,   # Single word
        'single_char': 10   # Single character
    }
    
    # Configurações OEM (OCR Engine Mode)
    OEM_MODES = {
        'legacy': 0,        # Legacy engine only
        'lstm': 1,          # Neural nets LSTM engine only
        'combined': 2,      # Legacy + LSTM engines
        'default': 3        # Default (based on what is available)
    }
    
    def __init__(self, 
                 languages: List[str] = None,
                 psm_mode: str = 'auto',
                 oem_mode: str = 'default',
                 tesseract_cmd: str = None):
        """
        Inicializa o engine Tesseract
        
        Args:
            languages: Lista de idiomas (padrão: ['por', 'eng'])
            psm_mode: Modo de segmentação de página
            oem_mode: Modo do engine OCR
            tesseract_cmd: Caminho customizado para o executável tesseract
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError("pytesseract não está disponível")
            
        self.languages = languages or ['por', 'eng']
        self.psm_mode = psm_mode
        self.oem_mode = oem_mode
        
        # Configurar caminho do tesseract se fornecido
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
        # Verificar se tesseract está disponível
        self._verify_tesseract()
        
        # Verificar idiomas disponíveis
        self._verify_languages()
        
        logger.info(f"TesseractEngine inicializado - Idiomas: {self.languages}")
    
    def _verify_tesseract(self):
        """Verifica se o Tesseract está instalado e funcionando"""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract versão: {version}")
        except Exception as e:
            raise RuntimeError(f"Tesseract não está disponível: {e}")
    
    def _verify_languages(self):
        """Verifica se os idiomas solicitados estão disponíveis"""
        try:
            available_langs = pytesseract.get_languages(config='')
            logger.debug(f"Idiomas disponíveis: {available_langs}")
            
            missing_langs = []
            for lang in self.languages:
                if lang not in available_langs:
                    missing_langs.append(lang)
            
            if missing_langs:
                logger.warning(f"Idiomas não disponíveis: {missing_langs}")
                # Remover idiomas não disponíveis
                self.languages = [lang for lang in self.languages if lang in available_langs]
                
            if not self.languages:
                logger.warning("Nenhum idioma disponível, usando inglês como padrão")
                self.languages = ['eng']
                
        except Exception as e:
            logger.warning(f"Erro ao verificar idiomas: {e}")
            self.languages = ['eng']  # Fallback para inglês
    
    def extract_text(self, image_path: str, 
                    confidence_threshold: float = 0.0,
                    custom_config: str = None) -> Dict[str, Any]:
        """
        Extrai texto de uma imagem
        
        Args:
            image_path: Caminho para a imagem
            confidence_threshold: Threshold mínimo de confiança (0-100)
            custom_config: Configuração customizada do Tesseract
            
        Returns:
            Dicionário com texto extraído e metadados
        """
        try:
            # Abrir imagem
            image = Image.open(image_path)
            logger.debug(f"Extraindo texto de: {image_path}")
            
            # Configurar idiomas
            lang_string = '+'.join(self.languages)
            
            # Configuração base do Tesseract
            config = self._build_config(custom_config)
            
            # Extrair texto
            text = pytesseract.image_to_string(
                image, 
                lang=lang_string,
                config=config
            )
            
            # Obter dados detalhados (incluindo confiança)
            data = pytesseract.image_to_data(
                image,
                lang=lang_string,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calcular estatísticas
            stats = self._calculate_stats(data, confidence_threshold)
            
            # Detectar idioma principal
            detected_lang = self._detect_language(text)
            
            result = {
                'text': text.strip(),
                'image_path': image_path,
                'languages_used': self.languages,
                'detected_language': detected_lang,
                'confidence_stats': stats,
                'word_count': len(text.split()),
                'char_count': len(text),
                'extraction_timestamp': datetime.now().isoformat(),
                'tesseract_config': config
            }
            
            logger.info(f"Texto extraído: {len(text)} caracteres, confiança média: {stats['avg_confidence']:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto de {image_path}: {e}")
            return {
                'text': '',
                'image_path': image_path,
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def extract_text_with_boxes(self, image_path: str) -> Dict[str, Any]:
        """
        Extrai texto com informações de posicionamento (bounding boxes)
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dicionário com texto e coordenadas das palavras
        """
        try:
            image = Image.open(image_path)
            lang_string = '+'.join(self.languages)
            config = self._build_config()
            
            # Extrair dados com coordenadas
            data = pytesseract.image_to_data(
                image,
                lang=lang_string,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Processar dados para extrair palavras com posições
            words_with_boxes = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Apenas palavras com confiança > 0
                    word_info = {
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': int(data['left'][i]),
                        'top': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i]),
                        'level': int(data['level'][i])
                    }
                    words_with_boxes.append(word_info)
            
            # Texto completo
            full_text = ' '.join([word['text'] for word in words_with_boxes if word['text'].strip()])
            
            return {
                'text': full_text,
                'words_with_boxes': words_with_boxes,
                'image_path': image_path,
                'total_words': len(words_with_boxes),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto com boxes de {image_path}: {e}")
            return {
                'text': '',
                'words_with_boxes': [],
                'image_path': image_path,
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def batch_extract(self, image_paths: List[str], 
                     output_dir: str = None,
                     save_individual: bool = True) -> Dict[str, Any]:
        """
        Extrai texto de múltiplas imagens em lote
        
        Args:
            image_paths: Lista de caminhos das imagens
            output_dir: Diretório para salvar resultados
            save_individual: Salvar resultado de cada imagem individualmente
            
        Returns:
            Dicionário com resultados consolidados
        """
        results = []
        total_text = ""
        total_chars = 0
        total_words = 0
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"Processando imagem {i}/{len(image_paths)}: {Path(image_path).name}")
            
            result = self.extract_text(image_path)
            results.append(result)
            
            if 'text' in result and result['text']:
                total_text += result['text'] + "\n\n"
                total_chars += result.get('char_count', 0)
                total_words += result.get('word_count', 0)
            
            # Salvar resultado individual se solicitado
            if save_individual and output_dir and 'text' in result:
                base_name = Path(image_path).stem
                text_file = os.path.join(output_dir, f"{base_name}_ocr.txt")
                json_file = os.path.join(output_dir, f"{base_name}_ocr.json")
                
                # Salvar texto
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                
                # Salvar metadados
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Resultado consolidado
        batch_result = {
            'total_images': len(image_paths),
            'successful_extractions': len([r for r in results if 'text' in r and r['text']]),
            'failed_extractions': len([r for r in results if 'error' in r]),
            'total_text': total_text.strip(),
            'total_characters': total_chars,
            'total_words': total_words,
            'individual_results': results,
            'batch_timestamp': datetime.now().isoformat(),
            'languages_used': self.languages
        }
        
        # Salvar resultado consolidado
        if output_dir:
            batch_file = os.path.join(output_dir, "batch_ocr_result.json")
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch_result, f, indent=2, ensure_ascii=False)
            
            # Salvar texto consolidado
            consolidated_text_file = os.path.join(output_dir, "consolidated_text.txt")
            with open(consolidated_text_file, 'w', encoding='utf-8') as f:
                f.write(total_text)
        
        logger.info(f"Lote processado: {batch_result['successful_extractions']}/{batch_result['total_images']} sucessos")
        return batch_result
    
    def _build_config(self, custom_config: str = None) -> str:
        """Constrói string de configuração do Tesseract"""
        if custom_config:
            return custom_config
            
        psm = self.PSM_MODES.get(self.psm_mode, 3)
        oem = self.OEM_MODES.get(self.oem_mode, 3)
        
        return f'--oem {oem} --psm {psm}'
    
    def _calculate_stats(self, data: Dict, confidence_threshold: float) -> Dict[str, float]:
        """Calcula estatísticas de confiança"""
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        
        if not confidences:
            return {
                'avg_confidence': 0.0,
                'min_confidence': 0.0,
                'max_confidence': 0.0,
                'words_above_threshold': 0,
                'total_words': 0
            }
        
        words_above_threshold = len([c for c in confidences if c >= confidence_threshold])
        
        return {
            'avg_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'words_above_threshold': words_above_threshold,
            'total_words': len(confidences)
        }
    
    def _detect_language(self, text: str) -> str:
        """Detecta idioma principal do texto (implementação simples)"""
        if not text.strip():
            return 'unknown'
        
        # Implementação simples baseada em palavras comuns
        portuguese_words = ['de', 'da', 'do', 'para', 'com', 'em', 'por', 'que', 'não', 'uma', 'um']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
        spanish_words = ['de', 'la', 'el', 'en', 'y', 'a', 'que', 'del', 'se', 'los', 'con']
        
        text_lower = text.lower()
        
        pt_count = sum(1 for word in portuguese_words if word in text_lower)
        en_count = sum(1 for word in english_words if word in text_lower)
        es_count = sum(1 for word in spanish_words if word in text_lower)
        
        if pt_count >= en_count and pt_count >= es_count:
            return 'por'
        elif en_count >= es_count:
            return 'eng'
        elif es_count > 0:
            return 'spa'
        else:
            return 'unknown'
    
    def get_available_languages(self) -> Dict[str, str]:
        """Retorna idiomas disponíveis no sistema"""
        try:
            available = pytesseract.get_languages(config='')
            return {lang: self.SUPPORTED_LANGUAGES.get(lang, lang) 
                   for lang in available if lang in self.SUPPORTED_LANGUAGES}
        except Exception as e:
            logger.error(f"Erro ao obter idiomas disponíveis: {e}")
            return {}

# Instância global do engine
tesseract_engine = TesseractEngine() 