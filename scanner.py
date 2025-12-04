"""Project scanner - recursively scans and indexes project files"""
from pathlib import Path
from typing import List, Dict, Set
from config import Config
from logger import get_logger

logger = get_logger()

class ProjectScanner:
    """Scans project directory and builds file index"""
    
    def __init__(self, config: Config):
        self.config = config
        self.ignore_dirs = set(config.IGNORE_DIRS)
        self.supported_extensions = set(config.SUPPORTED_EXTENSIONS)
    
    def scan(self, root_path: str) -> List[Dict[str, any]]:
        """
        Scan project directory and return list of file metadata
        
        Returns:
            List of dicts with keys: path, extension, size, lines
        """
        logger.info(f"Scanning project: {root_path}")
        root = Path(root_path).resolve()
        
        if not root.exists():
            logger.error(f"Path does not exist: {root_path}")
            return []
        
        files = []
        scanned_count = 0
        
        for file_path in self._walk_directory(root):
            try:
                relative_path = file_path.relative_to(root)
                
                # Count lines
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = sum(1 for _ in f)
                
                files.append({
                    'path': str(relative_path),
                    'absolute_path': str(file_path),
                    'extension': file_path.suffix,
                    'size': file_path.stat().st_size,
                    'lines': lines,
                    'name': file_path.name
                })
                scanned_count += 1
                
            except Exception as e:
                logger.debug(f"Error scanning {file_path}: {e}")
                continue
        
        logger.success(f"Scanned {scanned_count} files")
        return files
    
    def _walk_directory(self, root: Path) -> List[Path]:
        """Recursively walk directory, respecting ignore rules"""
        result = []
        
        try:
            for item in root.iterdir():
                # Skip ignored directories
                if item.is_dir():
                    if item.name in self.ignore_dirs or item.name.startswith('.'):
                        continue
                    result.extend(self._walk_directory(item))
                
                # Process files with supported extensions
                elif item.is_file():
                    if item.suffix in self.supported_extensions:
                        result.append(item)
        
        except PermissionError:
            logger.debug(f"Permission denied: {root}")
        
        return result
    
    def get_file_content(self, file_path: str) -> str:
        """Read and return file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return ""
    
    def get_file_lines(self, file_path: str) -> List[str]:
        """Read and return file lines"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.readlines()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []
