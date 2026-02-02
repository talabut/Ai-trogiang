import logging
from typing import Dict, Any

from backend.core.interfaces import IRetrievalService, IAgent

logger = logging.getLogger(__name__)

MIN_EVIDENCE_COUNT = 1


class QAAgent(IAgent):
    def __init__(self, retrieval_service: IRetrievalService):
        self.retrieval_service = retrieval_service

    def answer(self, query: str, course_id: str) -> Dict[str, Any]:
        try:
            result = self.retrieval_service.retrieve(query, course_id)
        except Exception as e:
            logger.error(f"RETRIEVAL_ERROR | {str(e)}")
            return self._refuse("RETRIEVAL_ERROR")

        evidence = result if isinstance(result, list) else result.get("evidence", [])

        if not evidence:
            return self._refuse("NO_EVIDENCE")

        if len(evidence) < MIN_EVIDENCE_COUNT:
            return self._refuse("HALLUCINATION_CHECK_FAILED")

        return {
            "answer": None,
            "refusal": False,
            "evidence": evidence,
        }

    def _refuse(self, reason: str) -> Dict[str, Any]:
        logger.info(f"AGENT_REFUSAL | reason={reason}")
        return {
            "answer": None,
            "refusal": True,
            "reason": reason,
            "evidence": [],
        }
