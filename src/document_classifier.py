import os
import re
from pathlib import Path
from typing import Dict, Any, Tuple

class DocumentClassifier:
    """Classifies documents by type for specialized processing"""
    
    @staticmethod
    def classify_document(file_path: str) -> Dict[str, Any]:
        """
        Classify a document by analyzing its content and extension
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dict with classification information
        """
        file_name = os.path.basename(file_path)
        _, extension = os.path.splitext(file_name)
        extension = extension.lower()
        
        # Check file extension first
        if extension in ['.log']:
            doc_type = "log"
        elif extension in ['.pdf']:
            doc_type = "pdf"
        elif extension in ['.txt', '.md', '.rst']:
            # For text files, we need to check if it's a log file
            doc_type = DocumentClassifier._analyze_text_content(file_path)
        else:
            # Default to standard document type
            doc_type = "document"
        
        return {
            "type": doc_type,
            "extension": extension,
            "specifics": DocumentClassifier._get_specifics(file_path, doc_type)
        }
    
    @staticmethod
    def _analyze_text_content(file_path: str, sample_lines: int = 20) -> str:
        """
        Analyze text content to determine if it's a log file
        
        Args:
            file_path: Path to the text file
            sample_lines: Number of lines to sample
            
        Returns:
            Document type ("log" or "document")
        """
        try:
            log_patterns = [
                # Common timestamp patterns
                r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # 2023-05-01 14:30:45
                r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',    # 2023-05-01T14:30:45
                r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', # [2023-05-01 14:30:45]
                r'^\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}',   # 01/05/2023 14:30:45
                r'^\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2}',   # 01-05-2023 14:30:45
                
                # Common log level patterns
                r'\s+INFO\s+',
                r'\s+DEBUG\s+',
                r'\s+WARNING\s+',
                r'\s+ERROR\s+',
                r'\s+CRITICAL\s+',
                r'\[INFO\]',
                r'\[DEBUG\]',
                r'\[WARNING\]',
                r'\[ERROR\]',
                r'\[CRITICAL\]',
                
                # Windows event log patterns
                r'^Event\[\d+\]:',
                r'^Log:',
                r'^Source:',
                r'^Type:'
            ]
            
            # Compile patterns
            patterns = [re.compile(pattern) for pattern in log_patterns]
            
            # Count matching lines
            match_count = 0
            total_lines = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= sample_lines:
                        break
                    
                    total_lines += 1
                    if any(pattern.search(line) for pattern in patterns):
                        match_count += 1
            
            # If more than 40% of sampled lines match log patterns, classify as log
            if total_lines > 0 and (match_count / total_lines) > 0.4:
                return "log"
            
            return "document"
            
        except Exception as e:
            print(f"Error analyzing text content: {e}")
            return "document"
    
    @staticmethod
    def _get_specifics(file_path: str, doc_type: str) -> Dict[str, Any]:
        """
        Get specific metadata for the document type
        
        Args:
            file_path: Path to the document file
            doc_type: Document type
            
        Returns:
            Dict with specific metadata
        """
        if doc_type == "log":
            return DocumentClassifier._analyze_log_specifics(file_path)
        elif doc_type == "pdf":
            # Could expand with PDF-specific analysis
            return {}
        else:
            return {}
    
    @staticmethod
    def _analyze_log_specifics(file_path: str, sample_lines: int = 100) -> Dict[str, Any]:
        """
        Analyze log file to extract specific metadata
        
        Args:
            file_path: Path to the log file
            sample_lines: Number of lines to sample
            
        Returns:
            Dict with log-specific metadata
        """
        try:
            log_levels = set()
            first_timestamp = None
            last_timestamp = None
            
            # Try multiple timestamp formats
            timestamp_patterns = [
                # Common formats
                (re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'), "%Y-%m-%d %H:%M:%S"),
                (re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'), "%Y-%m-%dT%H:%M:%S"),
                (re.compile(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})'), "%m/%d/%Y %H:%M:%S"),
                (re.compile(r'(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})'), "%d-%m-%Y %H:%M:%S")
            ]
            
            # Log level patterns
            level_patterns = [
                re.compile(r'\[(INFO|DEBUG|WARNING|ERROR|CRITICAL)\]'),
                re.compile(r'\s+(INFO|DEBUG|WARNING|ERROR|CRITICAL)\s+')
            ]
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i < sample_lines:
                        lines.append(line)
                    else:
                        # Still read the file to get the last timestamp
                        last_line = line
                
                # Check first lines for timestamp and log level
                for line in lines:
                    # Extract timestamp
                    for pattern, format_str in timestamp_patterns:
                        match = pattern.search(line)
                        if match and not first_timestamp:
                            first_timestamp = match.group(1)
                            break
                    
                    # Extract log level
                    for pattern in level_patterns:
                        match = pattern.search(line)
                        if match:
                            log_levels.add(match.group(1))
                            break
                
                # Try to get the last timestamp from the last line
                if 'last_line' in locals():
                    for pattern, format_str in timestamp_patterns:
                        match = pattern.search(last_line)
                        if match:
                            last_timestamp = match.group(1)
                            break
            
            # Estimate log type based on patterns
            log_type = "unknown"
            if any("Microsoft" in line or "Windows" in line for line in lines[:10]):
                log_type = "windows"
            elif any("apache" in line.lower() for line in lines[:10]):
                log_type = "apache"
            elif any("nginx" in line.lower() for line in lines[:10]):
                log_type = "nginx"
            elif any("exception" in line.lower() or "stacktrace" in line.lower() for line in lines):
                log_type = "application"
            
            return {
                "log_levels": list(log_levels),
                "first_timestamp": first_timestamp,
                "last_timestamp": last_timestamp,
                "log_type": log_type
            }
            
        except Exception as e:
            print(f"Error analyzing log specifics: {e}")
            return {}

# Test the classifier
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_classifier.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = DocumentClassifier.classify_document(file_path)
    
    print(f"Classification result for {file_path}:")
    print(f"Type: {result['type']}")
    print(f"Extension: {result['extension']}")
    print(f"Specifics: {result['specifics']}")