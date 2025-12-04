"""Utility functions"""
import re
from typing import List, Dict

def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text"""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can'
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def count_tokens_estimate(text: str) -> int:
    """Rough token count estimate (1 token ≈ 4 chars)"""
    return len(text) // 4

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def validate_json_structure(data: Dict, required_keys: List[str]) -> bool:
    """Validate that dict has required keys"""
    return all(key in data for key in required_keys)

def safe_filename(filename: str) -> str:
    """Convert string to safe filename"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def parse_package_spec(spec: str) -> Dict[str, str]:
    """
    Parse package specification
    Examples:
        "pip:requests" -> {"manager": "pip", "package": "requests"}
        "npm:@types/node" -> {"manager": "npm", "package": "@types/node"}
    """
    if ':' not in spec:
        return {"manager": "unknown", "package": spec}
    
    manager, package = spec.split(':', 1)
    return {"manager": manager, "package": package}

def indent_code(code: str, spaces: int = 4) -> str:
    """Indent code block"""
    indent = ' ' * spaces
    lines = code.split('\n')
    return '\n'.join(indent + line for line in lines)

def dedent_code(code: str) -> str:
    """Remove common leading whitespace"""
    import textwrap
    return textwrap.dedent(code)
