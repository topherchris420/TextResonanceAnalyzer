import os
import logging
import time
from functools import wraps
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from nlp_processor import NLPProcessor
from textblob import TextBlob

# Configure enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
CORS(app)

# Initialize enhanced NLP processor
nlp_processor = NLPProcessor()

# Performance monitoring decorator
def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{f.__name__} completed in {end_time - start_time:.3f}s")
        return result
    return decorated_function

@app.route('/')
def index():
    """Main page with the text analysis interface."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
@monitor_performance
def analyze_text():
    """Enhanced API endpoint for comprehensive text analysis."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Log request for monitoring
        logging.info(f"Analyzing text: {len(text)} characters")
        
        # Perform enhanced NLP analysis
        analysis_result = nlp_processor.analyze(text)
        
        # Add metadata for frontend
        analysis_result['metadata'] = {
            'text_length': len(text),
            'analysis_timestamp': time.time(),
            'version': '2.0-enhanced'
        }
        
        logging.info(f"Analysis completed: {analysis_result.get('processing_time', 0)}s")
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logging.error(f"Error analyzing text: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/quick-analyze', methods=['POST'])
@monitor_performance
def quick_analyze():
    """Lightweight analysis endpoint for real-time typing feedback."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'word_count': 0,
                'sentence_count': 0,
                'sentiment': {'polarity': 0.0, 'subjectivity': 0.0, 'confidence': 0.0}
            })
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                'word_count': 0,
                'sentence_count': 0,
                'sentiment': {'polarity': 0.0, 'subjectivity': 0.0, 'confidence': 0.0}
            })
        
        # Quick analysis for short texts (optimize for speed)
        if len(text) < 50:
            # Fast path for short texts
            words = len(text.split())
            sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
            
            # Basic sentiment for very short texts
            blob = TextBlob(text)
            sentiment_obj = blob.sentiment
            sentiment = {
                'polarity': round(sentiment_obj.polarity, 3),
                'subjectivity': round(sentiment_obj.subjectivity, 3),
                'confidence': round(abs(sentiment_obj.polarity), 3)
            }
            
            return jsonify({
                'word_count': words,
                'sentence_count': sentences,
                'sentiment': sentiment,
                'quick_mode': True
            })
        
        # Full analysis for longer texts (use cache)
        results = nlp_processor.analyze(text)
        
        return jsonify({
            'word_count': results.get('word_count', 0),
            'sentence_count': results.get('sentence_count', 0),
            'sentiment': results.get('sentiment', {}),
            'complexity_score': results.get('complexity_score', 0),
            'readability_score': results.get('readability_score', 0),
            'symbolic_resonance': results.get('symbolic_resonance', 0),
            'quick_mode': False
        })
        
    except Exception as e:
        logging.error(f"Quick analysis error: {str(e)}")
        return jsonify({
            'error': str(e),
            'word_count': 0,
            'sentence_count': 0,
            'sentiment': {'polarity': 0.0, 'subjectivity': 0.0, 'confidence': 0.0}
        }), 200  # Return 200 to not break UI

@app.route('/api/cache-stats', methods=['GET'])
def get_cache_stats():
    """Get NLP processor cache statistics."""
    try:
        stats = nlp_processor.get_cache_stats()
        return jsonify({
            'success': True,
            'cache_stats': stats
        })
    except Exception as e:
        logging.error(f"Cache stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the NLP processor cache."""
    try:
        nlp_processor.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        logging.error(f"Clear cache error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
