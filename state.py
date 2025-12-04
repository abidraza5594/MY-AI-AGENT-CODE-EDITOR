"""State management for agent execution"""
from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path

class AgentState:
    """Tracks agent execution state"""
    
    def __init__(self):
        self.iteration = 0
        self.instruction = ""
        self.plan = {}
        self.files_modified = []
        self.packages_installed = []
        self.tests_run = []
        self.search_queries = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def start(self, instruction: str):
        """Start new execution"""
        self.instruction = instruction
        self.start_time = datetime.now()
    
    def finish(self):
        """Mark execution as finished"""
        self.end_time = datetime.now()
    
    def add_modified_file(self, file_path: str, edits_count: int):
        """Record file modification"""
        self.files_modified.append({
            "file": file_path,
            "edits": edits_count,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_package_install(self, package: str, success: bool):
        """Record package installation"""
        self.packages_installed.append({
            "package": package,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_test_run(self, command: str, success: bool, output: str):
        """Record test execution"""
        self.tests_run.append({
            "command": command,
            "success": success,
            "output": output[:500],  # Truncate
            "timestamp": datetime.now().isoformat()
        })
    
    def add_search_query(self, query: str, results_count: int):
        """Record web search"""
        self.search_queries.append({
            "query": query,
            "results": results_count,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error(self, error: str):
        """Record error"""
        self.errors.append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary"""
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "iteration": self.iteration,
            "instruction": self.instruction,
            "plan": self.plan,
            "files_modified": self.files_modified,
            "packages_installed": self.packages_installed,
            "tests_run": self.tests_run,
            "search_queries": self.search_queries,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration
        }
    
    def save(self, path: str = ".ai_agent_state.json"):
        """Save state to file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str = ".ai_agent_state.json") -> 'AgentState':
        """Load state from file"""
        state = cls()
        if Path(path).exists():
            with open(path, 'r') as f:
                data = json.load(f)
                state.iteration = data.get("iteration", 0)
                state.instruction = data.get("instruction", "")
                state.plan = data.get("plan", {})
                state.files_modified = data.get("files_modified", [])
                state.packages_installed = data.get("packages_installed", [])
                state.tests_run = data.get("tests_run", [])
                state.search_queries = data.get("search_queries", [])
                state.errors = data.get("errors", [])
        return state
    
    def summary(self) -> str:
        """Generate execution summary"""
        lines = []
        lines.append("=" * 60)
        lines.append("EXECUTION SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Instruction: {self.instruction}")
        lines.append(f"Iterations: {self.iteration}")
        lines.append(f"Files Modified: {len(self.files_modified)}")
        lines.append(f"Packages Installed: {len(self.packages_installed)}")
        lines.append(f"Tests Run: {len(self.tests_run)}")
        lines.append(f"Web Searches: {len(self.search_queries)}")
        lines.append(f"Errors: {len(self.errors)}")
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            lines.append(f"Duration: {duration:.2f} seconds")
        
        lines.append("=" * 60)
        return "\n".join(lines)
