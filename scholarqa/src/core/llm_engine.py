"""
Motor LLM local optimizado usando llama.cpp
"""

from llama_cpp import Llama
from typing import Optional, List, Dict, Generator
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class LLMEngine:
    """Motor de inferencia LLM local con optimizaciones"""
    
    def __init__(self, model_path: str, n_ctx: int = 2048, 
                 n_threads: Optional[int] = None,
                 n_gpu_layers: int = 0):
        """
        Inicializa el motor LLM
        
        Args:
            model_path: Ruta al modelo .gguf
            n_ctx: Tamaño del contexto
            n_threads: Número de threads (None = auto)
            n_gpu_layers: Capas a cargar en GPU (0 = solo CPU)
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo LLM no encontrado: {model_path}\n"
                "Descarga un modelo .gguf y colócalo en models/downloaded/"
            )
        
        logger.info(f"Cargando modelo LLM: {model_path.name}")
        
        self.model_path = model_path
        self.n_ctx = n_ctx
        
        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )
        
        self._total_tokens = 0
        self._total_requests = 0
        
        logger.info("Modelo LLM cargado exitosamente")
    
    def generate(self, prompt: str, max_tokens: int = 512, 
                temperature: float = 0.7, top_p: float = 0.95,
                stop: Optional[List[str]] = None,
                repeat_penalty: float = 1.1) -> str:
        """
        Genera texto usando el modelo
        
        Args:
            prompt: Prompt de entrada
            max_tokens: Máximo de tokens a generar
            temperature: Temperature para sampling
            top_p: Top-p para sampling
            stop: Secuencias de parada
            repeat_penalty: Penalización por repetición
            
        Returns:
            Texto generado
        """
        start_time = time.time()
        logger.debug(f"Generando respuesta (max_tokens={max_tokens})")
        
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
                repeat_penalty=repeat_penalty,
                echo=False
            )
            
            text = response['choices'][0]['text'].strip()
            
            self._total_tokens += response['usage']['completion_tokens']
            self._total_requests += 1
            
            elapsed = time.time() - start_time
            logger.debug(f"Respuesta generada en {elapsed:.2f}s")
            
            return text
            
        except Exception as e:
            logger.error(f"Error generando texto: {e}", exc_info=True)
            raise
    
    def create_qa_prompt(self, question: str, context: str) -> str:
        """
        Crea un prompt para Q&A con contexto
        
        Args:
            question: Pregunta del usuario
            context: Contexto relevante
            
        Returns:
            Prompt formateado
        """
        prompt = f"""<s>[INST] Eres un asistente académico especializado. Responde la pregunta basándote ÚNICAMENTE en el contexto proporcionado. Si no puedes responder con la información dada, di "No tengo suficiente información en el contexto para responder esa pregunta."

Contexto:
{context}

Pregunta: {question}

Respuesta: [/INST]"""
        
        return prompt
    
    def answer_question(self, question: str, context_chunks: List[str],
                       max_tokens: int = 512, temperature: float = 0.7) -> Dict:
        """
        Responde una pregunta usando chunks de contexto
        
        Args:
            question: Pregunta del usuario
            context_chunks: Lista de chunks relevantes
            max_tokens: Máximo de tokens
            temperature: Temperature
            
        Returns:
            Diccionario con respuesta y metadatos
        """
        # Combinar chunks en contexto
        context = "\n\n".join(context_chunks)
        
        # Truncar contexto si es muy largo
        max_context_length = self.n_ctx - max_tokens - 200
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
            logger.warning(f"Contexto truncado a {max_context_length} caracteres")
        
        # Crear prompt
        prompt = self.create_qa_prompt(question, context)
        
        # Generar respuesta
        start_time = time.time()
        answer = self.generate(prompt, max_tokens=max_tokens, temperature=temperature)
        generation_time = time.time() - start_time
        
        return {
            'answer': answer,
            'context_used': len(context_chunks),
            'prompt_length': len(prompt),
            'generation_time': generation_time
        }
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del motor LLM"""
        return {
            'model_path': str(self.model_path),
            'context_size': self.n_ctx,
            'total_tokens_generated': self._total_tokens,
            'total_requests': self._total_requests
        }
