"""Configuration management for AI Code Agent"""
import os
from typing import List, Dict, Any

class Config:
    """Central configuration for the AI agent"""
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    PLANNER_MODEL: str = os.getenv("PLANNER_MODEL", "qwen2.5-coder:7b")
    WORKER_MODEL: str = os.getenv("WORKER_MODEL", "qwen2.5-coder:7b")
    
    # Token limits
    MAX_CONTEXT_TOKENS: int = 32000
    SNIPPET_CONTEXT_LINES: int = 60
    MAX_FILES_TO_ANALYZE: int = 15
    
    # Directories to ignore during scanning
    IGNORE_DIRS: List[str] = [
        "node_modules", "dist", "build", ".git", "venv", 
        "__pycache__", ".pytest_cache", "coverage", ".next",
        "target", "out", ".idea", ".vscode", "vendor"
    ]
    
    # File extensions to process
    SUPPORTED_EXTENSIONS: List[str] = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go",
        ".rs", ".cpp", ".c", ".h", ".hpp", ".cs", ".rb",
        ".php", ".html", ".css", ".scss", ".vue", ".svelte"
    ]
    
    # Agent behavior
    MAX_ITERATIONS: int = 5
    AUTO_APPROVE: bool = False
    ENABLE_WEB_SEARCH: bool = True
    ENABLE_AUTO_INSTALL: bool = True
    
    # Backup settings
    CREATE_BACKUPS: bool = True
    BACKUP_DIR: str = ".ai_agent_backups"
    
    # Web search
    DUCKDUCKGO_MAX_RESULTS: int = 5
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        config = cls()
        config.AUTO_APPROVE = os.getenv("AUTO_APPROVE", "false").lower() == "true"
        config.ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
        config.ENABLE_AUTO_INSTALL = os.getenv("ENABLE_AUTO_INSTALL", "true").lower() == "true"
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "ollama_base_url": self.OLLAMA_BASE_URL,
            "planner_model": self.PLANNER_MODEL,
            "worker_model": self.WORKER_MODEL,
            "max_context_tokens": self.MAX_CONTEXT_TOKENS,
            "auto_approve": self.AUTO_APPROVE,
            "enable_web_search": self.ENABLE_WEB_SEARCH,
            "enable_auto_install": self.ENABLE_AUTO_INSTALL
        }
