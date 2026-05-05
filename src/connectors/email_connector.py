import os
import imaplib
import email
import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from connectors.base import BaseConnector

class EmailConnector(BaseConnector):
    def __init__(self, connector_id: str, config: dict):
        super().__init__(connector_id, config)
        self.host = config.get("host")
        self.user = config.get("user")
        self.password = config.get("password")
        self.folder = config.get("folder", "INBOX")

    def fetch_updates(self, last_sync_state: Optional[str]) -> Tuple[List[Document], Optional[str]]:
        if not all([self.host, self.user, self.password]):
            print("[EmailConnector] Missing IMAP credentials in .env. Skipping.")
            return [], last_sync_state
            
        docs = []
        new_state = last_sync_state
        try:
            # Connect to the server
            mail = imaplib.IMAP4_SSL(self.host)
            mail.login(self.user, self.password)
            mail.select(self.folder)
            
            # Search for unseen emails using UID to easily track high-water mark
            status, messages = mail.uid('SEARCH', None, 'UNSEEN')
            
            if status != "OK":
                return [], new_state
                
            email_uids = messages[0].split()
            
            if not email_uids:
                mail.logout()
                return [], new_state
            
            # For prototype safety, limit to 10 latest unread emails
            max_uid = int(last_sync_state) if last_sync_state and last_sync_state.isdigit() else 0
            
            for uid_bytes in email_uids[-10:]:
                uid = int(uid_bytes)
                if uid <= max_uid:
                    continue # Skip if we've seen it, though UNSEEN should prevent this
                    
                # Fetch the email body
                res, msg = mail.uid('FETCH', uid_bytes, "(RFC822)")
                for response_part in msg:
                    if isinstance(response_part, tuple):
                        msg_obj = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject_header = decode_header(msg_obj["Subject"])[0]
                        subject, encoding = subject_header
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                            
                        # Decode sender
                        from_header = msg_obj.get("From")
                        if from_header:
                            sender, encoding = decode_header(from_header)[0]
                            if isinstance(sender, bytes):
                                sender = sender.decode(encoding if encoding else "utf-8", errors="ignore")
                        else:
                            sender = "Unknown Sender"
                            
                        # Extract body
                        body = ""
                        if msg_obj.is_multipart():
                            for part in msg_obj.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if content_type == "text/plain" and "attachment" not in content_disposition: #TODO: Handle attachments
                                    body_payload = part.get_payload(decode=True)
                                    if body_payload:
                                        body = body_payload.decode(errors="ignore")
                                    break
                        else:
                            body_payload = msg_obj.get_payload(decode=True)
                            if body_payload:
                                body = body_payload.decode(errors="ignore")
                            
                        date_header = msg_obj.get("Date")
                        source_ts = ""
                        if date_header:
                            try:
                                dt = parsedate_to_datetime(date_header)
                                source_ts = dt.astimezone(datetime.timezone.utc).isoformat()
                            except:
                                source_ts = ""
                                
                        retrieved_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                            
                        content = f"Email Subject: {subject}\nFrom: {sender}\nBody: {body}"
                        docs.append(Document(
                            page_content=content,
                            metadata={
                                "source": "email", 
                                "sender": sender, 
                                "subject": subject,
                                "connector_id": self.connector_id,
                                "source_timestamp": source_ts,
                                "retrieved_timestamp": retrieved_ts
                            }
                        ))
                        
                if uid > max_uid:
                    max_uid = uid
                    
            new_state = str(max_uid)
            mail.logout()
        except Exception as e:
            print(f"[EmailConnector] Error fetching emails: {e}")
            
        return docs, new_state
