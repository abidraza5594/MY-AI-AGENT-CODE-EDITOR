"""Logging utilities for AI Code Agent"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class AgentLogger:
    """Custom logger for the AI agent with colored output"""
    
    COLORS = {
        'RESET': '\033[0m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'BOLD': '\033[1m'
    }
    
    def __init__(self, name: str = "AIAgent", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Fix Windows console encoding
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['RESET']}"
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(self._colorize(f"ℹ️  {message}", 'CYAN'))
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(self._colorize(f"✅ {message}", 'GREEN'))
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(self._colorize(f"⚠️  {message}", 'YELLOW'))
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(self._colorize(f"❌ {message}", 'RED'))
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def step(self, step_num: int, message: str):
        """Log a step in the process"""
        self.logger.info(self._colorize(f"\n{'='*60}\n🔹 STEP {step_num}: {message}\n{'='*60}", 'BOLD'))
    
    def agent_action(self, agent: str, action: str):
        """Log agent action"""
        self.logger.info(self._colorize(f"🤖 [{agent}] {action}", 'MAGENTA'))
    
    def tool_call(self, tool: str, details: str):
        """Log tool call"""
        self.logger.info(self._colorize(f"🔧 [TOOL: {tool}] {details}", 'BLUE'))
    
    def file_operation(self, operation: str, file_path: str):
        """Log file operation"""
        self.logger.info(self._colorize(f"📝 [{operation}] {file_path}", 'WHITE'))

# Global logger instance
_logger_instance: Optional[AgentLogger] = None

def get_logger() -> AgentLogger:
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        log_dir = Path(".ai_agent_logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        _logger_instance = AgentLogger(log_file=str(log_file))
    return _logger_instance
