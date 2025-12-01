"""
Utilidades para monitoreo de rendimiento
"""

import time
import functools
import logging
from typing import Callable, Any
import psutil
import os

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor de rendimiento del sistema"""
    
    @staticmethod
    def get_memory_usage() -> dict:
        """
        Obtiene uso de memoria actual
        
        Returns:
            Diccionario con información de memoria
        """
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        return {
            'rss_mb': mem_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': mem_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def get_cpu_usage() -> float:
        """
        Obtiene uso de CPU
        
        Returns:
            Porcentaje de uso de CPU
        """
        process = psutil.Process(os.getpid())
        return process.cpu_percent(interval=0.1)
    
    @staticmethod
    def get_system_info() -> dict:
        """
        Obtiene información del sistema
        
        Returns:
            Diccionario con información del sistema
        """
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'memory_available_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024,
            'memory_percent': psutil.virtual_memory().percent
        }


def timeit(func: Callable) -> Callable:
    """
    Decorador para medir tiempo de ejecución
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        logger.debug(f"{func.__name__} ejecutado en {elapsed:.3f}s")
        
        return result
    
    return wrapper


def log_performance(func: Callable) -> Callable:
    """
    Decorador para logging detallado de rendimiento
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Mediciones antes
        start_time = time.time()
        mem_before = PerformanceMonitor.get_memory_usage()
        
        # Ejecutar función
        result = func(*args, **kwargs)
        
        # Mediciones después
        elapsed = time.time() - start_time
        mem_after = PerformanceMonitor.get_memory_usage()
        mem_delta = mem_after['rss_mb'] - mem_before['rss_mb']
        
        logger.info(
            f"{func.__name__}: "
            f"tiempo={elapsed:.3f}s, "
            f"mem_delta={mem_delta:+.2f}MB, "
            f"mem_actual={mem_after['rss_mb']:.2f}MB"
        )
        
        return result
    
    return wrapper


class Timer:
    """Context manager para medir tiempo"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        logger.debug(f"{self.name}: {self.elapsed:.3f}s")
