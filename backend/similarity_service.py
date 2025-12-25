"""
Cosine Similarity Service for Comment Moderation
=================================================
Uses TF-IDF vectorization for lightweight, fast similarity computation.
No external API calls - runs entirely locally.

Purpose:
1. Promise relevance: Check if comment relates to manifesto promises
2. Spam detection: Detect copy-paste and repeated content
3. Flagging: Auto-flag off-topic or spam-like comments

Thresholds (configurable):
- similarity < 25  → auto_flagged (off_topic)
- 25 – 40          → active (but marked "low relevance")
- > 40             → active (relevant)
- spam_sim > 92    → quarantined (spam_like)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple, Optional, Dict
import re


class SimilarityService:
    """
    Lightweight cosine similarity service using TF-IDF.
    No external dependencies - uses scikit-learn.
    """
    
    # Thresholds (0-100 scale)
    RELEVANCE_LOW = 25       # Below this = off_topic
    RELEVANCE_MEDIUM = 40    # Below this = low_relevance
    SPAM_THRESHOLD = 92      # Above this = spam_like
    
    def __init__(self):
        # Use simpler vectorizer that works better with short texts
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,  # Keep all words for short text
            ngram_range=(1, 3),  # Include trigrams for better matching
            min_df=1,
            max_df=1.0,  # Don't filter common words in small corpus
            analyzer='word',
            token_pattern=r'\b\w+\b'  # Match word boundaries
        )
        self._is_fitted = False
    
    def _preprocess(self, text: str) -> str:
        """Clean and normalize text for comparison."""
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    
    def _word_overlap_score(self, text1: str, text2: str) -> float:
        """Simple word overlap for very short texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)  # Jaccard similarity
    
    def compute_similarity(self, text1: str, text2: str) -> int:
        """
        Compute cosine similarity between two texts.
        Returns: Integer 0-100 (percentage)
        """
        text1 = self._preprocess(text1)
        text2 = self._preprocess(text2)
        
        if not text1 or not text2:
            return 0
        
        try:
            # For very short texts, use word overlap as fallback
            words1 = text1.split()
            words2 = text2.split()
            
            if len(words1) < 3 or len(words2) < 3:
                # Use Jaccard similarity for very short texts
                jaccard = self._word_overlap_score(text1, text2)
                return int(jaccard * 100)
            
            # Fit and transform on both texts
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return int(similarity * 100)
        except Exception as e:
            print(f"Similarity computation error: {e}")
            return 0
    
    def compute_max_similarity(self, comment: str, documents: List[str]) -> Tuple[int, int]:
        """
        Compute max similarity between comment and a list of documents.
        Returns: (max_similarity_score, index_of_best_match)
        """
        comment = self._preprocess(comment)
        
        if not comment or not documents:
            return (0, -1)
        
        processed_docs = [self._preprocess(doc) for doc in documents]
        # Filter out empty docs
        valid_docs = [(i, doc) for i, doc in enumerate(processed_docs) if doc]
        
        if not valid_docs:
            return (0, -1)
        
        try:
            all_texts = [comment] + [doc for _, doc in valid_docs]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Compute similarity between comment (index 0) and all documents
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            max_idx = int(np.argmax(similarities))
            max_score = int(similarities[max_idx] * 100)
            original_idx = valid_docs[max_idx][0]
            
            return (max_score, original_idx)
        except Exception as e:
            print(f"Max similarity computation error: {e}")
            return (0, -1)
    
    def check_promise_relevance(
        self, 
        comment: str, 
        manifesto_title: str,
        manifesto_description: str,
        promises: List[Dict] = None
    ) -> Dict:
        """
        Check if comment is relevant to the manifesto and its promises.
        
        Returns: {
            'similarity_score': int (0-100),
            'matched_promise_id': int or None,
            'is_relevant': bool,
            'flag_reason': str or None ('off_topic', 'low_relevance', None)
        }
        """
        # Build list of texts to compare against
        comparison_texts = []
        text_ids = []
        
        # Add manifesto title and description
        combined_manifesto = f"{manifesto_title} {manifesto_description}"
        comparison_texts.append(combined_manifesto)
        text_ids.append(('manifesto', None))
        
        # Add individual promises if provided
        if promises:
            for p in promises:
                promise_text = f"{p.get('title', '')} {p.get('description', '')}"
                comparison_texts.append(promise_text)
                text_ids.append(('promise', p.get('id')))
        
        max_score, best_idx = self.compute_max_similarity(comment, comparison_texts)
        
        # Determine relevance and flag reason
        flag_reason = None
        if max_score < self.RELEVANCE_LOW:
            flag_reason = 'off_topic'
        elif max_score < self.RELEVANCE_MEDIUM:
            flag_reason = 'low_relevance'
        
        matched_promise_id = None
        if best_idx >= 0 and text_ids[best_idx][0] == 'promise':
            matched_promise_id = text_ids[best_idx][1]
        
        return {
            'similarity_score': max_score,
            'matched_promise_id': matched_promise_id,
            'is_relevant': max_score >= self.RELEVANCE_LOW,
            'flag_reason': flag_reason
        }
    
    def check_spam_similarity(
        self, 
        comment: str, 
        recent_comments: List[str],
        same_author_comments: List[str] = None
    ) -> Dict:
        """
        Check if comment is similar to recent comments (spam detection).
        
        Returns: {
            'spam_score': int (0-100),
            'is_spam': bool,
            'matched_comment_idx': int or None
        }
        """
        all_comments = list(recent_comments)
        
        # Also check same author's recent comments
        if same_author_comments:
            all_comments.extend(same_author_comments)
        
        if not all_comments:
            return {
                'spam_score': 0,
                'is_spam': False,
                'matched_comment_idx': None
            }
        
        max_score, best_idx = self.compute_max_similarity(comment, all_comments)
        
        return {
            'spam_score': max_score,
            'is_spam': max_score >= self.SPAM_THRESHOLD,
            'matched_comment_idx': best_idx if max_score >= self.SPAM_THRESHOLD else None
        }
    
    def analyze_comment(
        self,
        comment: str,
        manifesto_title: str,
        manifesto_description: str,
        recent_comments: List[str] = None,
        same_author_comments: List[str] = None,
        promises: List[Dict] = None
    ) -> Dict:
        """
        Full analysis of a comment for moderation.
        
        Returns: {
            'state': str ('active', 'auto_flagged', 'quarantined'),
            'auto_flag_reason': str or None,
            'similarity_score': int,
            'matched_promise_id': int or None,
            'spam_similarity_score': int,
            'details': {...}
        }
        """
        # Check promise relevance
        relevance = self.check_promise_relevance(
            comment, 
            manifesto_title, 
            manifesto_description,
            promises
        )
        
        # Check spam similarity
        spam = self.check_spam_similarity(
            comment,
            recent_comments or [],
            same_author_comments
        )
        
        # Determine final state
        state = 'active'
        auto_flag_reason = None
        
        # Spam takes priority
        if spam['is_spam']:
            state = 'quarantined'
            auto_flag_reason = 'spam_like'
        elif relevance['flag_reason'] == 'off_topic':
            state = 'auto_flagged'
            auto_flag_reason = 'off_topic'
        elif relevance['flag_reason'] == 'low_relevance':
            # Don't flag, but mark as low relevance
            state = 'active'
            auto_flag_reason = 'low_relevance'
        
        return {
            'state': state,
            'auto_flag_reason': auto_flag_reason,
            'similarity_score': relevance['similarity_score'],
            'matched_promise_id': relevance['matched_promise_id'],
            'spam_similarity_score': spam['spam_score'],
            'details': {
                'relevance': relevance,
                'spam': spam
            }
        }


# Singleton instance
_similarity_service = None

def get_similarity_service() -> SimilarityService:
    """Get singleton instance of SimilarityService."""
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = SimilarityService()
    return _similarity_service
