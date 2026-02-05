"""
Hybrid extraction orchestrator.

Combines multiple extraction strategies with intelligent fallback:
1. Rule-based keywords (fast, reliable for common terms)
2. Semantic similarity (handles synonyms, novel terms)
3. Hybrid geocoding (local cache + external API)
4. Contextual validation (cross-checking)
"""
from typing import Dict, Optional
from app.schemas.crisis import EntityExtraction
from app.services.extraction import extract_entities as extract_with_keywords
from app.services.semantic import extract_need_type_semantic
from app.services.geocoding import resolve_location_hybrid


def extract_entities_hybrid(text: str) -> EntityExtraction:
    """
    Hybrid entity extraction combining multiple strategies.
    
    Tiered approach:
    1. Start with rule-based keyword extraction (baseline)
    2. Enhance with semantic similarity if confidence low
    3. Use hybrid geocoding for locations
    4. Cross-validate with contextual rules
    
    Args:
        text: Raw crisis message text
        
    Returns:
        EntityExtraction with extracted entities and confidence scores
    """
    # === STRATEGY 1: Rule-Based Extraction (Baseline) ===
    # Your existing keyword-based extraction
    baseline = extract_with_keywords(text)
    
    # === STRATEGY 2: Semantic Enhancement (Fallback for Low Confidence) ===
    # If rule-based confidence is low, try semantic similarity
    if baseline.need_type_confidence and baseline.need_type_confidence < 0.7:
        semantic_result = extract_need_type_semantic(text)
        
        if semantic_result and semantic_result['confidence'] > baseline.need_type_confidence:
            # Semantic gave better result - use it!
            baseline.need_type = semantic_result['need_type']
            baseline.need_type_confidence = semantic_result['confidence']
            # Note: extraction_methods would need to be added to EntityExtraction schema
    
    # === STRATEGY 3: Hybrid Geocoding ===
    # Replace simple location extraction with hybrid resolver
    if baseline.location:
        location_result = resolve_location_hybrid(baseline.location)
        
        # Update location fields with hybrid result
        if location_result.get('lat') and location_result.get('lng'):
            baseline.location = location_result['location_name']
            baseline.latitude = location_result['lat']
            baseline.longitude = location_result['lng']
            baseline.location_confidence = location_result['confidence']
            
            if location_result.get('alternatives'):
                baseline.location_alternatives = location_result['alternatives']
            
            if location_result.get('flags'):
                baseline.flags = location_result['flags']
    
    # === STRATEGY 4: Contextual Validation & Confidence ===
    
    # Calculate overall confidence
    confs = [
        baseline.need_type_confidence or 0.0,
        baseline.location_confidence or 0.0,
        baseline.quantity_confidence or 0.0
    ]
    baseline.overall_confidence = round(sum(confs) / 3.0, 2)
    
    # Aggregate flags
    if baseline.flags is None:
        baseline.flags = []
    
    if (baseline.need_type_confidence or 0.0) < 0.6:
        baseline.flags.append('unclear_need_type')
    if not baseline.contact:
        baseline.flags.append('missing_contact_info')
    
    return baseline


# Backward compatibility: keep same interface
def extract_entities(text: str) -> EntityExtraction:
    """
    Main entity extraction entry point.
    
    Now uses hybrid extraction by default.
    """
    return extract_entities_hybrid(text)
