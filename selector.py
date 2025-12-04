"""File selector - ranks and selects relevant files based on instruction"""
from typing import List, Dict
import re
from config import Config
from logger import get_logger

logger = get_logger()

class FileSelector:
    """Selects most relevant files based on instruction keywords"""
    
    def __init__(self, config: Config):
        self.config = config
        self.max_files = config.MAX_FILES_TO_ANALYZE
    
    def select_files(self, files: List[Dict], instruction: str) -> List[Dict]:
        """
        Select most relevant files based on instruction
        
        Args:
            files: List of file metadata from scanner
            instruction: User instruction text
            
        Returns:
            Sorted list of most relevant files
        """
        logger.info(f"Selecting relevant files from {len(files)} candidates")
        
        # Extract keywords from instruction
        keywords = self._extract_keywords(instruction)
        logger.debug(f"Keywords: {keywords}")
        
        # Score each file
        scored_files = []
        for file_info in files:
            score = self._score_file(file_info, keywords, instruction)
            if score > 0:
                file_info['relevance_score'] = score
                scored_files.append(file_info)
        
        # Sort by score descending
        scored_files.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Take top N files
        selected = scored_files[:self.max_files]
        
        logger.success(f"Selected {len(selected)} relevant files")
        for f in selected[:5]:
            logger.debug(f"  - {f['path']} (score: {f['relevance_score']:.2f})")
        
        return selected
    
    def _extract_keywords(self, instruction: str) -> List[str]:
        """Extract meaningful keywords from instruction"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', instruction.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _score_file(self, file_info: Dict, keywords: List[str], instruction: str) -> float:
        """Calculate relevance score for a file"""
        score = 0.0
        file_path = file_info['path'].lower()
        file_name = file_info['name'].lower()
        
        # Exact filename match
        for keyword in keywords:
            if keyword in file_name:
                score += 10.0
            if keyword in file_path:
                score += 5.0
        
        # Extension-based scoring
        ext = file_info['extension']
        if ext in ['.py', '.js', '.ts', '.tsx', '.jsx']:
            score += 2.0
        
        # Penalize very large files
        if file_info['lines'] > 1000:
            score *= 0.8
        
        # Boost config/main files
        if any(name in file_name for name in ['config', 'main', 'index', 'app', 'core']):
            score += 3.0
        
        # Check for specific patterns in instruction
        if 'test' in instruction.lower() and 'test' in file_path:
            score += 8.0
        if 'component' in instruction.lower() and 'component' in file_path:
            score += 8.0
        if 'module' in instruction.lower() and 'module' in file_path:
            score += 8.0
        
        return score
