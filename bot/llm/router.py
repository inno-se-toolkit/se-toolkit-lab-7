"""Intent router using LLM with tools."""
import sys
import json
from typing import Dict, Any, List
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from services.lms_client import LMSClient
from llm.client import LLMClient
from llm.tools import get_tool_definitions


class IntentRouter:
    """Route user intent using LLM with tool calling."""
    
    def __init__(self):
        self.config = load_config()
        self.llm_client = LLMClient(
            self.config.llm_api_base_url,
            self.config.llm_api_key,
            self.config.llm_api_model
        )
        self.lms_client = LMSClient(
            self.config.lms_api_base_url,
            self.config.lms_api_key
        )
        self.tools = get_tool_definitions()
        
        self.system_prompt = """You are a helpful assistant for LMS analytics. You help users query data about labs, scores, and student performance.

You have access to several tools to fetch data from the LMS backend. Always use these tools to answer questions - don't make up data.

IMPORTANT: For questions that require comparing multiple labs (like "which lab has the lowest pass rate"), you MUST:
1. First call get_items() to get all lab names
2. Then call get_pass_rates() for each lab to get their pass rates
3. Compare the results and identify the lab with the lowest pass rate
4. Provide the answer with specific numbers

For questions about specific labs, call get_pass_rates() with the lab name.

When responding:
- Be concise but informative
- Use numbers and percentages when available
- If a lab name is ambiguous, ask for clarification
- If the user asks about something you can't answer, suggest available commands

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Get score distribution for a lab
- get_pass_rates: Get per-task pass rates for a lab (use this for pass rates)
- get_timeline: Get submission timeline
- get_groups: Get per-group performance
- get_top_learners: Get top students
- get_completion_rate: Get completion percentage
- trigger_sync: Refresh data from autochecker

If the user asks a vague question like "lab 4", suggest what they can ask about (scores, pass rates, etc.)."""
    
    async def route(self, message: str) -> str:
        """Route user message to appropriate tool(s)."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Continue until no more tool calls
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = await self.llm_client.chat_completion(
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message_obj = response["choices"][0]["message"]
            
            # If no tool calls, return the content
            if not message_obj.get("tool_calls"):
                return message_obj.get("content", "I'm not sure how to help with that.")
            
            # Execute tool calls
            tool_results = []
            for tool_call in message_obj["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                
                print(f"[tool] LLM called: {tool_name}({arguments})", file=sys.stderr)
                
                # Execute the tool
                result = await self._execute_tool(tool_name, arguments)
                print(f"[tool] Result: {len(str(result))} chars", file=sys.stderr)
                
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # Add assistant message and tool results to conversation
            messages.append(message_obj)
            messages.extend(tool_results)
            
            print(f"[summary] Iteration {iteration}: executed {len(tool_results)} tools", file=sys.stderr)
        
        # If we've reached max iterations, return the last response
        final_response = await self.llm_client.chat_completion(
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        return final_response["choices"][0]["message"].get("content", "Processing completed.")
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool based on its name."""
        
        if tool_name == "get_items":
            return await self.lms_client.get_items()
        
        elif tool_name == "get_learners":
            return await self.lms_client.get_learners()
        
        elif tool_name == "get_scores":
            return await self.lms_client.get_scores(arguments.get("lab"))
        
        elif tool_name == "get_pass_rates":
            data = await self.lms_client.get_pass_rates(arguments.get("lab"))
            # Format for easier comparison
            if isinstance(data, dict) and 'tasks' in data:
                tasks = data['tasks']
                if tasks:
                    total_rate = sum(t.get('avg_score', 0) for t in tasks) / len(tasks)
                    return {
                        "lab": arguments.get("lab"),
                        "average_pass_rate": round(total_rate, 1),
                        "tasks_count": len(tasks)
                    }
            return data
        
        elif tool_name == "get_timeline":
            return await self.lms_client.get_timeline(arguments.get("lab"))
        
        elif tool_name == "get_groups":
            return await self.lms_client.get_groups(arguments.get("lab"))
        
        elif tool_name == "get_top_learners":
            return await self.lms_client.get_top_learners(
                arguments.get("lab"),
                arguments.get("limit", 5)
            )
        
        elif tool_name == "get_completion_rate":
            return await self.lms_client.get_completion_rate(arguments.get("lab"))
        
        elif tool_name == "trigger_sync":
            return await self.lms_client.trigger_sync()
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
