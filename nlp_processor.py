import spacy
import logging
from collections import defaultdict, Counter
from textblob import TextBlob
import re

class NLPProcessor:
    def __init__(self):
        """Initialize the NLP processor with spaCy model."""
        try:
            # Try to load the English model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy English model not found, using blank model")
            # Create a blank English model if the full model isn't available
            self.nlp = spacy.blank("en")
        
    def analyze(self, text):
        """
        Perform comprehensive NLP analysis on the input text.
        Returns a dictionary with sentiment, entities, and tree structure data.
        """
        try:
            # Sentiment Analysis using TextBlob
            blob = TextBlob(text)
            sentiment = {
                'polarity': round(blob.sentiment.polarity, 3),
                'subjectivity': round(blob.sentiment.subjectivity, 3),
                'confidence': abs(blob.sentiment.polarity)  # Use polarity magnitude as confidence
            }
            
            # spaCy processing
            doc = self.nlp(text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'description': spacy.explain(ent.label_) or ent.label_
                })
            
            # Extract key phrases and relationships
            relationships = self._extract_relationships(doc)
            
            # Generate symbolic resonance tree
            tree_data = self._generate_tree_structure(text, doc, entities, relationships, sentiment)
            
            return {
                'sentiment': sentiment,
                'entities': entities,
                'relationships': relationships,
                'tree_data': tree_data,
                'word_count': len([token for token in doc if not token.is_space]),
                'sentence_count': len(list(doc.sents))
            }
            
        except Exception as e:
            logging.error(f"NLP processing error: {str(e)}")
            raise
    
    def _extract_relationships(self, doc):
        """Extract semantic relationships between tokens."""
        relationships = []
        
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj', 'pobj', 'amod', 'compound']:
                relationships.append({
                    'source': token.text,
                    'target': token.head.text,
                    'relation': token.dep_,
                    'description': spacy.explain(token.dep_) or token.dep_
                })
        
        return relationships
    
    def _generate_tree_structure(self, text, doc, entities, relationships, sentiment):
        """
        Generate a hierarchical tree structure representing symbolic resonance patterns.
        """
        # Root node based on overall sentiment
        sentiment_label = "Positive" if sentiment['polarity'] > 0.1 else "Negative" if sentiment['polarity'] < -0.1 else "Neutral"
        
        root = {
            'name': f"{sentiment_label} Resonance",
            'type': 'root',
            'value': abs(sentiment['polarity']),
            'sentiment': sentiment,
            'children': []
        }
        
        # Group entities by type
        entity_groups = defaultdict(list)
        for entity in entities:
            entity_groups[entity['label']].append(entity)
        
        # Create entity branches
        for entity_type, entity_list in entity_groups.items():
            if len(entity_list) > 0:
                entity_node = {
                    'name': f"{entity_type} ({len(entity_list)})",
                    'type': 'entity_group',
                    'value': len(entity_list),
                    'description': entity_list[0].get('description', entity_type),
                    'children': []
                }
                
                # Add individual entities
                for entity in entity_list[:5]:  # Limit to top 5 to avoid clutter
                    entity_child = {
                        'name': entity['text'],
                        'type': 'entity',
                        'value': len(entity['text']),
                        'entity_data': entity,
                        'children': []
                    }
                    entity_node['children'].append(entity_child)
                
                root['children'].append(entity_node)
        
        # Create semantic relationship branches
        if relationships:
            # Group relationships by type
            rel_groups = defaultdict(list)
            for rel in relationships:
                rel_groups[rel['relation']].append(rel)
            
            # Create relationship branches
            for rel_type, rel_list in rel_groups.items():
                if len(rel_list) > 0:
                    rel_node = {
                        'name': f"{rel_type.upper()} ({len(rel_list)})",
                        'type': 'relationship_group',
                        'value': len(rel_list),
                        'description': rel_list[0].get('description', rel_type),
                        'children': []
                    }
                    
                    # Add individual relationships
                    for rel in rel_list[:3]:  # Limit to top 3
                        rel_child = {
                            'name': f"{rel['source']} → {rel['target']}",
                            'type': 'relationship',
                            'value': 1,
                            'relationship_data': rel,
                            'children': []
                        }
                        rel_node['children'].append(rel_child)
                    
                    root['children'].append(rel_node)
        
        # Create thematic branches based on key words
        key_words = self._extract_key_words(doc)
        if key_words:
            theme_node = {
                'name': f"Key Themes ({len(key_words)})",
                'type': 'theme_group',
                'value': len(key_words),
                'children': []
            }
            
            for word, freq in key_words[:5]:  # Top 5 themes
                theme_child = {
                    'name': f"{word} ({freq})",
                    'type': 'theme',
                    'value': freq,
                    'children': []
                }
                theme_node['children'].append(theme_child)
            
            root['children'].append(theme_node)
        
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
