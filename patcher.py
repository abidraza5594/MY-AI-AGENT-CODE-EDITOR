"""Patcher - applies code edits to files"""
from typing import Dict, List
from tools import Tools
from logger import get_logger

logger = get_logger()

class Patcher:
    """Applies edits to files"""
    
    def __init__(self, tools: Tools, create_backups: bool = True):
        self.tools = tools
        self.create_backups = create_backups
    
    def apply_edits(self, file_path: str, edits: List[Dict]) -> bool:
        """
        Apply list of edits to a file
        
        Args:
            file_path: Path to file
            edits: List of edit operations
            
        Returns:
            True if all edits applied successfully
        """
        if not edits:
            logger.warning(f"No edits to apply for {file_path}")
            return False
        
        # Read current content
        content = self.tools.read_file(file_path)
        if content is None:
            logger.error(f"Cannot read file: {file_path}")
            return False
        
        # Create backup
        if self.create_backups:
            self.tools.create_backup(file_path)
        
        # Apply each edit
        modified_content = content
        applied_count = 0
        
        for i, edit in enumerate(edits):
            try:
                if edit["operation"] == "replace":
                    match_text = edit["match"]
                    replacement = edit["replacement"]
                    
                    if match_text not in modified_content:
                        logger.warning(f"Edit {i+1}: Match not found in file")
                        continue
                    
                    # Check uniqueness
                    count = modified_content.count(match_text)
                    if count > 1:
                        logger.warning(f"Edit {i+1}: Match appears {count} times, skipping")
                        continue
                    
                    # Apply replacement
                    modified_content = modified_content.replace(match_text, replacement, 1)
                    applied_count += 1
                    logger.success(f"Edit {i+1}: Applied successfully")
                
                else:
                    logger.warning(f"Edit {i+1}: Unknown operation '{edit['operation']}'")
            
            except Exception as e:
                logger.error(f"Edit {i+1}: Failed to apply - {e}")
                continue
        
        if applied_count == 0:
            logger.warning(f"No edits were applied to {file_path}")
            return False
        
        # Write modified content
        success = self.tools.write_file(file_path, modified_content)
        
        if success:
            logger.success(f"Applied {applied_count}/{len(edits)} edits to {file_path}")
        
        return success
    
    def preview_edits(self, file_path: str, edits: List[Dict]) -> str:
        """Generate preview of what edits would do"""
        content = self.tools.read_file(file_path)
        if content is None:
            return "Error: Cannot read file"
        
        preview = f"=== Preview for {file_path} ===\n\n"
        
        for i, edit in enumerate(edits):
            preview += f"--- Edit {i+1} ---\n"
            preview += f"Operation: {edit['operation']}\n"
            preview += f"Match:\n{edit.get('match', 'N/A')}\n"
            preview += f"Replacement:\n{edit.get('replacement', 'N/A')}\n\n"
        
        return preview
