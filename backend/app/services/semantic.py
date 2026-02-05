"""
Semantic similarity-based need type detection.

Uses SpaCy word vectors to handle synonyms and novel terms
without maintaining hardcoded keyword lists.
"""
from typing import Optional, Dict
import spacy

# Load SpaCy NLP (must initialize lazily to avoid import-time errors)
_nlp = None
_seed_docs = None


def _init_nlp():
    """Lazy initialization of SpaCy and seed documents."""
    global _nlp, _seed_docs
    
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_md")
            
            # Create seed documents for each need type
            # These represent the "semantic fingerprint" of each category
            _seed_docs = {
                'medical': _nlp("ambulance doctor hospital emergency paramedic nurse injury wound bleeding"),
                'food': _nlp("food meal rice bread ration hunger nutrition khana bhojan"),
                'water': _nlp("water bottle drinking tanker thirsty paani jal"),
                'rescue': _nlp("trapped fire rescue evacuation firefighters stuck collapsed burning"),
                'shelter': _nlp("tent accommodation homeless camp roof housing"),
                'transport': _nlp("vehicle bus car truck evacuation transport"),
                'blankets': _nlp("blanket warm clothes clothing kambal"),
            }
        except OSError:
            # Model not available - semantic features disabled
            _nlp = None
            _seed_docs = None


def extract_need_type_semantic(text: str, threshold: float = 0.5) -> Optional[Dict]:
    """
    Extract need type using semantic similarity.
    
    Handles synonyms and novel terms without keyword lists:
    - "firefighters" → rescue (even if not in keywords)
    - "paramedic" → medical (via word vectors)
    - "starving" → food (semantic similarity)
    
    Args:
        text: Raw crisis message text
        threshold: Minimum similarity score (0.0-1.0)
        
    Returns:
        Dict with need_type, confidence, method or None
    """
    _init_nlp()
    
    # Fallback if model not available
    if _nlp is None or _seed_docs is None:
        return None
    
    try:
        doc = _nlp(text.lower())
        
        # Calculate similarity to each need type seed
        scores = {}
        for need_type, seed_doc in _seed_docs.items():
            similarity = doc.similarity(seed_doc)
            scores[need_type] = similarity
        
        # Find best match
        best_match = max(scores.items(), key=lambda x: x[1])
        
        if best_match[1] >= threshold:
            return {
                'need_type': best_match[0],
                'confidence': round(best_match[1], 2),
                'method': 'semantic',
                'all_scores': {k: round(v, 2) for k, v in scores.items()}
            }
        
        return None
        
    except Exception as e:
        # Graceful degradation if semantic matching fails
        print(f"⚠️  Semantic extraction failed: {e}")
        return None
