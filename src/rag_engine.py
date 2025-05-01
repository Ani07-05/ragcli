from typing import List, Dict, Any, Optional
from vector_store_manager_local import VectorStoreManager
from llama3_client import Llama3Client
from document_grader import DocumentGrader

class RAGEngine:
    """Retrieval-Augmented Generation engine using Llama 3 with specialized prompting"""
    
    def __init__(self, temperature: float = 0.7):
        self.vector_store = VectorStoreManager()
        self.llm = Llama3Client()
        self.temperature = temperature
        self.document_grader = DocumentGrader()
    
    def query(self, 
             repo_key: str, 
             query_text: str, 
             top_k: int = 5,
             use_grading: bool = True) -> Dict[str, Any]:
        """
        Query a repository using RAG
        
        Args:
            repo_key: Repository key to query
            query_text: Query text
            top_k: Number of top documents to retrieve
            use_grading: Whether to use document grading
            
        Returns:
            Dict with answer and sources
        """
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.search_repository(
            repo_key=repo_key,
            query=query_text,
            top_k=top_k * 2 if use_grading else top_k  # Retrieve more docs if using grading
        )
        
        # Step 2: Apply document grading if enabled
        if use_grading and retrieved_docs:
            # Determine document type
            doc_type = "standard"
            if retrieved_docs and "metadata" in retrieved_docs[0]:
                doc_type = retrieved_docs[0]["metadata"].get("document_type", "standard")
            
            # Grade and rerank documents
            retrieved_docs = self.document_grader.grade_retrieved_documents(
                query_text, retrieved_docs, doc_type
            )
            
            # Take top k after grading
            retrieved_docs = retrieved_docs[:top_k]
        
        # Step 3: Generate response based on retrieved documents
        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant information in the repository to answer your question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Extract text from retrieved documents
        context_chunks = [doc["text"] for doc in retrieved_docs]
        
        # Determine document type to use specialized prompting
        doc_type = "standard"
        if retrieved_docs and "metadata" in retrieved_docs[0]:
            doc_type = retrieved_docs[0]["metadata"].get("document_type", "standard")
        
        # Step 4: Generate answer using appropriate template based on document type
        if doc_type == "log":
            answer = self._generate_log_answer(query_text, context_chunks, retrieved_docs)
        else:
            answer = self._generate_standard_answer(query_text, context_chunks, retrieved_docs)
        
        # Step 5: Calculate answer confidence
        confidence = self.document_grader.calculate_answer_confidence(
            query_text, answer, retrieved_docs
        )
        
        # Step 6: Format sources for attribution
        sources = []
        for doc in retrieved_docs:
            source_info = {
                "text": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                "metadata": doc["metadata"] if "metadata" in doc else {},
                "score": doc["score"] if "score" in doc else 0.0,
                "grading": doc.get("grading", {})
            }
            sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
    
    def _generate_log_answer(self, 
                           query: str, 
                           context_chunks: List[str],
                           retrieved_docs: List[Dict[str, Any]]) -> str:
        """Generate answers specifically for log queries"""
        
        # Create a specialized system prompt for log analysis
        system_prompt = """You are a specialized log analysis assistant. When analyzing logs:
1. Focus on patterns, timestamps, sequences of events, and error messages
2. For timestamps, note the time periods and duration of events
3. For errors or warnings, summarize their frequency and severity
4. Look for correlations between events
5. Present information in a clear, structured way with headings
6. Be precise with technical details from the logs
7. Use bullet points and lists when appropriate to organize information
8. If analyzing system logs, look for critical failures, errors, and security concerns
9. For application logs, focus on exceptions, failed operations, and performance issues
10. Include specific log entries as examples when relevant

Only use information contained in the provided log context. If you cannot find relevant information,
clearly state that fact rather than speculating."""
        
        # Create a specialized prompt that includes log-specific guidance
        log_prompt = f"""I need you to analyze these log entries to answer: "{query}"

Log context:
{"".join([f"--- Log Chunk {i+1} ---\n{chunk}\n\n" for i, chunk in enumerate(context_chunks)])}

Based solely on the log entries above, provide a detailed analysis that answers the query.
Structure your answer with appropriate headings like:
1. "Analysis Summary" - A brief overview of your findings
2. "Key Observations" - The most important patterns or events you've identified
3. "Patterns and Trends" - Any recurring issues or notable sequences of events
4. "Insights and Recommendations" - What these logs tell us and what actions might be needed

If you see timestamps, note the time period covered. If you see errors, describe their frequency and severity.
When possible, include specific examples from the logs to support your analysis.
"""
        
        # Generate the answer with the specialized system prompt and log prompt
        return self.llm.generate(
            prompt=log_prompt,
            system_prompt=system_prompt,
            temperature=self.temperature
        )
    
    def _generate_standard_answer(self,
                                query: str,
                                context_chunks: List[str],
                                retrieved_docs: List[Dict[str, Any]]) -> str:
        """Generate answers for standard documents (PDFs, text, etc.)"""
        
        # Create a specialized system prompt for document analysis
        system_prompt = """You are a document analysis assistant specialized in extracting and synthesizing information from various documents. When answering questions about documents:
1. Provide concise, accurate answers based solely on the provided context
2. Maintain the factual accuracy of the original documents
3. Organize your response in a logical, structured manner
4. Use appropriate headings and formatting for clarity
5. Focus on the specific information requested in the query
6. Synthesize information from multiple sources when relevant
7. If technical content is present, maintain the technical accuracy
8. If the documents contain contradictory information, acknowledge the differences
9. For research documents, focus on methodology, findings, and conclusions
10. For technical manuals or guides, emphasize procedures and specifications

Only use information contained in the provided context. If you cannot find relevant information,
clearly state this limitation rather than making assumptions."""
        
        # Create specialized prompt for document analysis
        doc_prompt = f"""I need you to analyze these document excerpts to answer: "{query}"

Document context:
{"".join([f"--- Document Excerpt {i+1} ---\n{chunk}\n\n" for i, chunk in enumerate(context_chunks)])}

Based solely on the document excerpts above, provide a comprehensive answer to the query.
Focus on extracting and synthesizing the most relevant information from the provided context.
Structure your response in a clear, organized manner with appropriate sections and formatting.
If the documents contain tables, charts, or structured data, describe their content clearly.
If the query requests specific facts, figures, or technical details, provide them accurately.

If the documents don't contain information relevant to the query, clearly state this limitation.
"""
        
        # Generate the answer with the specialized system prompt and document prompt
        return self.llm.generate(
            prompt=doc_prompt,
            system_prompt=system_prompt,
            temperature=self.temperature
        )
    
    def detect_hallucination(self, 
                           query_text: str, 
                           answer: str, 
                           context_chunks: List[str]) -> bool:
        """
        Basic hallucination detection
        
        Args:
            query_text: Original query
            answer: Generated answer
            context_chunks: Context used to generate the answer
            
        Returns:
            Boolean indicating if hallucination is detected
        """
        # Use confidence scoring from document grader as a proxy
        confidence = self.document_grader.calculate_answer_confidence(
            query_text, answer, 
            [{"text": chunk, "score": 1.0} for chunk in context_chunks]
        )
        
        # Consider low confidence as potential hallucination
        return confidence < 0.5