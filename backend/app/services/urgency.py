"""
Urgency scoring engine for crisis messages.

Provides explainable, feature-based urgency scoring on a 5-level scale (U1-U5).
"""
from typing import List, Tuple
from app.schemas.crisis import EntityExtraction, UrgencyAnalysis


# ===== URGENCY LEVEL DEFINITIONS =====

URGENCY_LEVELS = {
    "U1": {"name": "Critical", "threshold": 80, "description": "Life-threatening, immediate response required"},
    "U2": {"name": "High", "threshold": 60, "description": "Serious situation, response within 1 hour"},
    "U3": {"name": "Medium", "threshold": 40, "description": "Significant need, response within 4 hours"},
    "U4": {"name": "Low", "threshold": 20, "description": "Non-urgent, routine response"},
    "U5": {"name": "Minimal", "threshold": 0, "description": "Informational or low-priority"},
}


# ===== KEYWORD CATEGORIES =====

# Life-threatening keywords (+50 points)
LIFE_THREATENING_KEYWORDS = [
    'dying', 'dead', 'death', 'collapsed', 'unconscious', 'bleeding',
    'suffocating', 'drowning', 'heart attack', 'stroke', 'critical condition',
    'flatlined', 'not breathing', 'severe bleeding', 'major injury',
]

# High urgency keywords (+30 points)
HIGH_URGENCY_KEYWORDS = [
    'trapped', 'stuck', 'fire', 'burning', 'injured', 'wounded',
    'accident', 'emergency', 'urgent', 'asap', 'immediately',
    'sos', 'help', 'mayday', 'distress',
]

# Time-sensitive keywords (+20 points)
TIME_SENSITIVE_KEYWORDS = [
    'now', 'right now', 'immediately', 'urgent', 'quickly', 'fast',
    'running out', 'last', 'fading', 'deteriorating', 'worsening',
    'turant', 'jaldi', 'abhi',  # Hindi
]

# Vulnerable population keywords (+15 points)
VULNERABLE_KEYWORDS = [
    'child', 'children', 'infant', 'baby', 'elderly', 'old',
    'pregnant', 'disabled', 'handicapped', 'bachche', 'budhhe',
]

# Emotional/dramatic keywords (low weight, +5 points only)
EMOTIONAL_KEYWORDS = [
    'please', 'help me', 'desperate', 'crying', 'scared', 'terrified',
    'begging', 'pray', 'god',
]


# ===== NEED TYPE URGENCY WEIGHTS =====

NEED_TYPE_URGENCY = {
    'medical': 40,     # High base urgency
    'rescue': 45,      # Highest base urgency
    'water': 25,       # Medium urgency
    'food': 20,        # Medium-low urgency
    'shelter': 15,     # Low-medium urgency
    'blankets': 10,    # Low urgency
    'transport': 15,   # Low-medium urgency
}


# ===== QUANTITY MULTIPLIERS =====

def get_quantity_multiplier(affected_count: str) -> Tuple[float, str]:
    """
    Calculate urgency multiplier based on affected count.
    
    Args:
        affected_count: String representation of affected people
        
    Returns:
        Tuple of (multiplier, reasoning)
    """
    if not affected_count:
        return 1.0, "No affected count specified"
    
    # Parse numeric values from string
    if 'families' in affected_count.lower():
        try:
            count = int(affected_count.split()[0])
            # Assume 4 people per family
            people = count * 4
            if people >= 100:
                return 1.3, f"Large group: {count} families (~{people} people)"
            elif people >= 50:
                return 1.2, f"Significant group: {count} families (~{people} people)"
            else:
                return 1.1, f"Multiple families: {count} families"
        except (ValueError, IndexError):
            return 1.1, "Multiple families affected"
    
    elif 'injured' in affected_count.lower():
        # Injured people always get higher multiplier
        if 'multiple' in affected_count.lower() or 'many' in affected_count.lower():
            return 1.4, "Multiple people injured"
        elif 'several' in affected_count.lower():
            return 1.3, "Several people injured"
        else:
            try:
                count = int(affected_count.split()[0])
                if count >= 10:
                    return 1.5, f"Mass casualty: {count} injured"
                elif count >= 5:
                    return 1.4, f"Multiple casualties: {count} injured"
                else:
                    return 1.3, f"{count} people injured"
            except (ValueError, IndexError):
                return 1.3, "People injured"
    
    else:
        # Regular people count
        try:
            count = int(affected_count) if affected_count.isdigit() else int(affected_count.split()[0])
            if count >= 100:
                return 1.3, f"Large group: {count} people"
            elif count >= 50:
                return 1.2, f"Significant group: {count} people"
            elif count >= 10:
                return 1.1, f"Multiple people: {count}"
            else:
                return 1.0, f"Small group: {count} people"
        except (ValueError, IndexError):
            # Qualitative indicators
            qualitative_map = {
                'multiple': (1.2, "Multiple people affected"),
                'many': (1.3, "Many people affected"),
                'several': (1.2, "Several people affected"),
                'few': (1.0, "Few people affected"),
            }
            for keyword, (mult, reason) in qualitative_map.items():
                if keyword in affected_count.lower():
                    return mult, reason
            return 1.0, "Affected count unclear"


def score_keywords(text: str) -> Tuple[int, List[str]]:
    """
    Score urgency based on keyword presence.
    
    Args:
        text: Raw crisis message text
        
    Returns:
        Tuple of (score, reasoning_list)
    """
    score = 0
    reasoning = []
    text_lower = text.lower()
    
    # Check life-threatening keywords
    for keyword in LIFE_THREATENING_KEYWORDS:
        if keyword in text_lower:
            score += 50
            reasoning.append(f"⚠️  Life-threatening keyword: '{keyword}' (+50)")
            break  # Only count once
    
    # Check high urgency keywords
    high_urgency_count = 0
    for keyword in HIGH_URGENCY_KEYWORDS:
        if keyword in text_lower:
            high_urgency_count += 1
    if high_urgency_count > 0:
        points = min(high_urgency_count * 10, 30)  # Max 30 points
        score += points
        reasoning.append(f"🔴 High urgency keywords: {high_urgency_count} found (+{points})")
    
    # Check time-sensitive keywords
    time_count = 0
    for keyword in TIME_SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            time_count += 1
    if time_count > 0:
        points = min(time_count * 7, 20)  # Max 20 points
        score += points
        reasoning.append(f"⏰ Time-sensitive keywords: {time_count} found (+{points})")
    
    # Check vulnerable population
    for keyword in VULNERABLE_KEYWORDS:
        if keyword in text_lower:
            score += 15
            reasoning.append(f"👶 Vulnerable population: '{keyword}' (+15)")
            break  # Only count once
    
    # Check emotional keywords (low weight to avoid inflation)
    emotional_count = 0
    for keyword in EMOTIONAL_KEYWORDS:
        if keyword in text_lower:
            emotional_count += 1
    if emotional_count > 0:
        points = min(emotional_count * 2, 5)  # Max 5 points, very low weight
        score += points
        reasoning.append(f"💬 Emotional language: {emotional_count} found (+{points}) [low weight]")
    
    return score, reasoning


def score_need_type(need_type: str, confidence: float) -> Tuple[int, str]:
    """
    Score urgency based on need type.
    
    Args:
        need_type: Extracted need type
        confidence: Confidence score for need extraction
        
    Returns:
        Tuple of (score, reasoning)
    """
    if not need_type:
        return 0, "No need type identified"
    
    base_score = NEED_TYPE_URGENCY.get(need_type, 10)
    
    # Adjust by confidence
    adjusted_score = int(base_score * confidence)
    
    reasoning = f"📦 Need type: {need_type} (base: {base_score}, confidence: {confidence:.2f}, final: +{adjusted_score})"
    
    return adjusted_score, reasoning


def detect_understatement(text: str, extraction: EntityExtraction) -> Tuple[int, List[str]]:
    """
    Detect understated critical cases and boost score.
    
    Looks for patterns like:
    - Short, factual messages with critical needs
    - No emotional language but serious situation
    - Specific counts + critical need type
    
    Args:
        text: Raw crisis message text
        extraction: Extracted entities
        
    Returns:
        Tuple of (bonus_score, reasoning_list)
    """
    reasoning = []
    bonus = 0
    text_lower = text.lower()
    
    # Pattern 1: Short message with critical need (medical/rescue)
    if len(text) < 100 and extraction.need_type in ['medical', 'rescue']:
        # Check if NO emotional keywords present
        has_emotional = any(keyword in text_lower for keyword in EMOTIONAL_KEYWORDS)
        if not has_emotional:
            bonus += 15
            reasoning.append("📊 Understated critical case: Short, factual message with critical need (+15)")
    
    # Pattern 2: Specific numbers + no plea for help
    if extraction.quantity and extraction.affected_count:
        has_plea = any(word in text_lower for word in ['please', 'help', 'urgent'])
        if not has_plea:
            bonus += 10
            reasoning.append("📊 Factual reporting: Specific counts without emotional plea (+10)")
    
    # Pattern 3: Medical/rescue with location but no urgency keywords
    if extraction.need_type in ['medical', 'rescue'] and extraction.location:
        has_urgency = any(keyword in text_lower for keyword in HIGH_URGENCY_KEYWORDS)
        if not has_urgency:
            bonus += 12
            reasoning.append("📊 Calm critical report: Medical/rescue need with location, no panic (+12)")
    
    return bonus, reasoning


def calculate_urgency(text: str, extraction: EntityExtraction) -> UrgencyAnalysis:
    """
    Calculate urgency score with explainable reasoning.
    
    Args:
        text: Raw crisis message text
        extraction: Extracted entities from message
        
    Returns:
        UrgencyAnalysis with score, level, reasoning, and confidence
    """
    reasoning = []
    total_score = 0
    
    # 1. Keyword scoring
    keyword_score, keyword_reasoning = score_keywords(text)
    total_score += keyword_score
    reasoning.extend(keyword_reasoning)
    
    # 2. Need type scoring
    if extraction.need_type:
        need_score, need_reasoning = score_need_type(
            extraction.need_type,
            extraction.need_type_confidence or 0.5
        )
        total_score += need_score
        reasoning.append(need_reasoning)
    
    # 3. Quantity multiplier
    if extraction.affected_count:
        multiplier, mult_reasoning = get_quantity_multiplier(extraction.affected_count)
        total_score = int(total_score * multiplier)
        reasoning.append(f"👥 {mult_reasoning} (×{multiplier:.1f})")
    
    # 4. Understatement detection
    understatement_bonus, understatement_reasoning = detect_understatement(text, extraction)
    total_score += understatement_bonus
    reasoning.extend(understatement_reasoning)
    
    # 5. Cap at 100
    total_score = min(total_score, 100)
    
    # 6. Determine urgency level
    if total_score >= 80:
        level = "U1 - Critical"
        flags = ["Immediate dispatch required"]
    elif total_score >= 60:
        level = "U2 - High"
        flags = ["Response within 1 hour required"]
    elif total_score >= 40:
        level = "U3 - Medium"
        flags = []
    elif total_score >= 20:
        level = "U4 - Low"
        flags = []
    else:
        level = "U5 - Minimal"
        flags = []
    
    # 7. Additional flags
    if not extraction.contact:
        flags.append("Missing contact information")
    if not extraction.location:
        flags.append("Missing location information")
    if extraction.location and extraction.location_confidence and extraction.location_confidence < 0.6:
        flags.append("Ambiguous location - manual verification needed")
    
    # 8. Calculate confidence
    # High confidence if we have good extractions
    confidence_factors = []
    if extraction.need_type and extraction.need_type_confidence:
        confidence_factors.append(extraction.need_type_confidence)
    if extraction.location and extraction.location_confidence:
        confidence_factors.append(extraction.location_confidence)
    if extraction.quantity and extraction.quantity_confidence:
        confidence_factors.append(extraction.quantity_confidence)
    
    if confidence_factors:
        avg_confidence = sum(confidence_factors) / len(confidence_factors)
    else:
        avg_confidence = 0.5  # Default moderate confidence
    
    # Final reasoning summary
    reasoning.insert(0, f"🎯 Final urgency score: {total_score}/100")
    
    return UrgencyAnalysis(
        score=total_score,
        level=level,
        reasoning=reasoning,
        confidence=round(avg_confidence, 2),
        flags=flags if flags else None
    )
