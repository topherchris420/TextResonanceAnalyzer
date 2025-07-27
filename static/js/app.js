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
        // Text input with debouncing and typing indicator
        this.textInput.addEventListener('input', (e) => {
            this.updateCharCount();
            this.showTypingIndicator();
            this.debouncedAnalyze();
        });
        
        // Focus effects
        this.textInput.addEventListener('focus', () => {
            this.textInput.closest('.input-wrapper').classList.add('focused');
        });
        
        this.textInput.addEventListener('blur', () => {
            this.textInput.closest('.input-wrapper').classList.remove('focused');
            this.hideTypingIndicator();
        });
        
        // Sample button handlers
        document.querySelectorAll('.sample-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sampleType = e.target.dataset.sample || e.target.closest('.sample-btn').dataset.sample;
                this.loadSampleText(sampleType);
                this.animateButton(e.target.closest('.sample-btn'));
            });
        });
        
        // Tree control buttons with enhanced feedback
        document.getElementById('centerTree').addEventListener('click', (e) => {
            this.treeViz.centerTree();
            this.animateButton(e.target);
        });
        
        document.getElementById('expandAll').addEventListener('click', (e) => {
            this.treeViz.expandAll();
            this.animateButton(e.target);
        });
        
        document.getElementById('collapseAll').addEventListener('click', (e) => {
            this.treeViz.collapseAll();
            this.animateButton(e.target);
        });
        
        // Initialize particle background
        this.createParticleBackground();
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
        this.createSuccessParticles();
    }
    
    showTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.classList.remove('d-none');
        }
    }
    
    hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.classList.add('d-none');
        }
    }
    
    loadSampleText(type) {
        const samples = {
            positive: "I absolutely love this innovative approach to natural language processing! The way it visualizes symbolic resonance patterns is truly groundbreaking and inspiring. This technology will revolutionize how we understand human communication.",
            neutral: "The weather forecast indicates partly cloudy skies with temperatures ranging from 65 to 75 degrees Fahrenheit. Light winds from the northeast at 5-10 mph are expected throughout the day.",
            negative: "I'm extremely disappointed with the poor customer service experience. The staff was unhelpful, the process was frustrating, and the final result was completely unsatisfactory. This needs immediate improvement."
        };
        
        const sample = samples[type] || samples.positive;
        this.textInput.value = sample;
        this.updateCharCount();
        this.textInput.focus();
        
        // Add typing animation
        this.typeWriter(sample, 0);
        
        // Trigger analysis after typing animation
        setTimeout(() => {
            this.debouncedAnalyze();
        }, sample.length * 20 + 500);
    }
    
    typeWriter(text, index) {
        if (index < text.length) {
            this.textInput.value = text.substring(0, index + 1);
            this.updateCharCount();
            setTimeout(() => this.typeWriter(text, index + 1), 20);
        }
    }
    
    animateButton(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);
    }
    
    createParticleBackground() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'particle-bg';
        document.body.appendChild(particleContainer);
        
        // Create floating particles
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                this.createParticle(particleContainer);
            }, i * 400);
        }
        
        // Continuously create new particles
        setInterval(() => {
            this.createParticle(particleContainer);
        }, 2000);
    }
    
    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + 'vw';
        particle.style.animationDuration = (Math.random() * 3 + 5) + 's';
        particle.style.opacity = Math.random() * 0.3 + 0.1;
        
        container.appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 8000);
    }
    
    createSuccessParticles() {
        const colors = ['#0d6efd', '#198754', '#0dcaf0', '#ffc107'];
        const container = document.querySelector('.tree-container-enhanced') || document.body;
        
        for (let i = 0; i < 15; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                particle.style.position = 'absolute';
                particle.style.width = '4px';
                particle.style.height = '4px';
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];
                particle.style.borderRadius = '50%';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = '50%';
                particle.style.pointerEvents = 'none';
                particle.style.zIndex = '1000';
                
                const animation = particle.animate([
                    { transform: 'translateY(0) scale(1)', opacity: 1 },
                    { transform: 'translateY(-100px) scale(0)', opacity: 0 }
                ], {
                    duration: 1000,
                    easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
                });
                
                container.appendChild(particle);
                
                animation.onfinish = () => {
                    if (particle.parentNode) {
                        particle.parentNode.removeChild(particle);
                    }
                };
            }, i * 50);
        }
    }
    
    displaySentiment(sentiment) {
        const polarity = sentiment.polarity;
        const subjectivity = sentiment.subjectivity;
        const confidence = sentiment.confidence;
        
        // Determine sentiment label and color
        let sentimentLabel, sentimentClass, sentimentIcon;
        if (polarity > 0.1) {
            sentimentLabel = 'Positive';
            sentimentClass = 'sentiment-positive';
            sentimentIcon = 'smile';
        } else if (polarity < -0.1) {
            sentimentLabel = 'Negative';
            sentimentClass = 'sentiment-negative';
            sentimentIcon = 'frown';
        } else {
            sentimentLabel = 'Neutral';
            sentimentClass = 'sentiment-neutral';
            sentimentIcon = 'meh';
        }
        
        // Determine subjectivity label
        const subjectivityLabel = subjectivity > 0.5 ? 'Subjective' : 'Objective';
        
        // Create progress bars for visual representation
        const polarityPercent = Math.abs(polarity * 100);
        const subjectivityPercent = subjectivity * 100;
        const confidencePercent = confidence * 100;
        
        this.sentimentResults.innerHTML = `
            <div class="sentiment-overview mb-4">
                <div class="text-center">
                    <div class="sentiment-icon-large mb-2">
                        <i class="fas fa-${sentimentIcon} fa-3x ${sentimentClass}"></i>
                    </div>
                    <h4 class="sentiment-label ${sentimentClass}">${sentimentLabel} Sentiment</h4>
                    <p class="text-muted">Overall emotional tone of the text</p>
                </div>
            </div>
            
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="sentiment-metric-enhanced">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-semibold">Polarity Score</span>
                            <span class="sentiment-value ${sentimentClass}">${polarity.toFixed(3)}</span>
                        </div>
                        <div class="progress progress-glow mb-2" style="height: 8px;">
                            <div class="progress-bar ${sentimentClass === 'sentiment-positive' ? 'bg-success' : sentimentClass === 'sentiment-negative' ? 'bg-danger' : 'bg-secondary'}" 
                                 style="width: ${polarityPercent}%; transition: width 1s ease-in-out;"></div>
                        </div>
                        <small class="text-muted">Range: -1 (very negative) to +1 (very positive)</small>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="sentiment-metric-enhanced">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-semibold">Confidence Level</span>
                            <span class="sentiment-value">${confidencePercent.toFixed(1)}%</span>
                        </div>
                        <div class="progress progress-glow mb-2" style="height: 8px;">
                            <div class="progress-bar bg-info" style="width: ${confidencePercent}%; transition: width 1s ease-in-out;"></div>
                        </div>
                        <small class="text-muted">How certain the analysis is</small>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="sentiment-metric-enhanced">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-semibold">Tone Type</span>
                            <span class="sentiment-value">${subjectivityLabel}</span>
                        </div>
                        <div class="progress progress-glow mb-2" style="height: 8px;">
                            <div class="progress-bar bg-warning" style="width: ${subjectivityPercent}%; transition: width 1s ease-in-out;"></div>
                        </div>
                        <small class="text-muted">Objective (factual) vs Subjective (opinion-based)</small>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="sentiment-metric-enhanced">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-semibold">Subjectivity Score</span>
                            <span class="sentiment-value">${subjectivity.toFixed(3)}</span>
                        </div>
                        <div class="progress progress-glow mb-2" style="height: 8px;">
                            <div class="progress-bar bg-primary" style="width: ${subjectivityPercent}%; transition: width 1s ease-in-out;"></div>
                        </div>
                        <small class="text-muted">0 (objective) to 1 (subjective)</small>
                    </div>
                </div>
            </div>
        `;
        
        this.sentimentResults.classList.remove('empty-state');
        this.sentimentResults.classList.add('fade-in');
    }
    
    displayTextStats(data) {
        const entityCount = data.entities ? data.entities.length : 0;
        const relationshipCount = data.relationships ? data.relationships.length : 0;
        
        // Calculate reading metrics
        const wordsPerMinute = 200; // Average reading speed
        const readingTime = Math.ceil((data.word_count || 0) / wordsPerMinute);
        
        this.textStats.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-font text-primary"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-number text-primary" data-target="${data.word_count || 0}">0</div>
                        <div class="stat-label">Words</div>
                        <div class="stat-progress">
                            <div class="progress" style="height: 3px;">
                                <div class="progress-bar bg-primary" style="width: 0%" data-width="100%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-paragraph text-info"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-number text-info" data-target="${data.sentence_count || 0}">0</div>
                        <div class="stat-label">Sentences</div>
                        <div class="stat-progress">
                            <div class="progress" style="height: 3px;">
                                <div class="progress-bar bg-info" style="width: 0%" data-width="100%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-tags text-success"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-number text-success" data-target="${entityCount}">0</div>
                        <div class="stat-label">Entities</div>
                        <div class="stat-progress">
                            <div class="progress" style="height: 3px;">
                                <div class="progress-bar bg-success" style="width: 0%" data-width="100%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-project-diagram text-warning"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-number text-warning" data-target="${relationshipCount}">0</div>
                        <div class="stat-label">Relations</div>
                        <div class="stat-progress">
                            <div class="progress" style="height: 3px;">
                                <div class="progress-bar bg-warning" style="width: 0%" data-width="100%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="stat-card reading-time">
                    <div class="stat-icon">
                        <i class="fas fa-clock text-secondary"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-number text-secondary">${readingTime}</div>
                        <div class="stat-label">Min. Read</div>
                        <small class="text-muted">Estimated reading time</small>
                    </div>
                </div>
            </div>
        `;
        
        this.textStats.classList.remove('empty-state');
        this.textStats.classList.add('fade-in');
        
        // Animate numbers counting up
        this.animateStatNumbers();
    }
    
    animateStatNumbers() {
        const statNumbers = document.querySelectorAll('.stat-number[data-target]');
        const progressBars = document.querySelectorAll('.stat-progress .progress-bar[data-width]');
        
        statNumbers.forEach((stat, index) => {
            const target = parseInt(stat.dataset.target);
            const duration = 1500;
            const increment = target / (duration / 16);
            let current = 0;
            
            const counter = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(counter);
                }
                stat.textContent = Math.floor(current);
            }, 16);
            
            // Animate progress bars
            if (progressBars[index]) {
                setTimeout(() => {
                    progressBars[index].style.width = progressBars[index].dataset.width;
                }, index * 200);
            }
        });
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
