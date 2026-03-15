"""
Google Drive Sync Service.
Periodically exports database tables to JSON files and uploads them to a shared Google Drive folder.
"""

import os
import json
import time
import logging
import threading
import io
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from app.database import SessionLocal
from app.models.user import User
from app.models.topic import Topic
from app.models.subtopic import SubTopic
from app.models.note import Note
from app.models.resource import Resource
from app.models.project import Project
from app.models.streak import Streak

logger = logging.getLogger("gdrive_sync")

# ── LOGGING ──────────────────────────────────────────────────────────────────
# Add FileHandler so logs are persisted in a file
log_file = os.path.join(os.getcwd(), "app.log")
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

# ── MODIFICATION TRACKER ──────────────────────────────────────────────────────
_HAS_CHANGES = False
_sync_lock = threading.Lock()

def mark_modified():
    """Call this whenever data is created/updated/deleted in the DB."""
    global _HAS_CHANGES
    with _sync_lock:
        _HAS_CHANGES = True
    logger.debug("Database marked as modified. Pending sync.")


# ── CONFIG ────────────────────────────────────────────────────────────────────
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
SYNC_INTERVAL_SECONDS = int(os.getenv("GDRIVE_SYNC_INTERVAL", "300"))
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

TOKEN_PATH = "token.json"
CREDS_PATH = "credentials.json"

class GDriveSyncService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._init_client()

    def _init_client(self):
        """Initialize GDrive API client using token.json (OAuth2) or Service Account."""
        if not GDRIVE_FOLDER_ID:
            logger.warning("GDRIVE_FOLDER_ID not set. Sync disabled.")
            return

        # 1. Try OAuth2 (Perfect for Personal Gmail)
        if os.path.exists(TOKEN_PATH):
            try:
                self.creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    with open(TOKEN_PATH, "w") as token:
                        token.write(self.creds.to_json())
            except Exception as e:
                logger.error("OAuth2 token refresh failed: %s — GDrive sync disabled. "
                             "Re-generate token.json or switch to a Service Account.", e)
                self.creds = None

            if self.creds:
                self.service = build("drive", "v3", credentials=self.creds)
                logger.info("Sync initialized (OAuth2/User Account).")
                return

        # 2. Fallback to Service Account (Keeping old logic just in case)
        sa_json = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            try:
                from google.oauth2 import service_account
                if sa_json.strip().startswith("{"):
                    info = json.loads(sa_json)
                    self.creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
                else:
                    self.creds = service_account.Credentials.from_service_account_file(sa_json, scopes=SCOPES)
                self.service = build("drive", "v3", credentials=self.creds)
                logger.info("Sync initialized (Service Account).")
                return
            except Exception as e:
                logger.error(f"Service account login failed: {e}")

        logger.warning("No valid credentials found. Run /tmp/gdrive_oauth_setup.py to login.")

    def get_table_data(self, db: Session, model):
        """Fetch all rows from a model and return as a list of dictionaries."""
        rows = db.query(model).all()
        data = []
        for row in rows:
            # Simple conversion: skip relationships, handle datetimes
            row_dict = {}
            for column in row.__table__.columns:
                val = getattr(row, column.name)
                if isinstance(val, datetime):
                    val = val.isoformat()
                row_dict[column.name] = val
            data.append(row_dict)
        return data

    def upload_file(self, filename: str, content: str):
        """Uploads or updates a file in the target GDrive folder."""
        if not self.service:
            return

        try:
            # 1. Check if file already exists in our folder
            query = f"name = '{filename}' and '{GDRIVE_FOLDER_ID}' in parents and trashed = false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get("files", [])

            fh = io.BytesIO(content.encode("utf-8"))
            media = MediaIoBaseUpload(fh, mimetype="application/json", resumable=True)

            if files:
                # Delete existing file(s) first as requested
                for f in files:
                    file_id = f["id"]
                    self.service.files().delete(fileId=file_id).execute()
                    logger.info(f"Deleted existing {filename} (ID: {file_id}) on GDrive.")

            # Create new file
            file_metadata = {
                "name": filename,
                "parents": [GDRIVE_FOLDER_ID]
            }
            self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            logger.info(f"Created new {filename} on GDrive.")
        except Exception as e:
            logger.error(f"Error syncing {filename} to GDrive: {e}")

    def download_file(self, filename: str) -> str:
        """Downloads a file's content from GDrive."""
        if not self.service:
            return ""

        try:
            query = f"name = '{filename}' and '{GDRIVE_FOLDER_ID}' in parents and trashed = false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get("files", [])

            if not files:
                logger.info(f"File {filename} not found on GDrive. Skipping download.")
                return ""

            file_id = files[0]["id"]
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return fh.getvalue().decode("utf-8")
        except Exception as e:
            logger.error(f"Error downloading {filename} from GDrive: {e}")
            return ""

    def sync_all_tables(self):
        """Syncs every table to GDrive as a JSON file."""
        if not self.service:
            logger.debug("Sync skipped (client not initialized).")
            return

        db = SessionLocal()
        try:
            tables = {
                "users.json": User,
                "topics.json": Topic,
                "subtopics.json": SubTopic,
                "notes.json": Note,
                "resources.json": Resource,
                "projects.json": Project,
                "streaks.json": Streak
            }

            logger.info("Starting GDrive sync cycle...")
            for filename, model in tables.items():
                data = self.get_table_data(db, model)
                content = json.dumps(data, indent=2)
                self.upload_file(filename, content)
            
            logger.info(f"Sync complete at {datetime.now(timezone.utc).isoformat()}")
        finally:
            db.close()

    def load_all_tables_from_gdrive(self):
        """Downloads all JSON files from GDrive and populates the database."""
        if not self.service:
            logger.debug("Load skipped (client not initialized).")
            return

        db = SessionLocal()
        try:
            # Order matters for foreign keys
            tables = [
                ("users.json", User),
                ("topics.json", Topic),
                ("subtopics.json", SubTopic),
                ("notes.json", Note),
                ("resources.json", Resource),
                ("projects.json", Project),
                ("streaks.json", Streak)
            ]

            logger.info("📥 Starting GDrive-to-DB data load...")
            for filename, model in tables:
                content = self.download_file(filename)
                if not content:
                    continue
                
                try:
                    data = json.loads(content)
                    if not isinstance(data, list):
                        continue
                    
                    for row_data in data:
                        # Convert ISO date strings back to datetime objects where needed
                        for col in model.__table__.columns:
                            if col.name in row_data and row_data[col.name] and "datetime" in str(col.type).lower():
                                try:
                                    row_data[col.name] = datetime.fromisoformat(row_data[col.name])
                                except (ValueError, TypeError):
                                    pass
                        
                        # Use merge to handle potential existing data (unlikely in memory but safer)
                        obj = model(**row_data)
                        db.merge(obj)
                    
                    db.commit()
                    logger.info(f"Loaded {len(data)} records from {filename}")
                except Exception as e:
                    logger.error(f"Error parsing/loading {filename}: {e}")
                    db.rollback()

            logger.info("✅ Data load from GDrive complete.")
        finally:
            db.close()

    def run_forever(self):
        """Run the sync cycle in a loop."""
        global _HAS_CHANGES
        if not self.service:
            logger.error("GDrive Sync loop cannot start: Missing credentials or folder ID.")
            return

        logger.info(f"GDrive Sync loop started (Interval: {SYNC_INTERVAL_SECONDS}s)")
        while True:
            # Atomic check and reset
            should_sync = False
            with _sync_lock:
                if _HAS_CHANGES:
                    should_sync = True
                    _HAS_CHANGES = False  # Reset it BEFORE starting the upload

            if should_sync:
                try:
                    self.sync_all_tables()
                except Exception as e:
                    # If it fails, put the flag back so we retry
                    with _sync_lock:
                        _HAS_CHANGES = True
                    logger.error(f"Critical error in GDrive sync loop: {e}")
            else:
                logger.debug("No changes detected. Skipping sync cycle.")
            
            time.sleep(SYNC_INTERVAL_SECONDS)


def start_gdrive_sync():
    """Starts the sync service in a background daemon thread."""
    service = GDriveSyncService()
    if not service.service:
        return
    
    # Load data from GDrive on startup
    service.load_all_tables_from_gdrive()
    
    thread = threading.Thread(target=service.run_forever, daemon=True, name="GDriveSyncThread")
    thread.start()
