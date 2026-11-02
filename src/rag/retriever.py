"""
Hybrid RAG Retriever combining patient profile lookup with TF-IDF semantic vector similarity
over clinical care gap protocols, hospital scheduling policies, and clinic information.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from src.rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.doc_matrix = None
        self._build_index()

    def _build_index(self):
        """Indexes all documents currently in the knowledge base."""
        if not self.kb.documents:
            self.doc_matrix = None
            return

        corpus = [doc["title"] + " " + doc["content"] for doc in self.kb.documents]
        try:
            self.doc_matrix = self.vectorizer.fit_transform(corpus)
            logger.info(f"Retriever indexed {len(corpus)} documents into TF-IDF vector space.")
        except Exception as e:
            logger.error(f"Error vectorizing corpus: {e}")
            self.doc_matrix = None

    def refresh(self):
        """Re-indexes after knowledge base changes."""
        self.kb.reload()
        self._build_index()

    def retrieve(self, query: str, patient_id: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant documents for the query.
        Ensures the patient's own profile and matching care gap protocols are prioritized.
        """
        results: List[Dict[str, Any]] = []
        seen_ids = set()

        # 1. Direct Patient Profile Retrieval
        # Detect patient ID in query if not explicitly passed
        target_pid = patient_id
        if not target_pid:
            pid_match = re.search(r"\b(PAT-\d{4})\b", query, re.IGNORECASE)
            if pid_match:
                target_pid = pid_match.group(1).upper()

        if target_pid:
            for doc in self.kb.documents:
                if doc.get("patient_id", "").upper() == target_pid.upper():
                    results.append({
                        "doc_id": doc["id"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "content": doc["content"],
                        "score": 1.0
                    })
                    seen_ids.add(doc["id"])
                    break

        # 2. Semantic TF-IDF Vector Similarity Search
        if self.doc_matrix is not None and len(self.kb.documents) > 0:
            try:
                query_vec = self.vectorizer.transform([query])
                sim_scores = cosine_similarity(query_vec, self.doc_matrix)[0]

                # Get top indices sorted by similarity score
                top_indices = np.argsort(sim_scores)[::-1]

                for idx in top_indices:
                    if len(results) >= (top_k + (1 if target_pid else 0)):
                        break
                    doc = self.kb.documents[idx]
                    score = float(sim_scores[idx])

                    if doc["id"] not in seen_ids and score > 0.05:
                        results.append({
                            "doc_id": doc["id"],
                            "title": doc["title"],
                            "category": doc["category"],
                            "content": doc["content"],
                            "score": score
                        })
                        seen_ids.add(doc["id"])
            except Exception as e:
                logger.error(f"Error during semantic retrieval: {e}")

        # 3. Always include Emergency Policy if emergency keywords are present
        emergency_keywords = ["emergency", "chest pain", "shortness of breath", "severe", "dizzy", "stroke", "bleeding", "crisis"]
        if any(w in query.lower() for w in emergency_keywords):
            for doc in self.kb.documents:
                if doc.get("id") == "policy_emergency_triage" and doc["id"] not in seen_ids:
                    results.insert(0, {
                        "doc_id": doc["id"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "content": doc["content"],
                        "score": 0.99
                    })
                    seen_ids.add(doc["id"])
                    break

        return results[:top_k]
