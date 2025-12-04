"""Planner agent - creates high-level execution plans"""
import json
from typing import Dict, List, Any
from llm import LLMClient
from config import Config
from logger import get_logger

logger = get_logger()

class PlannerAgent:
    """High-level planning agent that decides what to do"""
    
    def __init__(self, config: Config, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
    
    def create_plan(self, instruction: str, files: List[Dict], 
                   search_results: List[Dict] = None) -> Dict:
        """
        Create execution plan based on instruction and available files
        
        Returns:
            {
                "targets": [{"file": "path", "reason": "..."}],
                "actions": [{"type": "code_edit", "description": "...", "files": [...]}],
                "package_installs": ["pip:requests", "npm:axios"],
                "websearch_queries": ["query1", "query2"],
                "run_tests": true/false,
                "test_command": "pytest"
            }
        """
        logger.agent_action("PLANNER", "Creating execution plan")
        
        prompt = self._build_planner_prompt(instruction, files, search_results)
        
        response = self.llm.generate(
            prompt=prompt,
            model=self.config.PLANNER_MODEL,
            temperature=0.3,
            max_tokens=4000
        )
        
        try:
            plan = self._parse_plan(response)
            logger.success(f"Plan created: {len(plan.get('targets', []))} targets, "
                         f"{len(plan.get('actions', []))} actions")
            return plan
        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            return self._empty_plan()
    
    def _build_planner_prompt(self, instruction: str, files: List[Dict],
                             search_results: List[Dict] = None) -> str:
        """Build prompt for planner LLM"""
        
        file_list = "\n".join([
            f"- {f['path']} ({f['lines']} lines, {f['extension']})"
            for f in files[:20]
        ])
        
        search_context = ""
        if search_results:
            search_context = "\n\n## Web Search Results:\n"
            for result in search_results:
                search_context += f"- {result['title']}: {result['snippet']}\n"
        
        prompt = f"""You are an expert AI software architect and planner.

## User Instruction:
{instruction}

## Available Project Files:
{file_list}
{search_context}

## Your Task:
Analyze the instruction and create a detailed execution plan. Output ONLY valid JSON with this exact structure:

{{
  "targets": [
    {{"file": "path/to/file.py", "reason": "why this file needs changes"}}
  ],
  "actions": [
    {{
      "type": "code_edit",
      "description": "what changes to make",
      "files": ["file1.py", "file2.js"]
    }}
  ],
  "package_installs": ["pip:package_name", "npm:package_name"],
  "websearch_queries": ["search query if more info needed"],
  "run_tests": true,
  "test_command": "pytest tests/"
}}

## Rules:
1. Output ONLY valid JSON, no markdown, no explanation
2. Be specific about which files to modify
3. Include package installs if new dependencies are needed
4. Suggest web searches if you need more information
5. Set run_tests to true if changes should be tested
6. If no changes needed, return empty arrays

Generate the plan now:"""
        
        return prompt
    
    def _parse_plan(self, response: str) -> Dict:
        """Parse LLM response into plan dict"""
        # Try to extract JSON from response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        
        # Parse JSON
        plan = json.loads(response)
        
        # Validate structure
        if "targets" not in plan:
            plan["targets"] = []
        if "actions" not in plan:
            plan["actions"] = []
        if "package_installs" not in plan:
            plan["package_installs"] = []
        if "websearch_queries" not in plan:
            plan["websearch_queries"] = []
        if "run_tests" not in plan:
            plan["run_tests"] = False
        
        return plan
    
    def _empty_plan(self) -> Dict:
        """Return empty plan structure"""
        return {
            "targets": [],
            "actions": [],
            "package_installs": [],
            "websearch_queries": [],
            "run_tests": False,
            "test_command": ""
        }
    
    def refine_plan_with_search(self, original_plan: Dict, 
                               search_results: List[Dict],
                               instruction: str) -> Dict:
        """Refine plan based on web search results"""
        logger.agent_action("PLANNER", "Refining plan with search results")
        
        prompt = f"""You previously created this plan:
{json.dumps(original_plan, indent=2)}

For the instruction: {instruction}

Here are web search results that may help:
{json.dumps(search_results, indent=2)}

Based on these search results, refine your plan. Output ONLY valid JSON with the same structure.
If the search results don't change anything, return the original plan.

Refined plan:"""
        
        response = self.llm.generate(
            prompt=prompt,
            model=self.config.PLANNER_MODEL,
            temperature=0.3,
            max_tokens=4000
        )
        
        try:
            return self._parse_plan(response)
        except:
            return original_plan
