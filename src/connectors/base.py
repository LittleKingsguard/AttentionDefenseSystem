from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from langchain_core.documents import Document

class BaseConnector(ABC):
    def __init__(self, connector_id: str, config: dict):
        self.id = connector_id
        self.config = config

    @property
    def connector_id(self) -> str:
        """Return a unique identifier for this connector used in the data_connectors table."""
        return self.id

    @abstractmethod
    def fetch_updates(self, last_sync_state: Optional[str]) -> Tuple[List[Document], Optional[str]]:
        """
        Fetch updates from the data source.
        Returns a tuple of (List of LangChain Documents, new_sync_state string).
        """
        pass
