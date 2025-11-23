import logging
import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_db = None

def init_firebase() -> bool:
    """
    Initializes the Firebase Admin SDK.
    Uses Application Default Credentials (ADC) or service account if provided.
    Returns True if successful, False otherwise.
    """
    global _db
    if _db:
        return True

    try:
        if not firebase_admin._apps:
            # Try to use ADC by default
            logger.info("Initializing Firebase with Application Default Credentials...")
            firebase_admin.initialize_app()
        
        _db = firestore.client()
        logger.info("Firebase initialized successfully.")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize Firebase: {e}. Tools depending on Firebase will fail.")
        return False

def read_queue(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Reads pending tickets from the ticket queue.
    
    Args:
        limit (int): Maximum number of tickets to retrieve.
        
    Returns:
        List[Dict[str, Any]]: List of ticket documents.
    """
    if not _db and not init_firebase():
        return [{"error": "Firebase not initialized"}]

    try:
        tickets_ref = _db.collection('ticket_queue')
        query = tickets_ref.where('status', '==', 'PENDING').limit(limit)
        docs = query.stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
            
        logger.info(f"Read {len(results)} tickets from queue.")
        return results
    except Exception as e:
        logger.error(f"Error reading queue: {e}")
        return [{"error": str(e)}]

def update_ticket(ticket_id: str, status: str, result: Optional[str] = None) -> str:
    """
    Updates the status and result of a ticket.
    
    Args:
        ticket_id (str): The ID of the ticket to update.
        status (str): The new status (e.g., 'PROCESSING', 'COMPLETE', 'ERROR').
        result (Optional[str]): The result of the processing.
        
    Returns:
        str: Success message or error description.
    """
    if not _db and not init_firebase():
        return "Error: Firebase not initialized"

    try:
        ticket_ref = _db.collection('ticket_queue').document(ticket_id)
        
        update_data = {
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if result:
            update_data['result'] = result
            
        ticket_ref.update(update_data)
        logger.info(f"Updated ticket {ticket_id} to status {status}.")
        return f"Successfully updated ticket {ticket_id}"
    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id}: {e}")
        return f"Error updating ticket: {e}"
