"""
Procesador de PDFs académicos optimizado
"""

import pypdf
from pathlib import Path
from typing import List, Dict, Optional
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Procesa archivos PDF y extrae texto de manera optimizada"""
    
    def __init__(self, max_workers: int = 4):
        """
        Inicializa el procesador de PDFs
        
        Args:
            max_workers: Número máximo de workers para procesamiento paralelo
        """
        self.supported_extensions = ['.pdf']
        self.max_workers = max_workers
        self._page_cache = {}
    
    def extract_text(self, pdf_path: str, use_cache: bool = True) -> str:
        """
        Extrae todo el texto de un PDF con optimizaciones
        
        Args:
            pdf_path: Ruta al archivo PDF
            use_cache: Usar caché de páginas
            
        Returns:
            Texto extraído del PDF
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
            
            # Verificar caché
            cache_key = self._get_file_hash(pdf_path) if use_cache else None
            if cache_key and cache_key in self._page_cache:
                logger.debug(f"Usando texto cacheado para {pdf_path.name}")
                return self._page_cache[cache_key]
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Procesando {num_pages} páginas de {pdf_path.name}")
                
                # Extracción paralela de páginas
                if num_pages > 10 and self.max_workers > 1:
                    text = self._extract_pages_parallel(pdf_reader)
                else:
                    text = self._extract_pages_sequential(pdf_reader)
            
            # Limpiar texto
            text = self._clean_text(text)
            
            # Guardar en caché
            if cache_key:
                self._page_cache[cache_key] = text
            
            logger.info(f"Texto extraído: {len(text)} caracteres, {text.count(' ')} palabras aprox.")
            return text
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {e}", exc_info=True)
            raise
    
    def _extract_pages_sequential(self, pdf_reader: pypdf.PdfReader) -> str:
        """
        Extrae páginas secuencialmente
        
        Args:
            pdf_reader: Lector de PDF
            
        Returns:
            Texto completo
        """
        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"\n--- Página {page_num + 1} ---\n{page_text}")
        
        return "".join(text_parts)
    
    def _extract_pages_parallel(self, pdf_reader: pypdf.PdfReader) -> str:
        """
        Extrae páginas en paralelo para PDFs grandes
        
        Args:
            pdf_reader: Lector de PDF
            
        Returns:
            Texto completo
        """
        pages = list(pdf_reader.pages)
        text_parts = [None] * len(pages)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_page = {
                executor.submit(self._extract_page, page, idx): idx 
                for idx, page in enumerate(pages)
            }
            
            for future in as_completed(future_to_page):
                idx = future_to_page[future]
                try:
                    text_parts[idx] = future.result()
                except Exception as e:
                    logger.warning(f"Error extrayendo página {idx + 1}: {e}")
                    text_parts[idx] = ""
        
        return "".join(filter(None, text_parts))
    
    def _extract_page(self, page: pypdf.PageObject, page_num: int) -> str:
        """
        Extrae texto de una página
        
        Args:
            page: Objeto de página
            page_num: Número de página
            
        Returns:
            Texto de la página
        """
        try:
            page_text = page.extract_text()
            if page_text:
                return f"\n--- Página {page_num + 1} ---\n{page_text}"
        except Exception as e:
            logger.warning(f"Error en página {page_num + 1}: {e}")
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto extraído
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        # Eliminar múltiples espacios
        text = re.sub(r' +', ' ', text)
        
        # Eliminar múltiples saltos de línea
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Eliminar caracteres de control excepto saltos de línea y tabs
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        Genera hash único del archivo para caché
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Hash MD5 del archivo
        """
        hasher = hashlib.md5()
        hasher.update(str(file_path).encode())
        hasher.update(str(file_path.stat().st_mtime).encode())
        return hasher.hexdigest()
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """
        Extrae metadatos del PDF de manera robusta
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con metadatos
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                metadata = pdf_reader.metadata or {}
                
                # Extraer y limpiar metadatos
                def clean_metadata(value):
                    if value is None:
                        return ''
                    return str(value).strip()
                
                return {
                    'title': clean_metadata(metadata.get('/Title', Path(pdf_path).stem)),
                    'author': clean_metadata(metadata.get('/Author', 'Desconocido')),
                    'subject': clean_metadata(metadata.get('/Subject', '')),
                    'creator': clean_metadata(metadata.get('/Creator', '')),
                    'producer': clean_metadata(metadata.get('/Producer', '')),
                    'num_pages': len(pdf_reader.pages),
                    'file_size': Path(pdf_path).stat().st_size,
                    'created': metadata.get('/CreationDate', ''),
                    'modified': metadata.get('/ModDate', '')
                }
        except Exception as e:
            logger.warning(f"No se pudieron extraer metadatos: {e}")
            return {
                'title': Path(pdf_path).stem,
                'author': 'Desconocido',
                'subject': '',
                'creator': '',
                'producer': '',
                'num_pages': 0,
                'file_size': 0,
                'created': '',
                'modified': ''
            }
    
    def chunk_text(self, text: str, chunk_size: int = 1000, 
                   chunk_overlap: int = 200) -> List[str]:
        """
        Divide el texto en chunks con overlap (método básico, usa text_splitter para chunking avanzado)
        
        Args:
            text: Texto a dividir
            chunk_size: Tamaño de cada chunk
            chunk_overlap: Overlap entre chunks
            
        Returns:
            Lista de chunks de texto
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start += chunk_size - chunk_overlap
        
        logger.info(f"Texto dividido en {len(chunks)} chunks")
        return chunks
    
    def extract_text_with_layout(self, pdf_path: str) -> List[Dict]:
        """
        Extrae texto preservando información de layout (experimental)
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con texto y metadatos de página
        """
        try:
            pdf_path = Path(pdf_path)
            pages_data = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    
                    if page_text:
                        pages_data.append({
                            'page_number': page_num + 1,
                            'text': page_text,
                            'char_count': len(page_text),
                            'word_count': len(page_text.split())
                        })
            
            return pages_data
            
        except Exception as e:
            logger.error(f"Error extrayendo con layout: {e}")
            return []
    
    def clear_cache(self):
        """Limpia la caché de páginas"""
        self._page_cache.clear()
        logger.info("Caché de páginas limpiada")
    
    def validate_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Valida si un PDF es procesable
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con resultado de validación
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            pdf_path = Path(pdf_path)
            
            # Verificar existencia
            if not pdf_path.exists():
                result['errors'].append('Archivo no existe')
                return result
            
            # Verificar extensión
            if pdf_path.suffix.lower() != '.pdf':
                result['errors'].append('No es un archivo PDF')
                return result
            
            # Verificar tamaño
            file_size = pdf_path.stat().st_size
            if file_size == 0:
                result['errors'].append('Archivo vacío')
                return result
            
            if file_size > 100 * 1024 * 1024:  # 100 MB
                result['warnings'].append('Archivo muy grande (>100MB)')
            
            # Intentar abrir y leer
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                if len(pdf_reader.pages) == 0:
                    result['errors'].append('PDF sin páginas')
                    return result
                
                # Intentar extraer texto de primera página
                first_page_text = pdf_reader.pages[0].extract_text()
                if not first_page_text or len(first_page_text.strip()) == 0:
                    result['warnings'].append('Primera página sin texto extraíble')
            
            result['valid'] = True
            
        except Exception as e:
            result['errors'].append(f'Error al validar: {str(e)}')
        
        return result
