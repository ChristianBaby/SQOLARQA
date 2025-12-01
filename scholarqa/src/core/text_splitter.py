"""
Divisor de texto optimizado con chunking semántico
"""

from typing import List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class SemanticTextSplitter:
    """
    Divisor de texto inteligente que respeta límites semánticos
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa el divisor de texto
        
        Args:
            chunk_size: Tamaño objetivo de cada chunk
            chunk_overlap: Overlap entre chunks consecutivos
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Patrones para detectar límites semánticos
        self.sentence_endings = re.compile(r'[.!?]\s+')
        self.paragraph_endings = re.compile(r'\n\n+')
    
    def split_text(self, text: str) -> List[str]:
        """
        Divide el texto en chunks respetando límites semánticos
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks de texto
        """
        if not text or not text.strip():
            return []
        
        # Primero intentar dividir por párrafos
        paragraphs = self.paragraph_endings.split(text)
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Si el párrafo cabe en el chunk actual
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Guardar chunk actual si existe
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Si el párrafo es muy largo, dividirlo por oraciones
                if len(paragraph) > self.chunk_size:
                    para_chunks = self._split_long_paragraph(paragraph)
                    chunks.extend(para_chunks[:-1])
                    current_chunk = para_chunks[-1] if para_chunks else ""
                else:
                    current_chunk = paragraph
        
        # Añadir el último chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # Añadir overlap
        chunks = self._add_overlap(chunks)
        
        logger.info(f"Texto dividido en {len(chunks)} chunks semánticos")
        return chunks
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """
        Divide un párrafo largo en chunks por oraciones
        
        Args:
            paragraph: Párrafo a dividir
            
        Returns:
            Lista de chunks
        """
        sentences = self.sentence_endings.split(paragraph)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Si una sola oración es muy larga, dividirla por caracteres
                if len(sentence) > self.chunk_size:
                    chunks.extend(self._split_by_chars(sentence))
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_by_chars(self, text: str) -> List[str]:
        """
        Divide texto por caracteres (último recurso)
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks
        """
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """
        Añade overlap entre chunks para mantener contexto
        
        Args:
            chunks: Lista de chunks sin overlap
            
        Returns:
            Lista de chunks con overlap
        """
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks
        
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]
            
            # Tomar las últimas palabras del chunk anterior
            overlap_text = prev_chunk[-self.chunk_overlap:]
            
            # Buscar un límite de palabra limpio
            space_idx = overlap_text.find(' ')
            if space_idx > 0:
                overlap_text = overlap_text[space_idx + 1:]
            
            # Combinar overlap con chunk actual
            overlapped_chunk = overlap_text + " " + current_chunk
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks


class RecursiveTextSplitter:
    """
    Divisor recursivo que prueba múltiples separadores
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Separadores en orden de preferencia
        self.separators = ["\n\n", "\n", ". ", ", ", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """
        Divide texto recursivamente usando múltiples separadores
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks
        """
        return self._split_text_recursive(text, self.separators)
    
    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """
        División recursiva del texto
        
        Args:
            text: Texto a dividir
            separators: Lista de separadores a probar
            
        Returns:
            Lista de chunks
        """
        if not text or not text.strip():
            return []
        
        # Si el texto cabe en un chunk, retornarlo
        if len(text) <= self.chunk_size:
            return [text]
        
        # Probar con el primer separador
        if not separators:
            # No hay más separadores, dividir por caracteres
            return self._split_by_length(text)
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Dividir por el separador actual
        splits = text.split(separator) if separator else list(text)
        
        # Recombinar splits en chunks
        chunks = []
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_len = len(split)
            
            if current_length + split_len + len(separator) <= self.chunk_size:
                current_chunk.append(split)
                current_length += split_len + len(separator)
            else:
                # Guardar chunk actual
                if current_chunk:
                    chunk_text = separator.join(current_chunk)
                    chunks.append(chunk_text)
                
                # Si el split actual es muy grande, dividirlo recursivamente
                if split_len > self.chunk_size:
                    sub_chunks = self._split_text_recursive(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = []
                    current_length = 0
                else:
                    current_chunk = [split]
                    current_length = split_len
        
        # Añadir último chunk
        if current_chunk:
            chunk_text = separator.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks
    
    def _split_by_length(self, text: str) -> List[str]:
        """
        Divide texto por longitud fija con overlap
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
