"""Snippet extractor - extracts relevant code sections to avoid token overflow"""
from typing import List, Dict, Tuple
from config import Config
from logger import get_logger

logger = get_logger()

class SnippetExtractor:
    """Extracts relevant code snippets from files"""
    
    def __init__(self, config: Config):
        self.config = config
        self.context_lines = config.SNIPPET_CONTEXT_LINES
    
    def extract_snippets(self, file_path: str, file_lines: List[str], 
                        keywords: List[str]) -> Dict:
        """
        Extract relevant snippets from file
        
        Args:
            file_path: Path to file
            file_lines: List of file lines
            keywords: Keywords to search for
            
        Returns:
            Dict with snippets and metadata
        """
        total_lines = len(file_lines)
        
        # If file is small, return entire file
        if total_lines <= self.context_lines * 2:
            return {
                'file_path': file_path,
                'full_file': True,
                'content': ''.join(file_lines),
                'line_start': 1,
                'line_end': total_lines,
                'total_lines': total_lines
            }
        
        # Find relevant line numbers
        relevant_lines = self._find_relevant_lines(file_lines, keywords)
        
        if not relevant_lines:
            # No matches, return top of file
            snippet_lines = file_lines[:self.context_lines]
            return {
                'file_path': file_path,
                'full_file': False,
                'content': ''.join(snippet_lines),
                'line_start': 1,
                'line_end': len(snippet_lines),
                'total_lines': total_lines
            }
        
        # Extract snippet around relevant lines
        center_line = relevant_lines[len(relevant_lines) // 2]
        start_line = max(0, center_line - self.context_lines // 2)
        end_line = min(total_lines, center_line + self.context_lines // 2)
        
        snippet_lines = file_lines[start_line:end_line]
        
        return {
            'file_path': file_path,
            'full_file': False,
            'content': ''.join(snippet_lines),
            'line_start': start_line + 1,
            'line_end': end_line,
            'total_lines': total_lines,
            'relevant_lines': relevant_lines
        }
    
    def _find_relevant_lines(self, lines: List[str], keywords: List[str]) -> List[int]:
        """Find line numbers containing keywords"""
        relevant = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    relevant.append(i)
                    break
        
        return relevant
    
    def format_snippet(self, snippet: Dict) -> str:
        """Format snippet for LLM consumption"""
        if snippet['full_file']:
            header = f"=== {snippet['file_path']} (FULL FILE) ===\n"
        else:
            header = (f"=== {snippet['file_path']} "
                     f"(Lines {snippet['line_start']}-{snippet['line_end']} "
                     f"of {snippet['total_lines']}) ===\n")
        
        # Add line numbers
        lines = snippet['content'].split('\n')
        numbered_lines = []
        for i, line in enumerate(lines):
            line_num = snippet['line_start'] + i
            numbered_lines.append(f"{line_num:4d} | {line}")
        
        return header + '\n'.join(numbered_lines) + "\n\n"
