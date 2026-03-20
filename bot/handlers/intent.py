from services.intent_router import IntentRouter
from services.lms_api import LMSAPIClient
from services.llm import LLMClient
from config import LMS_API_URL, LMS_API_KEY, LLM_API_BASE_URL, LLM_API_KEY, LLM_API_MODEL


def handle_intent(user_input: str = "") -> str:
    """Handle natural language input using LLM routing."""
    if not user_input or not user_input.strip():
        return "Please ask me a question about labs, scores, or students."

    try:
        lms_client = LMSAPIClient(LMS_API_URL, LMS_API_KEY)
        llm_client = LLMClient(LLM_API_BASE_URL, LLM_API_KEY, LLM_API_MODEL)
        router = IntentRouter(lms_client, llm_client)
        return router.route(user_input.strip())
    except ConnectionError as e:
        return f"LLM error: {e}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
