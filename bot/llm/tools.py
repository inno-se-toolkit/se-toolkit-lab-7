"""Tool definitions for LLM."""
from typing import Dict, Any, List


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get all tool definitions for LLM."""
    
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get all items (labs and tasks) from the LMS",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled students and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution for a lab (4 buckets: 0-25, 25-50, 50-75, 75-100%)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                        }
                    },
                    "required": ["lab"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                        }
                    },
                    "required": ["lab"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline (submissions per day) for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                        }
                    },
                    "required": ["lab"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group performance data for a lab (scores and student counts)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                        }
                    },
                    "required": ["lab"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["lab"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                        }
                    },
                    "required": ["lab"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL sync to refresh data from autochecker",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]


# Map tool names to actual functions (will be implemented in router)
TOOL_HANDLERS = {
    "get_items": "get_items",
    "get_learners": "get_learners",
    "get_scores": "get_scores",
    "get_pass_rates": "get_pass_rates",
    "get_timeline": "get_timeline",
    "get_groups": "get_groups",
    "get_top_learners": "get_top_learners",
    "get_completion_rate": "get_completion_rate",
    "trigger_sync": "trigger_sync",
}

