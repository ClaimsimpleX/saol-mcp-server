import logging
from typing import Dict, Any
from src.tools.firebase_ops import _db, init_firebase
from src.core.telemetry_schema import MissionReceipt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_mission_receipt(receipt: Dict[str, Any]) -> str:
    """
    Logs the mission receipt to the 'telemetry_ledger' collection in Firestore.
    
    Args:
        receipt (Dict[str, Any]): The mission receipt data.
        
    Returns:
        str: Success message or error.
    """
    if not _db and not init_firebase():
        return "Error: Firebase not initialized"

    try:
        # Validate against schema (optional but good practice)
        # We assume the caller passes a dict that matches the schema, 
        # or we could parse it: MissionReceipt(**receipt)
        # Let's just write it.
        
        # Use ticket_id as document ID or auto-generate?
        # Using ticket_id might overwrite if multiple spokes process same ticket (retries).
        # Better to use auto-id or composite key.
        
        collection_ref = _db.collection('telemetry_ledger')
        doc_ref = collection_ref.add(receipt)
        
        logger.info(f"Telemetry logged. Document ID: {doc_ref[1].id}")
        return f"Telemetry logged successfully. ID: {doc_ref[1].id}"
    except Exception as e:
        logger.error(f"Error logging telemetry: {e}")
        return f"Error logging telemetry: {e}"
