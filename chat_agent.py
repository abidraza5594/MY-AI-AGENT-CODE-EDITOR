"""
Interactive Chat-Based AI Code Agent
Type your instructions, get instant code modifications
"""
import os
import sys
from pathlib import Path
from datetime import datetime

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
from diff_viewer import DiffViewer

class ChatAgent:
    """Interactive chat-based coding agent"""
    
    def __init__(self):
        self.config = Config.from_env()
        self.config.AUTO_APPROVE = True  # Auto mode for chat
        
        self.llm = LLMClient(self.config.OLLAMA_BASE_URL)
        self.scanner = ProjectScanner(self.config)
        self.selector = FileSelector(self.config)
        self.snippet_extractor = SnippetExtractor(self.config)
        self.planner = PlannerAgent(self.config, self.llm)
        self.worker = WorkerAgent(self.config, self.llm)
        self.tools = Tools(self.config.BACKUP_DIR)
        self.patcher = Patcher(self.tools, self.config.CREATE_BACKUPS)
        
        self.current_project = "."
        self.chat_history = []
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print("  🤖 AI CODE AGENT - INTERACTIVE CHAT MODE")
        print("="*70)
        print("\n💬 Chat with your AI coding assistant!")
        print("� Typee 'create <description>' to generate a complete project")
        print("📝 Type your instructions to modify existing code")
        print("❌ Type 'exit' or 'quit' to stop")
        print("🆘 Type 'help' for all commands\n")
    
    def print_help(self):
        """Print help message"""
        print("\n" + "="*70)
        print("  AVAILABLE COMMANDS")
        print("="*70)
        
        print("\n🚀 Create New Project:")
        print("  create <description>")
        print("  - Example: 'create Angular todo app'")
        print("  - Example: 'create React calculator app'")
        print("  - Example: 'create Python Flask API'")
        
        print("\n📝 Code Modification:")
        print("  - Just type your instruction naturally")
        print("  - Example: 'Add docstrings to all functions'")
        print("  - Example: 'Add type hints to calculator.py'")
        print("  - Example: 'Fix all TODO comments'")
        
        print("\n📂 Project Management:")
        print("  project <path>  - Change project directory")
        print("  scan            - Show all project files")
        print("  files           - List files in current project")
        
        print("\n💬 Chat Management:")
        print("  history         - Show conversation history")
        print("  clear           - Clear chat history")
        
        print("\n🔧 System:")
        print("  help            - Show this help message")
        print("  status          - Check Ollama connection")
        print("  exit/quit       - Exit chat mode")
        print()
    
    def check_ollama(self):
        """Check if Ollama is running"""
        if not self.llm.check_connection():
            print("\n❌ ERROR: Cannot connect to Ollama!")
            print("   Please start Ollama: ollama serve")
            print("   Then pull model: ollama pull qwen2.5-coder:7b\n")
            return False
        return True
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        cmd = user_input.lower().strip()
        
        if cmd in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye! Happy coding!\n")
            return True
        
        if cmd == 'help':
            self.print_help()
            return True
        
        if cmd == 'history':
            self.show_history()
            return True
        
        if cmd == 'clear':
            self.chat_history.clear()
            print("\n✅ Chat history cleared!\n")
            return True
        
        if cmd == 'scan' or cmd == 'files':
            self.scan_project()
            return True
        
        if cmd == 'status':
            self.check_status()
            return True
        
        if cmd.startswith('project '):
            path = cmd[8:].strip()
            self.change_project(path)
            return True
        
        # New: Create project command
        if cmd.startswith('create '):
            instruction = user_input[7:].strip()
            self.create_project(instruction)
            return True
        
        return False
    
    def show_history(self):
        """Show chat history"""
        if not self.chat_history:
            print("\n📋 No chat history yet.\n")
            return
        
        print("\n" + "="*70)
        print("  CHAT HISTORY")
        print("="*70)
        for i, entry in enumerate(self.chat_history, 1):
            print(f"\n[{i}] {entry['timestamp']}")
            print(f"You: {entry['instruction']}")
            print(f"Result: {entry['result']}")
        print()
    
    def scan_project(self):
        """Scan and display project files"""
        print(f"\n🔍 Scanning project: {self.current_project}")
        files = self.scanner.scan(self.current_project)
        
        if not files:
            print("❌ No files found!\n")
            return
        
        print(f"\n✅ Found {len(files)} files:\n")
        for f in files[:20]:
            print(f"  📄 {f['path']} ({f['lines']} lines)")
        
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more files")
        print()
    
    def change_project(self, path: str):
        """Change current project directory"""
        if not Path(path).exists():
            print(f"\n❌ Path does not exist: {path}\n")
            return
        
        self.current_project = path
        print(f"\n✅ Changed project to: {path}\n")
    
    def check_status(self):
        """Check system status"""
        print("\n" + "="*70)
        print("  SYSTEM STATUS")
        print("="*70)
        
        # Ollama connection
        if self.llm.check_connection():
            print("\n✅ Ollama: Connected")
            models = self.llm.list_models()
            print(f"   Models available: {len(models)}")
            for model in models[:3]:
                print(f"   - {model}")
        else:
            print("\n❌ Ollama: Not connected")
        
        # Current project
        print(f"\n📂 Current project: {self.current_project}")
        
        # Files
        files = self.scanner.scan(self.current_project)
        print(f"📄 Files found: {len(files)}")
        
        print()
    
    def create_project(self, instruction: str):
        """Create a complete project from scratch based on instruction"""
        print(f"\n{'='*70}")
        print(f"  🚀 CREATING PROJECT")
        print(f"{'='*70}\n")
        print(f"📋 Instruction: {instruction}\n")
        
        # Ask LLM to generate project structure
        prompt = f"""You are a project scaffolding expert. Create a complete project structure based on this instruction:

"{instruction}"

Output ONLY valid JSON with this structure:
{{
  "project_name": "folder-name",
  "project_type": "angular/react/python/etc",
  "files": [
    {{
      "path": "relative/path/to/file.ext",
      "content": "complete file content here"
    }}
  ]
}}

Generate a complete, working project with all necessary files.
"""
        
        try:
            print("🧠 Planning project structure...")
            response = self.llm.generate(
                prompt=prompt,
                model=self.config.PLANNER_MODEL,
                temperature=0.3,
                max_tokens=8000
            )
            
            # Parse response
            import json
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            
            project_data = json.loads(response)
            
            project_name = project_data.get("project_name", "new-project")
            project_type = project_data.get("project_type", "unknown")
            files = project_data.get("files", [])
            
            print(f"✅ Project plan created!")
            print(f"   Name: {project_name}")
            print(f"   Type: {project_type}")
            print(f"   Files: {len(files)}")
            
            # Ask for location
            print(f"\n📂 Where to create project?")
            location = input("   Path (default: current directory): ").strip()
            if not location:
                location = "."
            
            # Create project folder
            from pathlib import Path
            project_path = Path(location) / project_name
            project_path.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📁 Creating files in: {project_path}")
            
            # Create all files
            created_count = 0
            for file_info in files:
                file_path = project_path / file_info["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info["content"])
                
                print(f"   ✅ {file_info['path']}")
                created_count += 1
            
            print(f"\n{'='*70}")
            print(f"  ✅ PROJECT CREATED!")
            print(f"{'='*70}")
            print(f"\n📂 Location: {project_path}")
            print(f"📄 Files created: {created_count}")
            print(f"\n💡 Next steps:")
            print(f"   1. cd {project_path}")
            print(f"   2. Review the files")
            print(f"   3. Install dependencies if needed")
            print(f"\n💬 Want to modify? Type: project {project_path}\n")
            
        except Exception as e:
            print(f"\n❌ Error creating project: {e}")
            print("Try being more specific in your instruction.\n")
    
    def process_instruction(self, instruction: str):
        """Process user instruction"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{'='*70}")
        print(f"  🤖 Processing: {instruction}")
        print(f"{'='*70}\n")
        
        try:
            # Step 1: Scan project
            print("📂 Scanning project...")
            all_files = self.scanner.scan(self.current_project)
            if not all_files:
                print("❌ No files found in project!\n")
                return
            print(f"   Found {len(all_files)} files")
            
            # Step 2: Select relevant files
            print("🔍 Selecting relevant files...")
            relevant_files = self.selector.select_files(all_files, instruction)
            if not relevant_files:
                print("❌ No relevant files found!\n")
                return
            print(f"   Selected {len(relevant_files)} files")
            
            # Step 3: Create plan
            print("🧠 Creating execution plan...")
            plan = self.planner.create_plan(instruction, relevant_files)
            
            if not plan.get("targets"):
                print("✅ No changes needed!\n")
                self.chat_history.append({
                    'timestamp': timestamp,
                    'instruction': instruction,
                    'result': 'No changes needed'
                })
                return
            
            print(f"   Plan created: {len(plan['targets'])} files to modify")
            
            # Step 4: Execute edits
            modified_count = 0
            for target in plan.get("targets", []):
                file_path = target["file"]
                full_path = Path(self.current_project) / file_path
                
                if not full_path.exists():
                    print(f"⚠️  File not found: {file_path}")
                    continue
                
                print(f"\n📝 Modifying: {file_path}")
                
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
                
                # Generate edits
                action_desc = target.get("reason", "Make necessary changes")
                edits_result = self.worker.generate_edits(
                    file_path, snippet, instruction, action_desc
                )
                
                edits = edits_result.get("edits", [])
                if not edits:
                    print(f"   ⚠️  No edits generated")
                    continue
                
                # Apply edits
                success = self.patcher.apply_edits(str(full_path), edits)
                if success:
                    modified_count += 1
                    print(f"   ✅ Applied {len(edits)} edits")
                    
                    # Show diff
                    old_content = self.tools.read_file(str(full_path) + ".backup") or ""
                    new_content = self.tools.read_file(str(full_path)) or ""
                    if old_content and new_content:
                        diff = DiffViewer.generate_unified_diff(
                            old_content, new_content, file_path
                        )
                        print("\n" + DiffViewer.colorize_diff(diff)[:500])
            
            # Summary
            print(f"\n{'='*70}")
            print(f"  ✅ COMPLETED")
            print(f"{'='*70}")
            print(f"Modified {modified_count} file(s)")
            print(f"Backups saved in: {self.config.BACKUP_DIR}\n")
            
            self.chat_history.append({
                'timestamp': timestamp,
                'instruction': instruction,
                'result': f'Modified {modified_count} files'
            })
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print(f"   You can copy this error and ask me to fix it!\n")
            
            self.chat_history.append({
                'timestamp': timestamp,
                'instruction': instruction,
                'result': f'Error: {str(e)}'
            })
    
    def run(self):
        """Main chat loop"""
        self.print_banner()
        
        # Check Ollama
        if not self.check_ollama():
            return
        
        print(f"✅ Connected to Ollama")
        print(f"📂 Current project: {self.current_project}\n")
        
        # Main loop
        while True:
            try:
                # Get user input
                user_input = input("💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.handle_command(user_input):
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                    continue
                
                # Process as instruction
                self.process_instruction(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit.\n")
                continue
            except EOFError:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}\n")
                continue

def main():
    """Entry point"""
    agent = ChatAgent()
    agent.run()

if __name__ == "__main__":
    main()
