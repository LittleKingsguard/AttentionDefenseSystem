import os
import datetime
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from connectors.base import BaseConnector
from git import Repo, exc

class GitConnector(BaseConnector):
    def __init__(self, connector_id: str, config: dict):
        super().__init__(connector_id, config)
        self.repo_path = config.get("repo_path", ".")
        
    def fetch_updates(self, last_sync_state: Optional[str]) -> Tuple[List[Document], Optional[str]]:
        if not self.repo_path or not os.path.exists(self.repo_path):
            print("[GitConnector] Invalid repo path. Skipping.")
            return [], last_sync_state
            
        docs = []
        new_state = last_sync_state
        last_ts = float(last_sync_state) if last_sync_state else 0.0
        try:
            repo = Repo(self.repo_path)
            # Fetch the 10 most recent commits to prototype
            commits = list(repo.iter_commits('HEAD', max_count=10))
            max_ts = last_ts
            
            for commit in commits:
                commit_ts = commit.committed_date
                if commit_ts <= last_ts:
                    continue
                    
                if commit_ts > max_ts:
                    max_ts = commit_ts
                    
                source_ts = datetime.datetime.fromtimestamp(commit_ts, tz=datetime.timezone.utc).isoformat()
                retrieved_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                content = f"Commit: {commit.hexsha}\nAuthor: {commit.author.name}\nMessage: {commit.message}"
                docs.append(Document(
                    page_content=content,
                    metadata={
                        "source": "git", 
                        "commit_hash": commit.hexsha, 
                        "author": commit.author.name,
                        "connector_id": self.connector_id,
                        "source_timestamp": source_ts,
                        "retrieved_timestamp": retrieved_ts
                    }
                ))
                
            new_state = str(max_ts)
        except exc.InvalidGitRepositoryError:
            print(f"[GitConnector] No git repository found at {self.repo_path}")
        except Exception as e:
            print(f"[GitConnector] Error fetching git commits: {e}")
            
        return docs, new_state
