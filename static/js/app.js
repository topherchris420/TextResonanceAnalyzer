/**
 * Main application logic for NLP Symbolic Resonance Analyzer
 */

class NLPAnalyzer {
    constructor() {
        this.textInput = document.getElementById('textInput');
        this.charCount = document.getElementById('charCount');
        this.analysisStatus = document.getElementById('analysisStatus');
        this.errorDisplay = document.getElementById('errorDisplay');
        this.errorMessage = document.getElementById('errorMessage');
        this.sentimentResults = document.getElementById('sentimentResults');
        this.textStats = document.getElementById('textStats');
        
        this.debounceTimer = null;
        this.debounceDelay = 1000; // 1 second delay
        this.currentRequest = null;
        
        this.treeViz = new TreeVisualization('treeVisualization');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Text input with debouncing
        this.textInput.addEventListener('input', (e) => {
            this.updateCharCount();
            this.debouncedAnalyze();
        });
        
        // Tree control buttons
        document.getElementById('centerTree').addEventListener('click', () => {
            this.treeViz.centerTree();
        });
        
        document.getElementById('expandAll').addEventListener('click', () => {
            this.treeViz.expandAll();
        });
        
        document.getElementById('collapseAll').addEventListener('click', () => {
            this.treeViz.collapseAll();
        });
    }
    
    updateCharCount() {
        const count = this.textInput.value.length;
        this.charCount.textContent = count;
        
        // Color coding for character count
        if (count > 4500) {
            this.charCount.className = 'text-danger';
        } else if (count > 3500) {
            this.charCount.className = 'text-warning';
        } else {
            this.charCount.className = 'text-muted';
        }
    }
    
    debouncedAnalyze() {
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Cancel any ongoing request
        if (this.currentRequest) {
            this.currentRequest.abort();
            this.currentRequest = null;
        }
        
        const text = this.textInput.value.trim();
        
        if (!text) {
            this.clearResults();
            return;
        }
        
        // Set new timer
        this.debounceTimer = setTimeout(() => {
            this.analyzeText(text);
        }, this.debounceDelay);
    }
    
    async analyzeText(text) {
        this.showLoading();
        this.hideError();
        
        try {
            // Create AbortController for request cancellation
            const controller = new AbortController();
            this.currentRequest = controller;
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
                signal: controller.signal
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.displayResults(data);
            
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Request was cancelled');
                return;
            }
            
            console.error('Analysis error:', error);
            this.showError(error.message || 'An error occurred during analysis');
        } finally {
            this.hideLoading();
            this.currentRequest = null;
        }
    }
    
    displayResults(data) {
        this.displaySentiment(data.sentiment);
        this.displayTextStats(data);
        this.treeViz.updateTree(data.tree_data);
    }
    
    displaySentiment(sentiment) {
        const polarity = sentiment.polarity;
        const subjectivity = sentiment.subjectivity;
        const confidence = sentiment.confidence;
        
        // Determine sentiment label and color
        let sentimentLabel, sentimentClass;
        if (polarity > 0.1) {
            sentimentLabel = 'Positive';
            sentimentClass = 'sentiment-positive';
        } else if (polarity < -0.1) {
            sentimentLabel = 'Negative';
            sentimentClass = 'sentiment-negative';
        } else {
            sentimentLabel = 'Neutral';
            sentimentClass = 'sentiment-neutral';
        }
        
        // Determine subjectivity label
        const subjectivityLabel = subjectivity > 0.5 ? 'Subjective' : 'Objective';
        
        this.sentimentResults.innerHTML = `
            <div class="row g-3">
                <div class="col-md-4">
                    <div class="sentiment-metric">
                        <span>Overall Sentiment:</span>
                        <span class="sentiment-value ${sentimentClass}">
                            <i class="fas fa-${polarity > 0.1 ? 'smile' : polarity < -0.1 ? 'frown' : 'meh'} me-1"></i>
                            ${sentimentLabel}
                        </span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="sentiment-metric">
                        <span>Polarity Score:</span>
                        <span class="sentiment-value ${sentimentClass}">
                            ${polarity.toFixed(3)}
                        </span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="sentiment-metric">
                        <span>Confidence:</span>
                        <span class="sentiment-value">
                            ${(confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="sentiment-metric">
                        <span>Tone:</span>
                        <span class="sentiment-value">
                            ${subjectivityLabel}
                        </span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="sentiment-metric">
                        <span>Subjectivity:</span>
                        <span class="sentiment-value">
                            ${subjectivity.toFixed(3)}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        this.sentimentResults.classList.add('fade-in');
    }
    
    displayTextStats(data) {
        const entityCount = data.entities ? data.entities.length : 0;
        const relationshipCount = data.relationships ? data.relationships.length : 0;
        
        this.textStats.innerHTML = `
            <div class="row g-3">
                <div class="col-6 col-md-3">
                    <div class="text-center">
                        <div class="h4 mb-0 text-primary">${data.word_count || 0}</div>
                        <small class="text-muted">Words</small>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="text-center">
                        <div class="h4 mb-0 text-info">${data.sentence_count || 0}</div>
                        <small class="text-muted">Sentences</small>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="text-center">
                        <div class="h4 mb-0 text-success">${entityCount}</div>
                        <small class="text-muted">Entities</small>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="text-center">
                        <div class="h4 mb-0 text-warning">${relationshipCount}</div>
                        <small class="text-muted">Relations</small>
                    </div>
                </div>
            </div>
        `;
        
        this.textStats.classList.add('fade-in');
    }
    
    clearResults() {
        this.sentimentResults.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            Start typing to see sentiment analysis results...
        `;
        this.sentimentResults.className = 'text-muted';
        
        this.textStats.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            Text statistics will appear here...
        `;
        this.textStats.className = 'text-muted';
        
        this.treeViz.clearTree();
    }
    
    showLoading() {
        this.analysisStatus.classList.remove('d-none');
    }
    
    hideLoading() {
        this.analysisStatus.classList.add('d-none');
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorDisplay.classList.remove('d-none');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }
    
    hideError() {
        this.errorDisplay.classList.add('d-none');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const analyzer = new NLPAnalyzer();
    
    // Add some sample text to help users get started
    const sampleTexts = [
        "I absolutely love this new approach to data visualization. It's incredibly intuitive and powerful!",
        "The weather today is quite unpredictable. It started sunny but now it's raining heavily.",
        "Artificial intelligence is revolutionizing how we understand and process human language patterns."
    ];
    
    // Add a button to load sample text for testing
    const textInput = document.getElementById('textInput');
    textInput.placeholder = `Type or paste your text here to analyze its symbolic resonance patterns...\n\nTry this sample: "${sampleTexts[0]}"`;
});
