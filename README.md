# 🤖 AI Code Agent - Chat Interface

Ek simple chat interface jahan aap type karo aur AI aapka code modify kar de.

## 🚀 Kaise Use Karein?

```bash
# 1. Virtual environment activate karo
venv\Scripts\activate

# 2. Chat start karo
python chat_agent.py

# 3. Type karo
💬 You: Add docstrings to test_calculator.py
```

**Bas itna hi!** 🎉

📖 **Complete guide:** [HOW_TO_USE.md](HOW_TO_USE.md)

## 🎯 Features

✅ **Autonomous Planning** - Creates multi-step execution plans
✅ **Intelligent File Selection** - Finds relevant files automatically  
✅ **Smart Code Editing** - Generates precise code changes
✅ **Package Management** - Auto-installs pip/npm packages
✅ **Web Search Integration** - Searches for solutions when needed
✅ **Test Execution** - Runs tests automatically
✅ **Snippet Extraction** - Avoids token overflow with smart windowing
✅ **Diff Visualization** - Shows changes before applying
✅ **Backup System** - Creates backups before modifications
✅ **Full Auto Mode** - Zero human intervention with `--auto-approve`

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INSTRUCTION                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  PROJECT SCANNER                         │
│  Recursively scans files, ignores node_modules, etc.    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FILE SELECTOR                           │
│  Ranks files by relevance using keyword matching        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  PLANNER AGENT (LLM)                     │
│  Creates execution plan:                                │
│  - Target files                                          │
│  - Actions to perform                                    │
│  - Packages to install                                   │
│  - Web searches needed                                   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │ TOOLS  │  │ WORKER  │  │  TESTS   │
   │        │  │  AGENT  │  │          │
   │ - pip  │  │  (LLM)  │  │ pytest   │
   │ - npm  │  │         │  │ npm test │
   │ - web  │  │ Edits   │  │          │
   │ search │  │ Files   │  │          │
   └────────┘  └─────────┘  └──────────┘
                     │
                     ▼
              ┌──────────┐
              │ PATCHER  │
              │ Applies  │
              │ Changes  │
              └──────────┘
```

## 📦 Installation

### 1. Clone or create project

```bash
mkdir ai_code_agent
cd ai_code_agent
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download from: https://ollama.ai

```bash
# Start Ollama server
ollama serve

# Pull required models (in another terminal)
ollama pull qwen2.5-coder:32b   # Planner model
ollama pull qwen2.5-coder:14b   # Worker model

# Alternative smaller models:
# ollama pull qwen2.5-coder:7b
# ollama pull codellama:13b
```

## 🚀 Usage

### Basic Usage

```bash
python run.py "Convert this Flask app to FastAPI"
```

### Fully Automatic Mode (No Confirmations)

```bash
python run.py "Add error handling to all API endpoints" --auto-approve
```

### Advanced Options

```bash
python run.py "Migrate from Angular modules to standalone components" \\
  --project ./my-angular-app \\
  --auto-approve \\
  --max-iterations 10
```

### All Options

```bash
python run.py <instruction> [options]

Options:
  --project PATH          Project directory (default: current dir)
  --auto-approve          Fully automatic mode, no confirmations
  --no-search            Disable web search
  --no-install           Disable automatic package installation
  --max-iterations N     Maximum iterations (default: 5)
```

## 🔧 Configuration

Edit `config.py` or use environment variables:

```bash
# Ollama settings
export OLLAMA_BASE_URL="http://localhost:11434"
export PLANNER_MODEL="qwen2.5-coder:32b"
export WORKER_MODEL="qwen2.5-coder:14b"

# Agent behavior
export AUTO_APPROVE="true"
export ENABLE_WEB_SEARCH="true"
export ENABLE_AUTO_INSTALL="true"
```

## 📝 Example Instructions

```bash
# Refactoring
python run.py "Convert all class components to functional components with hooks"

# Feature addition
python run.py "Add authentication middleware to all protected routes"

# Migration
python run.py "Migrate from JavaScript to TypeScript"

# Testing
python run.py "Add unit tests for all service classes"

# Optimization
python run.py "Optimize database queries and add caching"

# Bug fixing
python run.py "Fix all ESLint errors and add proper error handling"
```

## 🛠️ How It Works

### 1. Planning Phase
The **Planner Agent** analyzes your instruction and creates a structured plan:
- Identifies which files need changes
- Determines what actions to perform
- Checks if packages need installation
- Decides if web search is needed

### 2. Tool Execution Phase
- **Package Installation**: Automatically runs `pip install` or `npm install`
- **Web Search**: Searches DuckDuckGo for relevant information
- **Plan Refinement**: Updates plan based on search results

### 3. Execution Phase
For each target file:
- **Snippet Extraction**: Extracts relevant code sections (avoids token overflow)
- **Worker Agent**: Generates precise edit operations
- **Patcher**: Applies edits with backup creation
- **Diff Display**: Shows what changed

### 4. Validation Phase
- Runs tests if specified in plan
- Checks for errors
- Decides if more iterations needed

## 🔒 Safety Features

- **Backups**: All files backed up before modification
- **Preview Mode**: Shows changes before applying (unless `--auto-approve`)
- **Unique Matching**: Only applies edits if match is unique
- **Error Recovery**: Continues on errors, logs everything
- **State Persistence**: Saves execution state to `.ai_agent_state.json`

## 📊 Output

The agent provides:
- Colored console output with progress indicators
- Detailed logs in `.ai_agent_logs/`
- Unified diffs showing all changes
- Execution summary with statistics
- State file for resuming/debugging

## 🧪 Testing

```bash
# Run agent on test project
python run.py "Add docstrings to all functions" --project ./test_project

# Check logs
cat .ai_agent_logs/agent_*.log

# Review state
cat .ai_agent_state.json
```

## ⚙️ Automatic Package Installation

When the planner detects missing dependencies:

```json
{
  "package_installs": [
    "pip:requests",
    "pip:fastapi",
    "npm:axios",
    "npm:@types/react"
  ]
}
```

The agent automatically runs:
```bash
pip install requests fastapi
npm install axios @types/react
```

## 🌐 Web Search Integration

When the agent needs more information:

```json
{
  "websearch_queries": [
    "How to migrate HttpModule to HttpClientModule in Angular",
    "FastAPI async database connection best practices"
  ]
}
```

Results are fed back to the planner for plan refinement.

## 🚨 Limitations

- **LLM Dependent**: Quality depends on Ollama model capabilities
- **Token Limits**: Very large files may be truncated
- **No Rollback**: Manual restoration from backups if needed
- **Single Project**: Processes one project at a time
- **Local Only**: Requires local Ollama installation

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve
```

### "Model not found"
```bash
# Pull the required models
ollama pull qwen2.5-coder:32b
ollama pull qwen2.5-coder:14b
```

### "No edits applied"
- Check if match text is exact
- Try with smaller, more specific instructions
- Review logs in `.ai_agent_logs/`

### "Package installation failed"
- Ensure pip/npm are in PATH
- Check internet connection
- Try manual installation first

## 📄 License

MIT License - Use freely for any purpose

## 🤝 Contributing

This is a production-ready autonomous agent. Contributions welcome:
- Better LLM prompts
- Additional tool integrations
- Improved file selection algorithms
- Support for more languages/frameworks

## 🎓 Credits

Built with:
- **Ollama** - Local LLM inference
- **Qwen2.5-Coder** - Code-specialized models
- **DuckDuckGo** - Web search API
- **Python** - Core implementation

---

**⚡ Ready to let AI handle your refactoring? Start with `--auto-approve` and watch it work!**
