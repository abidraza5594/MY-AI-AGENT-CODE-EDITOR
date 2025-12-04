"""Main orchestrator for autonomous AI code agent"""
import sys
from pathlib import Path
from typing import List, Dict

from config import Config
from logger import get_logger
from scanner import ProjectScanner
from selector import FileSelector
from snippet_extractor import SnippetExtractor
from planner import PlannerAgent
from worker import WorkerAgent
from tools import Tools
from patcher import Patcher
from llm import LLMClient
from state import AgentState
from diff_viewer import DiffViewer

logger = get_logger()

class AutonomousAgent:
    """Main autonomous agent orchestrator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMClient(config.OLLAMA_BASE_URL)
        self.scanner = ProjectScanner(config)
        self.selector = FileSelector(config)
        self.snippet_extractor = SnippetExtractor(config)
        self.planner = PlannerAgent(config, self.llm)
        self.worker = WorkerAgent(config, self.llm)
        self.tools = Tools(config.BACKUP_DIR)
        self.patcher = Patcher(self.tools, config.CREATE_BACKUPS)
        self.state = AgentState()
    
    def run(self, instruction: str, project_path: str = "."):
        """
        Main execution loop
        
        Args:
            instruction: High-level user instruction
            project_path: Path to project directory
        """
        logger.info(f"🚀 Starting Autonomous AI Code Agent")
        logger.info(f"📋 Instruction: {instruction}")
        logger.info(f"📁 Project: {project_path}")
        
        self.state.start(instruction)
        
        # Check Ollama connection
        if not self.llm.check_connection():
            logger.error("Cannot connect to Ollama. Make sure it's running: ollama serve")
            return
        
        try:
            # Main autonomous loop
            for iteration in range(1, self.config.MAX_ITERATIONS + 1):
                self.state.iteration = iteration
                logger.step(iteration, f"Iteration {iteration}/{self.config.MAX_ITERATIONS}")
                
                # Step 1: Scan project
                logger.info("Step 1: Scanning project...")
                all_files = self.scanner.scan(project_path)
                if not all_files:
                    logger.error("No files found to process")
                    break
                
                # Step 2: Select relevant files
                logger.info("Step 2: Selecting relevant files...")
                relevant_files = self.selector.select_files(all_files, instruction)
                
                # Step 3: Create plan
                logger.info("Step 3: Creating execution plan...")
                plan = self.planner.create_plan(instruction, relevant_files)
                self.state.plan = plan
                
                if not plan.get("targets") and not plan.get("actions"):
                    logger.success("No actions needed. Task complete!")
                    break
                
                # Step 4: Install packages if needed
                if plan.get("package_installs") and self.config.ENABLE_AUTO_INSTALL:
                    logger.info("Step 4: Installing packages...")
                    self._install_packages(plan["package_installs"])
                
                # Step 5: Web search if needed
                search_results = []
                if plan.get("websearch_queries") and self.config.ENABLE_WEB_SEARCH:
                    logger.info("Step 5: Performing web searches...")
                    search_results = self._perform_searches(plan["websearch_queries"])
                    
                    # Refine plan with search results
                    if search_results:
                        logger.info("Refining plan with search results...")
                        plan = self.planner.refine_plan_with_search(
                            plan, search_results, instruction
                        )
                        self.state.plan = plan
                
                # Step 6: Execute code edits
                if plan.get("targets"):
                    logger.info("Step 6: Executing code edits...")
                    self._execute_edits(plan, instruction, project_path)
                
                # Step 7: Run tests if requested
                if plan.get("run_tests"):
                    logger.info("Step 7: Running tests...")
                    self._run_tests(plan.get("test_command", "pytest"))
                
                # Check if we should continue
                if not self._should_continue(plan):
                    logger.success("All tasks completed!")
                    break
            
            # Execution complete
            self.state.finish()
            logger.success("✅ Agent execution complete!")
            print("\n" + self.state.summary())
            self.state.save()
            
        except KeyboardInterrupt:
            logger.warning("Execution interrupted by user")
            self.state.finish()
            self.state.save()
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self.state.add_error(str(e))
            self.state.finish()
            self.state.save()
            raise
    
    def _install_packages(self, packages: List[str]):
        """Install required packages"""
        results = self.tools.install_packages(packages)
        for pkg, success in results.items():
            self.state.add_package_install(pkg, success)
            if not success:
                logger.warning(f"Failed to install {pkg}")
    
    def _perform_searches(self, queries: List[str]) -> List[Dict]:
        """Perform web searches"""
        all_results = []
        for query in queries:
            results = self.tools.websearch_ddg(query, self.config.DUCKDUCKGO_MAX_RESULTS)
            all_results.extend(results)
            self.state.add_search_query(query, len(results))
        return all_results
    
    def _execute_edits(self, plan: Dict, instruction: str, project_path: str):
        """Execute code edits on target files"""
        targets = plan.get("targets", [])
        actions = plan.get("actions", [])
        
        for target in targets:
            file_path = target["file"]
            full_path = Path(project_path) / file_path
            
            if not full_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            logger.info(f"Processing: {file_path}")
            
            # Read file
            file_lines = self.scanner.get_file_lines(str(full_path))
            if not file_lines:
                continue
            
            # Extract snippet
            from utils import extract_keywords
            keywords = extract_keywords(instruction)
            snippet = self.snippet_extractor.extract_snippets(
                file_path, file_lines, keywords
            )
            
            # Find relevant action
            action_desc = target.get("reason", "Make necessary changes")
            for action in actions:
                if file_path in action.get("files", []):
                    action_desc = action.get("description", action_desc)
                    break
            
            # Generate edits
            edits_result = self.worker.generate_edits(
                file_path, snippet, instruction, action_desc
            )
            
            edits = edits_result.get("edits", [])
            if not edits:
                logger.warning(f"No edits generated for {file_path}")
                continue
            
            # Show preview if not auto-approve
            if not self.config.AUTO_APPROVE:
                preview = self.patcher.preview_edits(str(full_path), edits)
                print("\n" + preview)
                
                response = input(f"\nApply {len(edits)} edits to {file_path}? (y/n): ")
                if response.lower() != 'y':
                    logger.info("Skipped by user")
                    continue
            
            # Apply edits
            success = self.patcher.apply_edits(str(full_path), edits)
            if success:
                self.state.add_modified_file(file_path, len(edits))
                
                # Show diff
                old_content = self.tools.read_file(str(full_path) + ".backup") or ""
                new_content = self.tools.read_file(str(full_path)) or ""
                if old_content and new_content:
                    diff = DiffViewer.generate_unified_diff(
                        old_content, new_content, file_path
                    )
                    print("\n" + DiffViewer.colorize_diff(diff))
    
    def _run_tests(self, test_command: str):
        """Run test command"""
        if not test_command:
            test_command = "pytest"
        
        logger.info(f"Running: {test_command}")
        result = self.tools.run_shell_command(test_command.split())
        
        self.state.add_test_run(
            test_command,
            result["success"],
            result["stdout"] + result["stderr"]
        )
        
        if result["success"]:
            logger.success("Tests passed!")
        else:
            logger.error("Tests failed!")
            print(result["stderr"])
    
    def _should_continue(self, plan: Dict) -> bool:
        """Determine if agent should continue iterating"""
        # If no more actions, stop
        if not plan.get("actions"):
            return False
        
        # If in auto mode, continue
        if self.config.AUTO_APPROVE:
            return True
        
        # Ask user
        response = input("\nContinue to next iteration? (y/n): ")
        return response.lower() == 'y'

def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous AI Code Agent - DEVIN-style developer assistant"
    )
    parser.add_argument(
        "instruction",
        help="High-level instruction for the agent"
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project directory path (default: current directory)"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve all changes (FULLY AUTOMATIC MODE)"
    )
    parser.add_argument(
        "--no-search",
        action="store_true",
        help="Disable web search"
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Disable automatic package installation"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum iterations (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = Config.from_env()
    config.AUTO_APPROVE = args.auto_approve
    config.ENABLE_WEB_SEARCH = not args.no_search
    config.ENABLE_AUTO_INSTALL = not args.no_install
    config.MAX_ITERATIONS = args.max_iterations
    
    # Create and run agent
    agent = AutonomousAgent(config)
    agent.run(args.instruction, args.project)

if __name__ == "__main__":
    main()
