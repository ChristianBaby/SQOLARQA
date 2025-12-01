"""
Validadores de entrada y datos
"""

from pathlib import Path
from typing import Optional, List
import re


class ValidationError(Exception):
    """Error de validación"""
    pass


class FileValidator:
    """Validador de archivos"""
    
    @staticmethod
    def validate_pdf(file_path: Path, max_size_mb: int = 100) -> dict:
        """
        Valida un archivo PDF
        
        Args:
            file_path: Ruta al archivo
            max_size_mb: Tamaño máximo en MB
            
        Returns:
            Diccionario con resultado de validación
            
        Raises:
            ValidationError: Si el archivo no es válido
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar existencia
        if not file_path.exists():
            result['valid'] = False
            result['errors'].append('El archivo no existe')
            return result
        
        # Verificar extensión
        if file_path.suffix.lower() != '.pdf':
            result['valid'] = False
            result['errors'].append('El archivo debe ser PDF')
            return result
        
        # Verificar tamaño
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        if file_size_mb > max_size_mb:
            result['valid'] = False
            result['errors'].append(f'El archivo excede {max_size_mb}MB')
            return result
        
        if file_size_mb == 0:
            result['valid'] = False
            result['errors'].append('El archivo está vacío')
            return result
        
        # Advertencias
        if file_size_mb > max_size_mb * 0.8:
            result['warnings'].append(f'El archivo es grande ({file_size_mb:.1f}MB)')
        
        return result


class TextValidator:
    """Validador de texto"""
    
    @staticmethod
    def validate_question(question: str, 
                         min_length: int = 3, 
                         max_length: int = 500) -> dict:
        """
        Valida una pregunta
        
        Args:
            question: Texto de la pregunta
            min_length: Longitud mínima
            max_length: Longitud máxima
            
        Returns:
            Diccionario con resultado de validación
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not question or not question.strip():
            result['valid'] = False
            result['errors'].append('La pregunta no puede estar vacía')
            return result
        
        question = question.strip()
        
        if len(question) < min_length:
            result['valid'] = False
            result['errors'].append(f'La pregunta debe tener al menos {min_length} caracteres')
        
        if len(question) > max_length:
            result['valid'] = False
            result['errors'].append(f'La pregunta no puede exceder {max_length} caracteres')
        
        return result
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitiza texto de entrada
        
        Args:
            text: Texto a sanitizar
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


class ConfigValidator:
    """Validador de configuración"""
    
    @staticmethod
    def validate_config(config: dict) -> dict:
        """
        Valida configuración de la aplicación
        
        Args:
            config: Diccionario de configuración
            
        Returns:
            Diccionario con resultado de validación
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validar chunk_size
        if 'chunk_size' in config:
            if not isinstance(config['chunk_size'], int):
                result['errors'].append('chunk_size debe ser entero')
                result['valid'] = False
            elif config['chunk_size'] < 100 or config['chunk_size'] > 10000:
                result['warnings'].append('chunk_size fuera de rango recomendado (100-10000)')
        
        # Validar chunk_overlap
        if 'chunk_overlap' in config:
            if not isinstance(config['chunk_overlap'], int):
                result['errors'].append('chunk_overlap debe ser entero')
                result['valid'] = False
            elif config.get('chunk_size') and config['chunk_overlap'] >= config['chunk_size']:
                result['errors'].append('chunk_overlap debe ser menor que chunk_size')
                result['valid'] = False
        
        return result
