import spacy
import logging
from collections import defaultdict, Counter
from textblob import TextBlob
import re
import hashlib
from functools import lru_cache
import threading
import time
from typing import Dict, List, Tuple, Any

class NLPProcessor:
    def __init__(self):
        """Initialize the NLP processor with spaCy model and caching."""
        try:
            # Try to load the English model with optimized pipeline
            self.nlp = spacy.load("en_core_web_sm")
            # Add sentencizer for sentence boundary detection
            if "sentencizer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("sentencizer")
            # Disable parser initially for better performance (re-enable when needed)
            if "parser" in self.nlp.pipe_names:
                self.nlp.disable_pipe("parser")
        except OSError:
            logging.warning("spaCy English model not found, using blank model")
            self.nlp = spacy.blank("en")
            # Add sentencizer to blank model
            self.nlp.add_pipe("sentencizer")
        
        # Cache for processed results to avoid recomputing identical texts
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._max_cache_size = 100
        
        # Enhanced word importance weights
        self.importance_weights = {
            'NOUN': 1.0,
            'PROPN': 1.2,  # Proper nouns are more important
            'VERB': 0.8,
            'ADJ': 0.7,
            'ADV': 0.5,
            'NUM': 0.6
        }
        
        # Semantic categories for better pattern recognition
        self.semantic_categories = {
            'emotions': ['happy', 'sad', 'angry', 'excited', 'calm', 'anxious', 'love', 'hate', 'fear', 'joy'],
            'actions': ['run', 'walk', 'think', 'create', 'destroy', 'build', 'learn', 'teach', 'help'],
            'descriptors': ['beautiful', 'ugly', 'fast', 'slow', 'big', 'small', 'important', 'trivial'],
            'temporal': ['now', 'then', 'future', 'past', 'today', 'tomorrow', 'yesterday', 'always', 'never']
        }
        
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive NLP analysis with caching and optimization.
        Returns a dictionary with sentiment, entities, and tree structure data.
        """
        if not text or len(text.strip()) == 0:
            return self._empty_result()
        
        # Create cache key
        cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # Check cache first
        with self._cache_lock:
            if cache_key in self._cache:
                logging.debug(f"Cache hit for text: {text[:50]}...")
                return self._cache[cache_key]
        
        try:
            start_time = time.time()
            
            # Parallel processing for better performance
            sentiment = self._analyze_sentiment_optimized(text)
            
            # spaCy processing with optimizations
            doc = self.nlp(text)
            
            # Extract components in parallel where possible
            entities = self._extract_entities_enhanced(doc)
            relationships = self._extract_relationships_enhanced(doc)
            semantic_patterns = self._extract_semantic_patterns(doc, text)
            symbolic_resonance = self._calculate_symbolic_resonance(doc, sentiment)
            
            # Generate enhanced tree structure
            tree_data = self._generate_enhanced_tree_structure(
                text, doc, entities, relationships, sentiment, 
                semantic_patterns, symbolic_resonance
            )
            
            # Calculate additional metrics
            complexity_score = self._calculate_text_complexity(doc)
            readability_score = self._calculate_readability(text, doc)
            
            result = {
                'sentiment': sentiment,
                'entities': entities,
                'relationships': relationships,
                'semantic_patterns': semantic_patterns,
                'symbolic_resonance': symbolic_resonance,
                'tree_data': tree_data,
                'word_count': len([token for token in doc if not token.is_space]),
                'sentence_count': len(list(doc.sents)),
                'complexity_score': complexity_score,
                'readability_score': readability_score,
                'processing_time': round(time.time() - start_time, 3)
            }
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            logging.debug(f"Analysis completed in {result['processing_time']}s")
            return result
            
        except Exception as e:
            logging.error(f"NLP processing error: {str(e)}")
            raise
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure for invalid input."""
        return {
            'sentiment': {'polarity': 0.0, 'subjectivity': 0.0, 'confidence': 0.0},
            'entities': [],
            'relationships': [],
            'semantic_patterns': [],
            'symbolic_resonance': 0.0,
            'tree_data': {'name': 'Empty', 'type': 'root', 'children': []},
            'word_count': 0,
            'sentence_count': 0,
            'complexity_score': 0.0,
            'readability_score': 0.0,
            'processing_time': 0.0
        }
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache the analysis result with size management."""
        with self._cache_lock:
            if len(self._cache) >= self._max_cache_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            self._cache[cache_key] = result
    
    def _analyze_sentiment_optimized(self, text: str) -> Dict[str, float]:
        """Optimized sentiment analysis with enhanced confidence calculation."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Enhanced confidence calculation based on text length and word intensity
        intensity_words = ['very', 'extremely', 'absolutely', 'completely', 'totally', 
                          'utterly', 'quite', 'rather', 'really', 'truly', 'deeply']
        
        intensity_count = sum(1 for word in intensity_words if word.lower() in text.lower())
        base_confidence = abs(polarity)
        length_factor = min(len(text.split()) / 50, 1.0)  # Normalize by typical sentence length
        intensity_factor = min(intensity_count / 10, 0.3)  # Cap intensity bonus
        
        confidence = min(base_confidence + length_factor * 0.2 + intensity_factor, 1.0)
        
        return {
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'confidence': round(confidence, 3)
        }
    
    def _extract_entities_enhanced(self, doc) -> List[Dict[str, Any]]:
        """Enhanced entity extraction with confidence scoring and categorization."""
        entities = []
        entity_freq = Counter()
        
        for ent in doc.ents:
            entity_freq[ent.text.lower()] += 1
            
        for ent in doc.ents:
            # Calculate entity importance based on frequency and type
            importance = self._calculate_entity_importance(ent, entity_freq)
            
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'description': spacy.explain(ent.label_) or ent.label_,
                'importance': importance,
                'frequency': entity_freq[ent.text.lower()],
                'sentiment_context': self._get_entity_sentiment_context(ent, doc)
            })
        
        # Sort by importance for better visualization
        entities.sort(key=lambda x: x['importance'], reverse=True)
        return entities[:20]  # Limit to top 20 for performance
    
    def _calculate_entity_importance(self, ent, entity_freq: Counter) -> float:
        """Calculate entity importance based on type, frequency, and position."""
        base_weights = {
            'PERSON': 1.0, 'ORG': 0.9, 'GPE': 0.8, 'PRODUCT': 0.7,
            'EVENT': 0.8, 'DATE': 0.6, 'TIME': 0.5, 'MONEY': 0.7,
            'CARDINAL': 0.4, 'ORDINAL': 0.3
        }
        
        base_score = base_weights.get(ent.label_, 0.5)
        frequency_score = min(entity_freq[ent.text.lower()] / 5, 1.0)  # Normalize frequency
        length_bonus = min(len(ent.text) / 20, 0.3)  # Longer entities often more important
        
        return round(base_score + frequency_score * 0.3 + length_bonus, 3)
    
    def _get_entity_sentiment_context(self, ent, doc) -> str:
        """Analyze sentiment context around entity."""
        # Get surrounding tokens for context
        start_idx = max(0, ent.start - 3)
        end_idx = min(len(doc), ent.end + 3)
        context_tokens = doc[start_idx:end_idx]
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'best', 'love']
        negative_words = ['bad', 'terrible', 'awful', 'worst', 'hate', 'horrible', 'poor']
        
        context_text = ' '.join([token.text.lower() for token in context_tokens])
        
        pos_count = sum(1 for word in positive_words if word in context_text)
        neg_count = sum(1 for word in negative_words if word in context_text)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
    
    def _extract_relationships_enhanced(self, doc) -> List[Dict[str, Any]]:
        """Enhanced relationship extraction with semantic analysis."""
        # Re-enable parser for dependency analysis
        if "parser" not in self.nlp.pipe_names:
            self.nlp.enable_pipe("parser")
        
        relationships = []
        important_deps = [
            'nsubj', 'dobj', 'pobj', 'amod', 'compound', 'prep', 
            'agent', 'attr', 'ccomp', 'xcomp', 'acl'
        ]
        
        for token in doc:
            if token.dep_ in important_deps and not token.is_stop:
                strength = self._calculate_relationship_strength(token)
                
                relationships.append({
                    'source': token.text,
                    'target': token.head.text,
                    'relation': token.dep_,
                    'description': spacy.explain(token.dep_) or token.dep_,
                    'strength': strength,
                    'pos_source': token.pos_,
                    'pos_target': token.head.pos_,
                    'semantic_type': self._classify_relationship_semantics(token)
                })
        
        # Filter and sort by strength
        relationships = [r for r in relationships if r['strength'] > 0.3]
        relationships.sort(key=lambda x: x['strength'], reverse=True)
        return relationships[:15]  # Limit for performance
    
    def _calculate_relationship_strength(self, token) -> float:
        """Calculate the semantic strength of a relationship."""
        base_weights = {
            'nsubj': 1.0, 'dobj': 0.9, 'amod': 0.7, 'compound': 0.8,
            'prep': 0.6, 'agent': 0.8, 'attr': 0.7, 'ccomp': 0.6
        }
        
        base_score = base_weights.get(token.dep_, 0.5)
        
        # Boost for important POS tags
        pos_boost = 0.2 if token.pos_ in ['NOUN', 'PROPN', 'VERB'] else 0.0
        head_boost = 0.1 if token.head.pos_ in ['NOUN', 'PROPN', 'VERB'] else 0.0
        
        # Penalize very common words
        frequency_penalty = 0.2 if token.is_stop or token.head.is_stop else 0.0
        
        return max(0.0, base_score + pos_boost + head_boost - frequency_penalty)
    
    def _classify_relationship_semantics(self, token) -> str:
        """Classify the semantic type of relationship."""
        if token.dep_ in ['nsubj', 'agent']:
            return 'actor'
        elif token.dep_ in ['dobj', 'pobj']:
            return 'object'
        elif token.dep_ in ['amod', 'attr']:
            return 'descriptor'  
        elif token.dep_ in ['compound', 'prep']:
            return 'modifier'
        else:
            return 'other'
    
    def _extract_semantic_patterns(self, doc, text: str) -> List[Dict[str, Any]]:
        """Extract semantic patterns and thematic structures."""
        patterns = []
        
        # Extract key phrases based on POS patterns
        key_phrases = self._extract_key_phrases(doc)
        
        # Categorize words by semantic meaning
        semantic_clusters = self._cluster_semantic_meanings(doc)
        
        # Find emotional patterns
        emotional_patterns = self._extract_emotional_patterns(doc, text)
        
        # Detect narrative structure
        narrative_elements = self._detect_narrative_elements(doc)
        
        return {
            'key_phrases': key_phrases,
            'semantic_clusters': semantic_clusters,
            'emotional_patterns': emotional_patterns,
            'narrative_elements': narrative_elements
        }
    
    def _extract_key_phrases(self, doc) -> List[Dict[str, Any]]:
        """Extract key phrases using linguistic patterns."""
        key_phrases = []
        
        # Common patterns for key phrases
        patterns = [
            ['ADJ', 'NOUN'],  # Adjective + Noun
            ['NOUN', 'NOUN'],  # Compound nouns
            ['VERB', 'ADV'],   # Verb + Adverb
            ['ADV', 'ADJ'],    # Adverb + Adjective
        ]
        
        tokens = [token for token in doc if not token.is_stop and not token.is_punct]
        
        for i in range(len(tokens) - 1):
            current_pattern = [tokens[i].pos_, tokens[i + 1].pos_]
            
            if current_pattern in patterns:
                phrase = f"{tokens[i].text} {tokens[i + 1].text}"
                importance = self._calculate_phrase_importance(tokens[i], tokens[i + 1])
                
                if importance > 0.3:
                    key_phrases.append({
                        'phrase': phrase,
                        'importance': importance,
                        'pattern': '_'.join(current_pattern),
                        'start': tokens[i].idx,
                        'end': tokens[i + 1].idx + len(tokens[i + 1].text)
                    })
        
        # Sort by importance and return top phrases
        key_phrases.sort(key=lambda x: x['importance'], reverse=True)
        return key_phrases[:10]
    
    def _calculate_phrase_importance(self, token1, token2) -> float:
        """Calculate importance of a two-word phrase."""
        # Base importance from POS weights
        weight1 = self.importance_weights.get(token1.pos_, 0.5)
        weight2 = self.importance_weights.get(token2.pos_, 0.5)
        
        # Length bonus for longer words
        length_bonus = (len(token1.text) + len(token2.text)) / 20
        
        # Penalty for very common words
        frequency_penalty = 0.3 if (token1.is_stop or token2.is_stop) else 0.0
        
        return max(0.0, (weight1 + weight2) / 2 + length_bonus - frequency_penalty)
    
    def _cluster_semantic_meanings(self, doc) -> Dict[str, List[str]]:
        """Cluster words by semantic categories."""
        clusters = {category: [] for category in self.semantic_categories}
        
        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.text) > 2:
                lemma = token.lemma_.lower()
                
                for category, words in self.semantic_categories.items():
                    if lemma in words or any(word in lemma for word in words):
                        clusters[category].append({
                            'word': token.text,
                            'lemma': lemma,
                            'pos': token.pos_,
                            'importance': self.importance_weights.get(token.pos_, 0.5)
                        })
        
        # Remove empty clusters and sort by importance
        return {k: sorted(v, key=lambda x: x['importance'], reverse=True)[:5] 
                for k, v in clusters.items() if v}
    
    def _extract_emotional_patterns(self, doc, text: str) -> Dict[str, Any]:
        """Extract emotional patterns and intensity."""
        emotion_words = {
            'joy': ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'thrilled'],
            'sadness': ['sad', 'sorrow', 'grief', 'melancholy', 'depressed', 'gloomy'],
            'anger': ['angry', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened']
        }
        
        emotion_scores = {}
        text_lower = text.lower()
        
        for emotion, words in emotion_words.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                emotion_scores[emotion] = {
                    'score': score,
                    'intensity': min(score / len(words), 1.0),
                    'detected_words': [word for word in words if word in text_lower]
                }
        
        return emotion_scores
    
    def _detect_narrative_elements(self, doc) -> Dict[str, List[str]]:
        """Detect narrative elements like characters, actions, settings."""
        elements = {
            'characters': [],
            'actions': [],
            'settings': [],
            'temporal_markers': []
        }
        
        for token in doc:
            # Characters (people, pronouns)
            if token.pos_ in ['PROPN'] or token.ent_type_ == 'PERSON':
                if token.text not in elements['characters']:
                    elements['characters'].append(token.text)
            
            # Actions (verbs)
            elif token.pos_ == 'VERB' and not token.is_stop:
                elements['actions'].append(token.lemma_)
            
            # Settings (places, organizations)
            elif token.ent_type_ in ['GPE', 'LOC', 'ORG']:
                if token.text not in elements['settings']:
                    elements['settings'].append(token.text)
            
            # Temporal markers
            elif token.ent_type_ in ['DATE', 'TIME'] or token.lemma_.lower() in self.semantic_categories['temporal']:
                elements['temporal_markers'].append(token.text)
        
        return {k: list(set(v))[:5] for k, v in elements.items()}  # Remove duplicates, limit items
    
    def _calculate_symbolic_resonance(self, doc, sentiment: Dict[str, float]) -> float:
        """Calculate overall symbolic resonance score."""
        # Base score from sentiment intensity
        base_score = abs(sentiment['polarity']) * sentiment['confidence']
        
        # Complexity bonus (more complex = higher resonance potential)
        unique_pos = len(set(token.pos_ for token in doc if not token.is_stop))
        complexity_bonus = min(unique_pos / 10, 0.3)
        
        # Entity richness bonus
        entity_count = len([token for token in doc if token.ent_type_])
        entity_bonus = min(entity_count / 20, 0.2)
        
        # Vocabulary richness
        unique_words = len(set(token.lemma_.lower() for token in doc 
                               if not token.is_stop and not token.is_punct))
        total_words = len([token for token in doc if not token.is_stop and not token.is_punct])
        
        vocab_ratio = unique_words / max(total_words, 1)
        vocab_bonus = min(vocab_ratio, 0.3)
        
        resonance = base_score + complexity_bonus + entity_bonus + vocab_bonus
        return min(round(resonance, 3), 1.0)  # Cap at 1.0
    
    def _calculate_text_complexity(self, doc) -> float:
        """Calculate text complexity score."""
        if not doc:
            return 0.0
        
        # Average sentence length
        sentences = list(doc.sents)
        if not sentences:
            return 0.0
        
        avg_sentence_length = sum(len([token for token in sent if not token.is_space]) 
                                for sent in sentences) / len(sentences)
        
        # Vocabulary diversity
        words = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
        unique_words = len(set(words))
        total_words = len(words)
        
        diversity = unique_words / max(total_words, 1)
        
        # Syntactic complexity (variety of POS tags)
        pos_variety = len(set(token.pos_ for token in doc)) / 17  # 17 universal POS tags
        
        # Combine metrics
        complexity = (avg_sentence_length / 20 + diversity + pos_variety) / 3
        return min(round(complexity, 3), 1.0)
    
    def _calculate_readability(self, text: str, doc) -> float:
        """Calculate readability score (simplified)."""
        if not text or not doc:
            return 0.0
        
        sentences = list(doc.sents)
        words = [token for token in doc if not token.is_space and not token.is_punct]
        
        if not sentences or not words:
            return 0.0
        
        # Average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Average syllables per word (approximated by vowel count)
        total_syllables = sum(max(1, len([c for c in word.text.lower() if c in 'aeiou'])) 
                            for word in words)
        avg_syllables_per_word = total_syllables / len(words)
        
        # Simplified Flesch-like score (higher = more readable)
        readability = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale
        normalized = max(0, min(100, readability)) / 100
        return round(normalized, 3)
    
    def _generate_enhanced_tree_structure(self, text: str, doc, entities: List[Dict], 
                                        relationships: List[Dict], sentiment: Dict[str, float], 
                                        semantic_patterns: Dict, symbolic_resonance: float) -> Dict[str, Any]:
        """
        Generate an enhanced hierarchical tree structure representing symbolic resonance patterns.
        """
        # Enhanced root node with symbolic resonance
        sentiment_label = ("Positive" if sentiment['polarity'] > 0.1 else 
                          "Negative" if sentiment['polarity'] < -0.1 else "Neutral")
        
        root = {
            'name': f"{sentiment_label} Resonance ({symbolic_resonance:.2f})",
            'type': 'root',
            'value': symbolic_resonance,
            'sentiment': sentiment,
            'resonance_score': symbolic_resonance,
            'children': []
        }
        
        # Enhanced entity branches with importance scoring
        if entities:
            entity_groups = defaultdict(list)
            for entity in entities:
                entity_groups[entity['label']].append(entity)
            
            for entity_type, entity_list in entity_groups.items():
                if entity_list:
                    # Calculate group importance
                    group_importance = sum(e.get('importance', 0.5) for e in entity_list) / len(entity_list)
                    
                    entity_node = {
                        'name': f"{entity_type} ({len(entity_list)})",
                        'type': 'entity_group',
                        'value': group_importance,
                        'description': entity_list[0].get('description', entity_type),
                        'children': []
                    }
                    
                    # Add top entities by importance
                    sorted_entities = sorted(entity_list, key=lambda x: x.get('importance', 0), reverse=True)
                    for entity in sorted_entities[:5]:
                        entity_child = {
                            'name': f"{entity['text']} ({entity.get('importance', 0.5):.2f})",
                            'type': 'entity',
                            'value': entity.get('importance', 0.5),
                            'entity_data': entity,
                            'sentiment_context': entity.get('sentiment_context', 'neutral'),
                            'children': []
                        }
                        entity_node['children'].append(entity_child)
                    
                    root['children'].append(entity_node)
        
        # Enhanced relationship branches with strength scoring
        if relationships:
            rel_groups = defaultdict(list)
            for rel in relationships:
                rel_groups[rel.get('semantic_type', rel['relation'])].append(rel)
            
            for rel_type, rel_list in rel_groups.items():
                if rel_list:
                    # Calculate average strength
                    avg_strength = sum(r.get('strength', 0.5) for r in rel_list) / len(rel_list)
                    
                    rel_node = {
                        'name': f"{rel_type.upper()} Relations ({len(rel_list)})",
                        'type': 'relationship_group',
                        'value': avg_strength,
                        'description': f"Semantic relationships of type: {rel_type}",
                        'children': []
                    }
                    
                    # Add strongest relationships
                    sorted_rels = sorted(rel_list, key=lambda x: x.get('strength', 0), reverse=True)
                    for rel in sorted_rels[:4]:
                        rel_child = {
                            'name': f"{rel['source']} → {rel['target']} ({rel.get('strength', 0.5):.2f})",
                            'type': 'relationship',
                            'value': rel.get('strength', 0.5),
                            'relationship_data': rel,
                            'children': []
                        }
                        rel_node['children'].append(rel_child)
                    
                    root['children'].append(rel_node)
        
        # Semantic pattern branches
        if semantic_patterns.get('key_phrases'):
            phrase_node = {
                'name': f"Key Phrases ({len(semantic_patterns['key_phrases'])})",
                'type': 'phrase_group',
                'value': 0.8,
                'description': "Important linguistic patterns and phrases",
                'children': []
            }
            
            for phrase_data in semantic_patterns['key_phrases'][:6]:
                phrase_child = {
                    'name': f"{phrase_data['phrase']} ({phrase_data['importance']:.2f})",
                    'type': 'phrase',
                    'value': phrase_data['importance'],
                    'pattern': phrase_data['pattern'],
                    'children': []
                }
                phrase_node['children'].append(phrase_child)
            
            root['children'].append(phrase_node)
        
        # Emotional pattern branches
        if semantic_patterns.get('emotional_patterns'):
            emotion_node = {
                'name': f"Emotional Patterns ({len(semantic_patterns['emotional_patterns'])})",
                'type': 'emotion_group',
                'value': 0.7,
                'description': "Detected emotional patterns and intensities",
                'children': []
            }
            
            for emotion, data in semantic_patterns['emotional_patterns'].items():
                emotion_child = {
                    'name': f"{emotion.title()} ({data['intensity']:.2f})",
                    'type': 'emotion',
                    'value': data['intensity'],
                    'detected_words': data['detected_words'],
                    'children': []
                }
                emotion_node['children'].append(emotion_child)
            
            root['children'].append(emotion_node)
        
        # Semantic cluster branches
        if semantic_patterns.get('semantic_clusters'):
            for cluster_name, cluster_words in semantic_patterns['semantic_clusters'].items():
                if cluster_words:
                    cluster_node = {
                        'name': f"{cluster_name.title()} ({len(cluster_words)})",
                        'type': 'semantic_cluster',
                        'value': len(cluster_words) / 10,  # Normalize
                        'description': f"Words related to {cluster_name}",
                        'children': []
                    }
                    
                    for word_data in cluster_words[:4]:
                        word_child = {
                            'name': f"{word_data['word']} ({word_data['importance']:.2f})",
                            'type': 'semantic_word',
                            'value': word_data['importance'],
                            'pos': word_data['pos'],
                            'children': []
                        }
                        cluster_node['children'].append(word_child)
                    
                    root['children'].append(cluster_node)
        
        # Narrative elements (if detected)
        narrative = semantic_patterns.get('narrative_elements', {})
        if any(narrative.values()):
            narrative_node = {
                'name': "Narrative Elements",
                'type': 'narrative_group',
                'value': 0.6,
                'description': "Story elements and narrative structure",
                'children': []
            }
            
            for element_type, elements in narrative.items():
                if elements:
                    element_child = {
                        'name': f"{element_type.replace('_', ' ').title()} ({len(elements)})",
                        'type': 'narrative_element',
                        'value': len(elements) / 10,
                        'elements': elements,
                        'children': []
                    }
                    narrative_node['children'].append(element_child)
            
            if narrative_node['children']:
                root['children'].append(narrative_node)
        
        return root
    
    def _extract_key_words(self, doc):
        """Extract key words based on frequency and importance."""
        word_freq = Counter()
        
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                len(token.text) > 2 and
                token.pos_ in ['NOUN', 'ADJ', 'VERB']):
                word_freq[token.lemma_.lower()] += 1
        
        return word_freq.most_common(10)
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        with self._cache_lock:
            self._cache.clear()
            logging.info("NLP cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._cache_lock:
            return {
                'cache_size': len(self._cache),
                'max_cache_size': self._max_cache_size,
                'cached_analyses': list(self._cache.keys())[:5]  # Show first 5 cache keys
            }
