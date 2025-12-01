"""
Aplicación web Flask para ScholarQA
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pathlib import Path
import logging
import sys

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from core.pdf_processor import PDFProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from core.llm_engine import LLMEngine
from utils.config import Config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Inicializar componentes (lazy loading)
pdf_processor = None
embedding_engine = None
vector_store = None
llm_engine = None


def initialize_components():
    """Inicializa los componentes de IA (lazy loading)"""
    global pdf_processor, embedding_engine, vector_store, llm_engine
    
    if pdf_processor is None:
        logger.info("Inicializando componentes...")
        pdf_processor = PDFProcessor()
        embedding_engine = EmbeddingEngine(Config.EMBEDDING_MODEL)
        vector_store = VectorStore(
            str(Config.get_vector_store_path()),
            Config.COLLECTION_NAME
        )
        
        # LLM es opcional
        try:
            llm_engine = LLMEngine(str(Config.get_llm_model_path()))
        except FileNotFoundError as e:
            logger.warning(f"Modelo LLM no disponible: {e}")
            llm_engine = None


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/status')
def status():
    """Estado del sistema"""
    initialize_components()
    
    return jsonify({
        'status': 'ok',
        'components': {
            'pdf_processor': pdf_processor is not None,
            'embedding_engine': embedding_engine is not None,
            'vector_store': vector_store is not None,
            'llm_engine': llm_engine is not None
        },
        'documents_count': vector_store.get_collection_count() if vector_store else 0
    })


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Sube y procesa un PDF"""
    try:
        initialize_components()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Solo se aceptan archivos PDF'}), 400
        
        # Guardar archivo
        upload_folder = Config.get_upload_folder()
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        filepath = upload_folder / file.filename
        file.save(filepath)
        
        logger.info(f"Procesando: {file.filename}")
        
        # Extraer texto
        text = pdf_processor.extract_text(filepath)
        metadata = pdf_processor.extract_metadata(filepath)
        
        # Crear chunks
        chunks = pdf_processor.chunk_text(
            text, 
            Config.CHUNK_SIZE, 
            Config.CHUNK_OVERLAP
        )
        
        # Añadir a vector store
        metadatas = [
            {
                'source': file.filename,
                'chunk_id': i,
                'title': metadata.get('title', file.filename)
            }
            for i in range(len(chunks))
        ]
        
        ids = [f"{file.filename}_chunk_{i}" for i in range(len(chunks))]
        
        vector_store.add_documents(chunks, metadatas, ids)
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'chunks': len(chunks),
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"Error en upload: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Responde una pregunta sobre los documentos"""
    try:
        initialize_components()
        
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Pregunta vacía'}), 400
        
        if not llm_engine:
            return jsonify({'error': 'Modelo LLM no disponible'}), 503
        
        logger.info(f"Pregunta: {question}")
        
        # Buscar contexto relevante
        results = vector_store.query(question, n_results=Config.MAX_CHUNKS_PER_QUERY)
        
        if not results['documents'][0]:
            return jsonify({
                'answer': 'No encontré documentos relevantes. Por favor, sube un PDF primero.',
                'sources': []
            })
        
        # Generar respuesta
        context_chunks = results['documents'][0]
        response = llm_engine.answer_question(
            question, 
            context_chunks,
            max_tokens=Config.MAX_TOKENS
        )
        
        # Preparar fuentes
        sources = []
        for i, metadata in enumerate(results['metadatas'][0]):
            sources.append({
                'source': metadata.get('source', 'Unknown'),
                'chunk_id': metadata.get('chunk_id', i)
            })
        
        return jsonify({
            'answer': response['answer'],
            'sources': sources,
            'context_used': response['context_used']
        })
        
    except Exception as e:
        logger.error(f"Error en ask: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents')
def list_documents():
    """Lista documentos cargados"""
    try:
        initialize_components()
        
        count = vector_store.get_collection_count()
        
        return jsonify({
            'total_chunks': count,
            'message': f'{count} chunks en la base de datos'
        })
        
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Iniciando ScholarQA...")
    logger.info(f"Servidor en http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
