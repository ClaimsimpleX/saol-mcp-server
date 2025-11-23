import logging
import os
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import google.auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def _get_drive_service():
    """
    Authenticates and returns the Google Drive service.
    Uses Application Default Credentials (ADC) or Service Account File.
    """
    creds = None
    try:
        # Try to use ADC or environment variable
        creds, project = google.auth.default(scopes=SCOPES)
        logger.info("Authenticated with Google Drive using default credentials.")
    except Exception as e:
        logger.warning(f"Failed to authenticate with Google Drive: {e}")
        return None

    return build('drive', 'v3', credentials=creds)

def upload_file(content: str, filename: str, folder_id: Optional[str] = None) -> str:
    """
    Uploads a file to Google Drive.
    
    Args:
        content (str): The text content of the file.
        filename (str): The name of the file.
        folder_id (Optional[str]): The ID of the folder to upload to.
        
    Returns:
        str: The webViewLink of the uploaded file, or an error message.
    """
    service = _get_drive_service()
    if not service:
        return "Error: Google Drive authentication failed."

    try:
        file_metadata = {'name': filename}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Create a media upload object from the string content
        fh = io.BytesIO(content.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='text/plain')

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        logger.info(f"File ID: {file.get('id')} uploaded successfully.")
        return file.get('webViewLink')

    except Exception as e:
        logger.error(f"Error uploading file to Drive: {e}")
        return f"Error uploading file: {e}"

def delete_file(file_id: str) -> str:
    """
    Deletes a file from Google Drive.
    
    Args:
        file_id (str): The ID of the file to delete.
        
    Returns:
        str: Success message or error.
    """
    service = _get_drive_service()
    if not service:
        return "Error: Google Drive authentication failed."
        
    try:
        service.files().delete(fileId=file_id).execute()
        logger.info(f"File ID: {file_id} deleted successfully.")
        return f"Successfully deleted file {file_id}"
    except Exception as e:
        logger.error(f"Error deleting file from Drive: {e}")
        return f"Error deleting file: {e}"
