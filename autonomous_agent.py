"""
Fully Autonomous AI Agent
- Creates any project from scratch
- Edits any file anywhere
- Fixes errors automatically
- No manual intervention needed
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Force unbuffered output for real-time display
os.environ['PYTHONUNBUFFERED'] = '1'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

from config import Config
from logger import get_logger
from llm import LLMClient
from tools import Tools

class AutonomousAgent:
    """Fully autonomous AI coding agent"""
    
    def __init__(self):
        self.config = Config.from_env()
        self.llm = LLMClient(self.config.OLLAMA_BASE_URL)
        self.tools = Tools()
        self.conversation_history = []
        self.current_file_buffer = ""
        self.current_file_path = ""
        self.in_file_content = False
        self.step_count = 0
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print("  🤖 FULLY AUTONOMOUS AI AGENT")
        print("="*70)
        print("\n✨ I can do ANYTHING:")
        print("   🚀 Create complete projects from scratch")
        print("   📝 Edit any file anywhere on your system")
        print("   🔧 Fix errors automatically")
        print("   📦 Install packages automatically")
        print("   🌐 Search web for solutions")
        print("\n💬 Just tell me what you want in plain language!")
        print("❌ Type 'exit' to stop\n")
    
    def chat(self):
        """Main chat loop"""
        self.print_banner()
        
        # Check Ollama
        if not self.llm.check_connection():
            print("❌ Cannot connect to Ollama!")
            print("   Start it with: ollama serve\n")
            return
        
        print("✅ Connected to Ollama\n")
        
        while True:
            try:
                # Get user input
                user_input = input("💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                # Process autonomously
                self.process_autonomous(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit.\n")
                continue
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Trying to fix automatically...\n")
                self.auto_fix_error(str(e), user_input)
    
    def process_autonomous(self, instruction: str):
        """Process instruction fully autonomously"""
        print(f"\n{'='*70}")
        print(f"  🤖 PROCESSING: {instruction}")
        print(f"{'='*70}\n")
        
        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'content': instruction
        })
        
        # Ask LLM what to do
        plan = self.create_autonomous_plan(instruction)
        
        if not plan:
            print("❌ Could not create plan\n")
            return
        
        # Execute plan
        self.execute_plan(plan)
    
    def create_autonomous_plan(self, instruction: str) -> dict:
        """Create fully autonomous execution plan"""
        print("🧠 Creating plan and executing in real-time...", flush=True)
        
        # Build context from history
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history[-5:]
        ])
        
        prompt = f"""Task: {instruction}

Output JSON (max 5 files):
{{
  "action_type": "create_project",
  "steps": [
    {{"type": "create_file", "details": {{"path": "D:\\\\Folder\\\\file.ts", "content": "import..."}}}},
    {{"type": "create_file", "details": {{"path": "D:\\\\Folder\\\\file.html", "content": "<div>..."}}}}
  ],
  "location": "D:\\\\Folder"
}}

Rules: Brief code, no ng commands, max 5 files.
JSON:"""
        
        try:
            print("   💭 Generating plan...", flush=True)
            response = self.llm.generate(
                prompt=prompt,
                model=self.config.PLANNER_MODEL,
                temperature=0.2,
                max_tokens=2000
            )
            print("   ✅ Plan generated!", flush=True)
            
            # Parse JSON
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            
            plan = json.loads(response)
            
            print(f"✅ Plan created: {plan['action_type']}")
            print(f"   Description: {plan['description']}")
            print(f"   Steps: {len(plan.get('steps', []))}\n")
            
            return plan
            
        except Exception as e:
            print(f"❌ Planning failed: {e}\n")
            return None
    
    def execute_plan(self, plan: dict):
        """Execute the autonomous plan"""
        action_type = plan.get('action_type')
        steps = plan.get('steps', [])
        location = plan.get('location', '.')
        
        print(f"🚀 Executing {len(steps)} steps...\n")
        
        # Ensure location exists
        if location != 'current':
            Path(location).mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        
        for i, step in enumerate(steps, 1):
            step_type = step.get('type')
            details = step.get('details', {})
            
            print(f"\n{'='*60}", flush=True)
            print(f"Step {i}/{len(steps)}: {step_type}", flush=True)
            print(f"{'='*60}", flush=True)
            
            try:
                if step_type == 'create_folder':
                    self.create_folder(details, location)
                    success_count += 1
                
                elif step_type == 'create_file':
                    self.create_file(details, location)
                    success_count += 1
                
                elif step_type == 'edit_file':
                    self.edit_file(details, location)
                    success_count += 1
                
                elif step_type == 'run_command':
                    self.run_command(details)
                    success_count += 1
                
                elif step_type == 'install':
                    self.install_package(details)
                    success_count += 1
                
                elif step_type == 'search':
                    self.web_search(details)
                    success_count += 1
                
                else:
                    print(f"   ⚠️  Unknown step type: {step_type}")
            
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print(f"   🔧 Attempting auto-fix...")
                self.auto_fix_step(step, str(e))
        
        print(f"\n{'='*70}")
        print(f"  ✅ COMPLETED: {success_count}/{len(steps)} steps successful")
        print(f"{'='*70}\n")
    
    def create_folder(self, details: dict, base_location: str):
        """Create a folder"""
        folder_path = details.get('path', '')
        
        if not folder_path:
            return
        
        full_path = Path(folder_path)
        
        print(f"   📁 Creating folder: {full_path}", flush=True)
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Folder created: {full_path}", flush=True)
    
    def create_file(self, details: dict, base_location: str):
        """Create a file"""
        file_path = details.get('path', '')
        content = details.get('content', '')
        
        if base_location != 'current':
            full_path = Path(base_location) / file_path
        else:
            full_path = Path(file_path)
        
        print(f"   📝 Creating file: {full_path}", flush=True)
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Show file size and preview
        size = len(content)
        lines = content.count('\n') + 1
        print(f"   ✅ File created: {size} bytes, {lines} lines", flush=True)
    
    def edit_file(self, details: dict, base_location: str):
        """Edit an existing file"""
        file_path = details.get('path', '')
        changes = details.get('changes', '')
        
        if base_location != 'current':
            full_path = Path(base_location) / file_path
        else:
            full_path = Path(file_path)
        
        if not full_path.exists():
            print(f"   ⚠️  File doesn't exist, creating: {full_path}")
            self.create_file(details, base_location)
            return
        
        print(f"   📝 Editing: {full_path}", flush=True)
        print(f"   ⏳ Generating changes... (10-20 seconds)", flush=True)
        
        # Read current content
        with open(full_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Ask LLM to apply changes
        prompt = f"""Apply these changes to the file:

Current content:
{current_content}

Changes to make:
{changes}

Output ONLY the complete new file content, no explanations.
"""
        
        new_content = self.llm.generate(
            prompt=prompt,
            model=self.config.WORKER_MODEL,
            temperature=0.2,
            max_tokens=4000
        )
        
        # Backup
        backup_path = full_path.with_suffix(full_path.suffix + '.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(current_content)
        
        # Write new content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   ✅ Edited: {full_path}", flush=True)
        print(f"   💾 Backup: {backup_path}", flush=True)
    
    def run_command(self, details: dict):
        """Run a shell command"""
        command = details.get('command', '')
        
        if not command:
            return
        
        print(f"   🔧 Running: {command}")
        
        result = self.tools.run_shell_command(command.split())
        
        if result['success']:
            print(f"   ✅ Success")
            if result['stdout']:
                print(f"   Output: {result['stdout'][:200]}")
        else:
            print(f"   ❌ Failed: {result['stderr'][:200]}")
    
    def install_package(self, details: dict):
        """Install a package"""
        package = details.get('package', '')
        
        if not package:
            return
        
        print(f"   📦 Installing package: {package}", flush=True)
        print(f"   ⏳ This may take a minute...", flush=True)
        
        if ':' in package:
            manager, pkg_name = package.split(':', 1)
            if manager == 'pip':
                success = self.tools.pip_install(pkg_name)
            elif manager == 'npm':
                success = self.tools.npm_install(pkg_name)
            else:
                print(f"   ⚠️  Unknown package manager: {manager}", flush=True)
                return
        else:
            success = self.tools.pip_install(package)
        
        if success:
            print(f"   ✅ Package installed successfully!", flush=True)
        else:
            print(f"   ❌ Installation failed", flush=True)
    
    def web_search(self, details: dict):
        """Search the web"""
        query = details.get('query', '')
        
        if not query:
            return
        
        print(f"   🌐 Searching web: {query}", flush=True)
        print(f"   ⏳ Searching...", flush=True)
        
        results = self.tools.websearch_ddg(query, max_results=3)
        
        if results:
            print(f"   ✅ Found {len(results)} results:", flush=True)
            for i, r in enumerate(results[:2], 1):
                print(f"      {i}. {r['title']}", flush=True)
        else:
            print(f"   ⚠️  No results found", flush=True)
    
    def auto_fix_error(self, error: str, original_instruction: str):
        """Automatically fix an error"""
        print(f"🔧 Auto-fixing error...\n")
        
        prompt = f"""An error occurred while executing this instruction:
Instruction: {original_instruction}
Error: {error}

Analyze the error and provide a fix. Output JSON:
{{
  "diagnosis": "what went wrong",
  "fix": "how to fix it",
  "steps": ["step 1", "step 2"]
}}
"""
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                model=self.config.PLANNER_MODEL,
                temperature=0.3,
                max_tokens=2000
            )
            
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            
            fix_plan = json.loads(response)
            
            print(f"📋 Diagnosis: {fix_plan.get('diagnosis', 'Unknown')}")
            print(f"🔧 Fix: {fix_plan.get('fix', 'Unknown')}\n")
            
            # Try to apply fix
            for step in fix_plan.get('steps', []):
                print(f"   - {step}")
            
            print("\n✅ Error analysis complete. Try again with more details.\n")
            
        except Exception as e:
            print(f"❌ Could not auto-fix: {e}\n")
    
    def auto_fix_step(self, step: dict, error: str):
        """Fix a failed step"""
        print(f"   🔧 Analyzing failure...")
        
        # Simple retry logic
        try:
            step_type = step.get('type')
            details = step.get('details', {})
            
            if step_type == 'create_file':
                # Maybe directory doesn't exist
                file_path = details.get('path', '')
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                self.create_file(details, 'current')
                print(f"   ✅ Fixed and retried")
            else:
                print(f"   ⚠️  Could not auto-fix this step")
        
        except Exception as e:
            print(f"   ❌ Auto-fix failed: {e}")
    
    def on_plan_chunk(self, chunk: str):
        """Callback for streaming plan generation - creates files in real-time"""
        import re
        
        # Look for file paths and content in the streaming JSON
        # Pattern: "path": "D:\\AbidTodo\\file.ts"
        path_match = re.search(r'"path":\s*"([^"]+)"', chunk)
        if path_match and not self.in_file_content:
            self.current_file_path = path_match.group(1)
            self.step_count += 1
            print(f"\n   📝 [{self.step_count}] Creating: {self.current_file_path}", flush=True)
            self.in_file_content = True
            self.current_file_buffer = ""
        
        # Pattern: "content": "code here..."
        if self.in_file_content and '"content"' in chunk:
            # Start collecting content
            content_start = chunk.find('"content"')
            if content_start != -1:
                # Extract content between quotes
                content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)"', chunk)
                if content_match:
                    content = content_match.group(1)
                    # Unescape the content
                    content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                    
                    # Create file immediately
                    if self.current_file_path and content:
                        try:
                            file_path = Path(self.current_file_path)
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            size = len(content)
                            lines = content.count('\n') + 1
                            print(f"   ✅ Created: {size} bytes, {lines} lines", flush=True)
                            
                            self.in_file_content = False
                            self.current_file_path = ""
                        except Exception as e:
                            print(f"   ⚠️  Error: {e}", flush=True)

def main():
    """Entry point"""
    agent = AutonomousAgent()
    agent.chat()

if __name__ == "__main__":
    main()
