import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from nlp_processor import NLPProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
CORS(app)

# Initialize NLP processor
nlp_processor = NLPProcessor()

@app.route('/')
def index():
    """Main page with the text analysis interface."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """API endpoint for real-time text analysis."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Perform NLP analysis
        analysis_result = nlp_processor.analyze(text)
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logging.error(f"Error analyzing text: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
