"""Tools module - provides file I/O, shell, package install, and web search capabilities"""
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import requests
from logger import get_logger

logger = get_logger()

class Tools:
    """Collection of tools the agent can use"""
    
    def __init__(self, backup_dir: str = ".ai_agent_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    # ===== FILE OPERATIONS =====
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            logger.file_operation("READ", path)
            return content
        except Exception as e:
            logger.error(f"Failed to read {path}: {e}")
            return None
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.file_operation("WRITE", path)
            return True
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            return False
    
    def create_backup(self, path: str) -> Optional[str]:
        """Create backup of file"""
        try:
            if not Path(path).exists():
                return None
            
            backup_path = self.backup_dir / Path(path).name
            counter = 1
            while backup_path.exists():
                backup_path = self.backup_dir / f"{Path(path).stem}_{counter}{Path(path).suffix}"
                counter += 1
            
            shutil.copy2(path, backup_path)
            logger.file_operation("BACKUP", f"{path} -> {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to backup {path}: {e}")
            return None
    
    def list_files(self, root: str, recursive: bool = True) -> List[str]:
        """List files in directory"""
        try:
            root_path = Path(root)
            if recursive:
                files = [str(p) for p in root_path.rglob("*") if p.is_file()]
            else:
                files = [str(p) for p in root_path.glob("*") if p.is_file()]
            return files
        except Exception as e:
            logger.error(f"Failed to list files in {root}: {e}")
            return []
    
    # ===== SHELL OPERATIONS =====
    
    def run_shell_command(self, command: List[str], cwd: str = None, 
                         timeout: int = 300) -> Dict:
        """
        Run shell command and return result
        
        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "returncode": int
            }
        """
        logger.tool_call("SHELL", f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            
            if success:
                logger.success(f"Command succeeded: {' '.join(command)}")
            else:
                logger.warning(f"Command failed with code {result.returncode}")
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    # ===== PACKAGE INSTALLATION =====
    
    def pip_install(self, package: str) -> bool:
        """Install Python package using pip"""
        logger.tool_call("PIP", f"Installing {package}")
        result = self.run_shell_command(["pip", "install", package])
        return result["success"]
    
    def npm_install(self, package: str, dev: bool = False) -> bool:
        """Install npm package"""
        logger.tool_call("NPM", f"Installing {package}")
        cmd = ["npm", "install"]
        if dev:
            cmd.append("--save-dev")
        cmd.append(package)
        result = self.run_shell_command(cmd)
        return result["success"]
    
    def install_packages(self, packages: List[str]) -> Dict[str, bool]:
        """
        Install multiple packages
        Format: ["pip:requests", "npm:axios", "npm:@types/node"]
        """
        results = {}
        
        for pkg in packages:
            if ":" not in pkg:
                logger.warning(f"Invalid package format: {pkg}")
                results[pkg] = False
                continue
            
            manager, package_name = pkg.split(":", 1)
            
            if manager == "pip":
                results[pkg] = self.pip_install(package_name)
            elif manager == "npm":
                results[pkg] = self.npm_install(package_name)
            else:
                logger.warning(f"Unknown package manager: {manager}")
                results[pkg] = False
        
        return results
    
    # ===== WEB SEARCH =====
    
    def websearch_ddg(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search using DuckDuckGo
        
        Returns:
            [{"title": str, "url": str, "snippet": str}]
        """
        logger.tool_call("WEBSEARCH", f"Searching: {query}")
        
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
            
            logger.success(f"Found {len(results)} search results")
            return results
            
        except ImportError:
            logger.error("duckduckgo_search not installed. Run: pip install duckduckgo-search")
            return []
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    # ===== DIFF OPERATIONS =====
    
    def show_diff(self, old_content: str, new_content: str, file_path: str) -> str:
        """Generate unified diff"""
        import difflib
        
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
