"""Worker agent - executes code edits on individual files"""
import json
from typing import Dict, List
from llm import LLMClient
from config import Config
from logger import get_logger

logger = get_logger()

class WorkerAgent:
    """Worker agent that performs actual code edits"""
    
    def __init__(self, config: Config, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
    
    def generate_edits(self, file_path: str, snippet: Dict, 
                      instruction: str, action_description: str) -> Dict:
        """
        Generate code edits for a specific file
        
        Returns:
            {
                "edits": [
                    {
                        "operation": "replace",
                        "match": "old code...",
                        "replacement": "new code..."
                    }
                ]
            }
        """
        logger.agent_action("WORKER", f"Generating edits for {file_path}")
        
        prompt = self._build_worker_prompt(
            file_path, snippet, instruction, action_description
        )
        
        response = self.llm.generate(
            prompt=prompt,
            model=self.config.WORKER_MODEL,
            temperature=0.2,
            max_tokens=6000
        )
        
        try:
            edits = self._parse_edits(response)
            logger.success(f"Generated {len(edits.get('edits', []))} edits")
            return edits
        except Exception as e:
            logger.error(f"Failed to parse edits: {e}")
            return {"edits": []}
    
    def _build_worker_prompt(self, file_path: str, snippet: Dict,
                            instruction: str, action_description: str) -> str:
        """Build prompt for worker LLM"""
        
        from snippet_extractor import SnippetExtractor
        extractor = SnippetExtractor(self.config)
        formatted_snippet = extractor.format_snippet(snippet)
        
        prompt = f"""You are an expert code editor AI.

## File: {file_path}

## Current Code:
{formatted_snippet}

## User Instruction:
{instruction}

## Specific Action:
{action_description}

## Your Task:
Generate precise code edits. Output ONLY valid JSON with this structure:

{{
  "edits": [
    {{
      "operation": "replace",
      "match": "exact code to find and replace (must match exactly)",
      "replacement": "new code to insert"
    }}
  ]
}}

## Rules:
1. Output ONLY valid JSON, no markdown, no explanation, no comments
2. "match" must be EXACT code from the file (copy-paste exactly)
3. Include enough context in "match" to be unique
4. "replacement" should be the complete new code
5. Preserve indentation and formatting
6. If no changes needed, return empty edits array
7. Multiple edits should be independent (don't overlap)

Generate edits now:"""
        
        return prompt
    
    def _parse_edits(self, response: str) -> Dict:
        """Parse LLM response into edits dict"""
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        
        # Parse JSON
        edits = json.loads(response)
        
        # Validate structure
        if "edits" not in edits:
            edits = {"edits": []}
        
        return edits
    
    def validate_edit(self, edit: Dict, file_content: str) -> bool:
        """Validate that an edit can be applied"""
        if edit["operation"] != "replace":
            return False
        
        match_text = edit.get("match", "")
        if not match_text:
            return False
        
        # Check if match exists in file
        if match_text not in file_content:
            logger.warning(f"Match text not found in file")
            return False
        
        # Check if match is unique
        count = file_content.count(match_text)
        if count > 1:
            logger.warning(f"Match text appears {count} times (not unique)")
            return False
        
        return True
