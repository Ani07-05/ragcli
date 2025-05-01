import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class DocumentGrader:
    """
    Provides document grading functionality to improve retrieval quality
    """
    
    @staticmethod
    def grade_retrieved_documents(
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        doc_type: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Grade and rerank retrieved documents based on relevance to query
        
        Args:
            query: The user's query
            retrieved_docs: List of retrieved documents with scores
            doc_type: Type of document ('log', 'pdf', etc.)
            
        Returns:
            Reranked list of documents with updated scores
        """
        if not retrieved_docs:
            return []
        
        # Select appropriate grading method based on document type
        if doc_type == "log":
            return DocumentGrader._grade_log_documents(query, retrieved_docs)
        else:
            return DocumentGrader._grade_standard_documents(query, retrieved_docs)
    
    @staticmethod
    def _grade_standard_documents(
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Grade standard documents"""
        
        # Extract query keywords (remove common words)
        query_keywords = DocumentGrader._extract_keywords(query)
        
        for doc in retrieved_docs:
            # Start with base vector similarity score
            base_score = doc.get("score", 0.0)
            
            # Get document text
            text = doc.get("text", "")
            
            # 1. Keyword presence boost
            keyword_matches = sum(1 for keyword in query_keywords if keyword.lower() in text.lower())
            keyword_score = min(keyword_matches / max(len(query_keywords), 1), 1.0) * 0.3
            
            # 2. Text length penalty (too short or too long)
            length = len(text)
            length_score = 0.0
            if 100 <= length <= 2000:
                length_score = 0.1  # Ideal length
            elif length < 100:
                length_score = 0.05  # Too short
            else:
                length_score = 0.05  # Too long
            
            # 3. Document structure bonus (organized with headers, lists, etc.)
            structure_score = 0.0
            if re.search(r'#+\s+\w+', text):  # Has headers
                structure_score += 0.05
            if re.search(r'[-*]\s+\w+', text):  # Has bullet points
                structure_score += 0.05
            
            # Calculate final score (base + boosts)
            # Keep vector similarity as 50% of the score
            final_score = (base_score * 0.5) + keyword_score + length_score + structure_score
            
            # Update document score
            doc["score"] = min(final_score, 1.0)  # Cap at 1.0
            
            # Add grading explanation
            doc["grading"] = {
                "base_score": base_score,
                "keyword_score": keyword_score,
                "length_score": length_score,
                "structure_score": structure_score,
                "final_score": doc["score"]
            }
        
        # Sort by score in descending order
        return sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)
    
    @staticmethod
    def _grade_log_documents(
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Grade log documents with specialized log scoring"""
        
        # Extract query keywords
        query_keywords = DocumentGrader._extract_keywords(query)
        
        # Look for log-specific terms in query
        error_terms = ["error", "fail", "exception", "critical"]
        warning_terms = ["warning", "alert", "attention"]
        time_terms = ["time", "period", "duration", "from", "between", "when"]
        
        has_error_focus = any(term in query.lower() for term in error_terms)
        has_warning_focus = any(term in query.lower() for term in warning_terms)
        has_time_focus = any(term in query.lower() for term in time_terms)
        
        for doc in retrieved_docs:
            # Start with base vector similarity score
            base_score = doc.get("score", 0.0)
            
            # Get document text
            text = doc.lower()
            
            # 1. Keyword presence boost
            keyword_matches = sum(1 for keyword in query_keywords if keyword.lower() in text)
            keyword_score = min(keyword_matches / max(len(query_keywords), 1), 1.0) * 0.3
            
            # 2. Log-specific relevance
            log_relevance = 0.0
            
            # If query focuses on errors, boost chunks with errors
            if has_error_focus and any(term in text for term in error_terms):
                log_relevance += 0.15
            
            # If query focuses on warnings, boost chunks with warnings
            if has_warning_focus and any(term in text for term in warning_terms):
                log_relevance += 0.1
            
            # If query is about time periods, boost chunks with timestamps
            if has_time_focus and re.search(r'\d{4}-\d{2}-\d{2}', text):
                log_relevance += 0.1
            
            # 3. Timestamp relevance for logs
            timestamp_score = 0.0
            if re.search(r'\d{4}-\d{2}-\d{2}', text):
                timestamp_score = 0.1
            
            # Calculate final score
            final_score = (base_score * 0.5) + keyword_score + log_relevance + timestamp_score
            
            # Update document score
            doc["score"] = min(final_score, 1.0)  # Cap at 1.0
            
            # Add grading explanation
            doc["grading"] = {
                "base_score": base_score,
                "keyword_score": keyword_score,
                "log_relevance": log_relevance,
                "timestamp_score": timestamp_score,
                "final_score": doc["score"]
            }
        
        # Sort by score in descending order
        return sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text by removing common words"""
        # List of common words to filter out
        common_words = set([
            "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
            "in", "on", "at", "to", "for", "with", "by", "about", "like",
            "through", "over", "before", "between", "after", "since", "without",
            "under", "i", "you", "he", "she", "it", "we", "they", "this", 
            "that", "these", "those", "do", "does", "did", "have", "has", "had",
            "my", "your", "his", "her", "its", "our", "their"
        ])
        
        # Tokenize and filter
        words = text.split()
        keywords = [word.strip(".,;:!?()[]{}\"'").lower() for word in words
                   if word.strip(".,;:!?()[]{}\"'").lower() not in common_words
                   and len(word) > 2]
        
        return keywords
    
    @staticmethod
    def calculate_answer_confidence(
        query: str,
        answer: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence score for generated answer
        
        Args:
            query: User query
            answer: Generated answer
            retrieved_docs: Retrieved documents used for generation
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not retrieved_docs or not answer:
            return 0.0
        
        # 1. Document support - Do we have high-scoring documents?
        doc_scores = [doc.get("score", 0.0) for doc in retrieved_docs]
        avg_doc_score = sum(doc_scores) / len(doc_scores) if doc_scores else 0
        
        # 2. Content verification - Does answer content appear in sources?
        answer_keywords = DocumentGrader._extract_keywords(answer)
        if not answer_keywords:
            return 0.3  # Very low confidence if no keywords
        
        # Check if answer keywords appear in documents
        docs_text = " ".join([doc.get("text", "") for doc in retrieved_docs]).lower()
        keyword_matches = sum(1 for keyword in answer_keywords if keyword.lower() in docs_text)
        keyword_ratio = keyword_matches / len(answer_keywords)
        
        # 3. Answer quality factors
        quality_score = 0.0
        
        # Answer length (too short answers are less confident)
        if len(answer) < 50:
            quality_score = 0.3
        elif 50 <= len(answer) < 200:
            quality_score = 0.7
        else:
            quality_score = 1.0
        
        # Calculate final confidence
        confidence = (avg_doc_score * 0.4) + (keyword_ratio * 0.4) + (quality_score * 0.2)
        
        return min(confidence, 1.0)  # Cap at 1.0

# Example usage
if __name__ == "__main__":
    # Test with sample documents and query
    sample_docs = [
        {"text": "Windows error log shows critical system failures", "score": 0.8},
        {"text": "Application started normally with no errors", "score": 0.6},
        {"text": "The system encountered network connectivity issues", "score": 0.7}
    ]
    
    sample_query = "Are there any critical errors in the logs?"
    
    # Grade the documents
    graded_docs = DocumentGrader.grade_retrieved_documents(sample_query, sample_docs, "log")
    
    # Print results
    for i, doc in enumerate(graded_docs):
        print(f"Document {i+1}: Score {doc['score']:.4f}")
        print(f"Text: {doc['text']}")
        print(f"Grading: {doc['grading']}")
        print()