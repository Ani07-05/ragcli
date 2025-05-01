import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re

from config import CHUNK_SIZE

class LogProcessor:
    """Specialized processor for log files"""
    
    @staticmethod
    def process_log_file(
        file_path: str,
        doc_id: str,
        output_dir: Path,
        chunk_strategy: str = "time_window",
        chunk_size: int = CHUNK_SIZE
    ) -> Dict[str, Any]:
        """
        Process a log file into chunks with metadata
        
        Args:
            file_path: Path to the log file
            doc_id: Document ID
            output_dir: Output directory for processed content
            chunk_strategy: Strategy for chunking logs ("time_window", "fixed_size", "log_level")
            chunk_size: Size of chunks (lines for fixed_size, minutes for time_window)
            
        Returns:
            Dict with processing metadata
        """
        # Create content directory
        content_dir = output_dir / "content"
        content_dir.mkdir(exist_ok=True)
        
        # Read the log file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_lines = f.readlines()
        
        # Extract metadata and chunk the logs
        if chunk_strategy == "time_window":
            chunks, chunk_metadata = LogProcessor._chunk_by_time_window(log_lines, chunk_size)
        elif chunk_strategy == "log_level":
            chunks, chunk_metadata = LogProcessor._chunk_by_log_level(log_lines)
        else:  # default to fixed_size
            chunks, chunk_metadata = LogProcessor._chunk_by_fixed_size(log_lines, chunk_size)
        
        # Save each chunk to a separate file
        chunk_files = []
        for i, (chunk, metadata) in enumerate(zip(chunks, chunk_metadata)):
            chunk_file = content_dir / f"chunk_{i+1}.log"
            with open(chunk_file, "w", encoding="utf-8") as f:
                f.write("".join(chunk))
            
            chunk_files.append({
                "chunk_num": i + 1,
                "file": f"chunk_{i+1}.log",
                "metadata": metadata
            })
        
        # Extract overall log metadata
        overall_metadata = LogProcessor._extract_overall_metadata(log_lines)
        
        # Return metadata
        return {
            "total_chunks": len(chunks),
            "chunk_strategy": chunk_strategy,
            "chunks": chunk_files,
            "total_lines": len(log_lines),
            "log_metadata": overall_metadata
        }
    
    @staticmethod
    def _extract_overall_metadata(log_lines: List[str]) -> Dict[str, Any]:
        """Extract overall metadata from log lines"""
        # Extract timestamp patterns
        timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})')
        level_pattern = re.compile(r'\[(INFO|DEBUG|WARNING|ERROR|CRITICAL)\]')
        
        first_timestamp = None
        last_timestamp = None
        log_levels = {}
        error_count = 0
        warning_count = 0
        unique_components = set()
        
        # Component pattern (very basic, would need to be adjusted for specific log formats)
        component_pattern = re.compile(r'\]\s*([A-Za-z0-9_-]+)[:.]')
        
        for line in log_lines:
            # Extract timestamp
            ts_match = timestamp_pattern.search(line)
            if ts_match:
                if not first_timestamp:
                    first_timestamp = ts_match.group(1)
                last_timestamp = ts_match.group(1)
            
            # Extract log level
            level_match = level_pattern.search(line)
            if level_match:
                level = level_match.group(1)
                log_levels[level] = log_levels.get(level, 0) + 1
                
                if level == "ERROR" or level == "CRITICAL":
                    error_count += 1
                elif level == "WARNING":
                    warning_count += 1
            
            # Extract component
            comp_match = component_pattern.search(line)
            if comp_match:
                unique_components.add(comp_match.group(1))
        
        # Calculate timespan if timestamps were found
        timespan = None
        if first_timestamp and last_timestamp:
            try:
                first_dt = datetime.strptime(first_timestamp, "%Y-%m-%d %H:%M:%S")
                last_dt = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
                timespan = (last_dt - first_dt).total_seconds() / 3600  # hours
            except ValueError:
                pass
        
        return {
            "first_timestamp": first_timestamp,
            "last_timestamp": last_timestamp,
            "timespan_hours": timespan,
            "log_level_counts": log_levels,
            "error_count": error_count,
            "warning_count": warning_count,
            "unique_components": list(unique_components)
        }
    
    @staticmethod
    def _chunk_by_fixed_size(log_lines: List[str], chunk_size: int) -> Tuple[List[List[str]], List[Dict]]:
        """Chunk logs by fixed number of lines"""
        chunks = []
        chunk_metadata = []
        
        for i in range(0, len(log_lines), chunk_size):
            chunk = log_lines[i:i+chunk_size]
            chunks.append(chunk)
            
            # Extract basic metadata from chunk
            metadata = {
                "start_line": i + 1,
                "end_line": min(i + chunk_size, len(log_lines)),
                "line_count": len(chunk),
                "log_levels": LogProcessor._extract_log_levels(chunk)
            }
            chunk_metadata.append(metadata)
        
        return chunks, chunk_metadata
    
    @staticmethod
    def _chunk_by_time_window(log_lines: List[str], window_minutes: int = 60) -> Tuple[List[List[str]], List[Dict]]:
        """Chunk logs by time windows"""
        # Regex for timestamp extraction (flexible pattern)
        timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})')
        
        chunks = []
        chunk_metadata = []
        current_chunk = []
        current_timestamp = None
        chunk_start_time = None
        
        for line in log_lines:
            # Extract timestamp from line
            match = timestamp_pattern.search(line)
            
            if match:
                try:
                    line_timestamp = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                    
                    # If this is the first line or we need a new chunk
                    if not current_timestamp:
                        chunk_start_time = line_timestamp
                        current_chunk = [line]
                        current_timestamp = line_timestamp
                    elif (line_timestamp - chunk_start_time).total_seconds() / 60 > window_minutes:
                        # New chunk if time window exceeded
                        chunks.append(current_chunk)
                        
                        # Extract metadata from chunk
                        metadata = {
                            "start_time": chunk_start_time.isoformat(),
                            "end_time": current_timestamp.isoformat(),
                            "line_count": len(current_chunk),
                            "log_levels": LogProcessor._extract_log_levels(current_chunk)
                        }
                        chunk_metadata.append(metadata)
                        
                        # Start new chunk
                        chunk_start_time = line_timestamp
                        current_chunk = [line]
                    else:
                        current_chunk.append(line)
                    
                    current_timestamp = line_timestamp
                except ValueError:
                    # If timestamp parsing fails, just add to current chunk
                    current_chunk.append(line)
            else:
                # If no timestamp, add to current chunk
                current_chunk.append(line)
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)
            metadata = {
                "start_time": chunk_start_time.isoformat() if chunk_start_time else None,
                "end_time": current_timestamp.isoformat() if current_timestamp else None,
                "line_count": len(current_chunk),
                "log_levels": LogProcessor._extract_log_levels(current_chunk)
            }
            chunk_metadata.append(metadata)
        
        return chunks, chunk_metadata
    
    @staticmethod
    def _chunk_by_log_level(log_lines: List[str]) -> Tuple[List[List[str]], List[Dict]]:
        """Chunk logs by log level"""
        # Define log levels in order of severity
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level_pattern = re.compile(r'\[(INFO|DEBUG|WARNING|ERROR|CRITICAL)\]')
        
        # Initialize chunks for each log level
        level_chunks = {level: [] for level in log_levels}
        unknown_chunk = []
        
        for line in log_lines:
            level_match = level_pattern.search(line)
            if level_match:
                level = level_match.group(1)
                level_chunks[level].append(line)
            else:
                unknown_chunk.append(line)
        
        # Create final chunks and metadata
        chunks = []
        chunk_metadata = []
        
        for level in log_levels:
            if level_chunks[level]:
                chunks.append(level_chunks[level])
                metadata = {
                    "log_level": level,
                    "line_count": len(level_chunks[level])
                }
                chunk_metadata.append(metadata)
        
        # Add unknown level chunk if not empty
        if unknown_chunk:
            chunks.append(unknown_chunk)
            metadata = {
                "log_level": "UNKNOWN",
                "line_count": len(unknown_chunk)
            }
            chunk_metadata.append(metadata)
        
        return chunks, chunk_metadata
    
    @staticmethod
    def _extract_log_levels(lines: List[str]) -> Dict[str, int]:
        """Extract log levels and their counts from lines"""
        level_pattern = re.compile(r'\[(INFO|DEBUG|WARNING|ERROR|CRITICAL)\]')
        counts = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
        
        for line in lines:
            match = level_pattern.search(line)
            if match:
                level = match.group(1)
                counts[level] += 1
        
        return counts