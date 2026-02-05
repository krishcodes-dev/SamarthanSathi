import logging
import json
from datetime import datetime
from pathlib import Path

# Configure logging
log_file_path = Path("samarthansathi.log")

# Create specific logger
logger = logging.getLogger('samarthansathi')
logger.setLevel(logging.INFO)

# Create handlers if not already added
if not logger.handlers:
    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def log_request_processing(request_id: str, raw_message: str, extraction_result: dict, urgency_result: dict = None):
    """Log crisis request processing for audit trail"""
    log_data = {
        'event': 'request_processed',
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': str(request_id),
        'raw_message': raw_message[:100] + "..." if len(raw_message) > 100 else raw_message,
        'extracted_need': extraction_result.get('need_type'),
        'extracted_location': extraction_result.get('location'),
        'urgency_level': urgency_result.get('level') if urgency_result else None,
        'urgency_score': urgency_result.get('score') if urgency_result else None,
        'confidence': extraction_result.get('overall_confidence')
    }
    logger.info(json.dumps(log_data))


def log_dispatch(request_id: str, resource_id: str, quantity: int, distance_km: float = None):
    """Log resource dispatch for audit trail"""
    log_data = {
        'event': 'resource_dispatched',
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': str(request_id),
        'resource_id': str(resource_id),
        'quantity': quantity,
        'distance_km': distance_km
    }
    logger.info(json.dumps(log_data))

def log_error(request_id: str, error_msg: str, context: str):
    """Log processing errors"""
    log_data = {
        'event': 'processing_error',
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': str(request_id),
        'context': context,
        'error': error_msg
    }
    logger.error(json.dumps(log_data))
