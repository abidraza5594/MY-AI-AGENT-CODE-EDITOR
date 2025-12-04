"""Quick test script to verify agent setup"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
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
        from utils import extract_keywords
        
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        config = Config.from_env()
        print(f"  Ollama URL: {config.OLLAMA_BASE_URL}")
        print(f"  Planner Model: {config.PLANNER_MODEL}")
        print(f"  Worker Model: {config.WORKER_MODEL}")
        print("✅ Configuration loaded!")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_logger():
    """Test logger"""
    print("\nTesting logger...")
    
    try:
        from logger import get_logger
        logger = get_logger()
        logger.info("Test info message")
        logger.success("Test success message")
        logger.warning("Test warning message")
        print("✅ Logger working!")
        return True
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

def test_llm_connection():
    """Test Ollama connection"""
    print("\nTesting Ollama connection...")
    
    try:
        from llm import LLMClient
        from config import Config
        
        config = Config.from_env()
        llm = LLMClient(config.OLLAMA_BASE_URL)
        
        if llm.check_connection():
            print("✅ Ollama is running!")
            models = llm.list_models()
            print(f"  Available models: {len(models)}")
            for model in models[:5]:
                print(f"    - {model}")
            return True
        else:
            print("⚠️  Ollama not running. Start with: ollama serve")
            return False
    except Exception as e:
        print(f"❌ LLM connection test failed: {e}")
        return False

def test_tools():
    """Test tools"""
    print("\nTesting tools...")
    
    try:
        from tools import Tools
        tools = Tools()
        
        # Test file operations
        test_file = ".test_agent_temp.txt"
        tools.write_file(test_file, "Test content")
        content = tools.read_file(test_file)
        
        if content == "Test content":
            print("✅ File operations working!")
            Path(test_file).unlink()
            return True
        else:
            print("❌ File operations failed")
            return False
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI CODE AGENT - SETUP VERIFICATION")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Logger", test_logger()))
    results.append(("Tools", test_tools()))
    results.append(("Ollama Connection", test_llm_connection()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Agent is ready to use.")
        print("\nNext steps:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Pull models: ollama pull qwen2.5-coder:32b")
        print("3. Run agent: python run.py \"your instruction here\"")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
