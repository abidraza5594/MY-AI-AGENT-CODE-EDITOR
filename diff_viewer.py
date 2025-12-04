"""Diff viewer - displays code changes"""
from typing import List, Tuple
import difflib

class DiffViewer:
    """Displays diffs in a readable format"""
    
    @staticmethod
    def generate_unified_diff(old_content: str, new_content: str, 
                             file_path: str) -> str:
        """Generate unified diff format"""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        )
        
        return ''.join(diff)
    
    @staticmethod
    def generate_side_by_side(old_content: str, new_content: str,
                             context_lines: int = 3) -> str:
        """Generate side-by-side diff"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        diff = difflib.Differ()
        result = list(diff.compare(old_lines, new_lines))
        
        output = []
        output.append("=" * 80)
        output.append("SIDE-BY-SIDE DIFF")
        output.append("=" * 80)
        
        for line in result:
            if line.startswith('- '):
                output.append(f"OLD: {line[2:]}")
            elif line.startswith('+ '):
                output.append(f"NEW: {line[2:]}")
            elif line.startswith('? '):
                continue
            else:
                output.append(f"    {line[2:]}")
        
        return '\n'.join(output)
    
    @staticmethod
    def colorize_diff(diff_text: str) -> str:
        """Add ANSI colors to diff"""
        lines = diff_text.split('\n')
        colored = []
        
        for line in lines:
            if line.startswith('+'):
                colored.append(f"\033[92m{line}\033[0m")  # Green
            elif line.startswith('-'):
                colored.append(f"\033[91m{line}\033[0m")  # Red
            elif line.startswith('@@'):
                colored.append(f"\033[96m{line}\033[0m")  # Cyan
            else:
                colored.append(line)
        
        return '\n'.join(colored)
