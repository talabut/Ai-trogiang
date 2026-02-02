from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class IRetriever(ABC):
    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Must return list of {content, score, metadata}
        and MUST enforce threshold.
        """
        raise NotImplementedError
