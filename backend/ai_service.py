import json
import os
import asyncio
import logging
import warnings
from typing import Optional, List, Dict, Any, Callable
from functools import lru_cache
import PIL.Image
import google.generativeai as genai
from async_lru import alru_cache

from backend.retry_utils import exponential_backoff_retry
from backend.exceptions import AIServiceException

# Configure logging
logger = logging.getLogger(__name__)

# Suppress deprecation warnings from google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google.generativeai")

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = "dummy"
    if os.environ.get("ENVIRONMENT") == "production":
         logger.warning("GEMINI_API_KEY not set in production environment!")
else:
    genai.configure(api_key=api_key)

RESPONSIBILITY_MAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "responsibility_map.json")

@lru_cache(maxsize=1)
def _load_responsibility_map() -> dict:
    """Load responsibility map for authority tagging."""
    try:
        with open(RESPONSIBILITY_MAP_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def build_x_post(issue_description: str, category: str) -> str:
    """
    Build an X.com (Twitter) post tagging the relevant authority when available.
    """
    responsibility_map = _load_responsibility_map()
    category_key = str(category).lower().replace(" ", "_")
    authority_info = responsibility_map.get(category_key, {})
    handle = authority_info.get("twitter")

    base_message = f"Reporting a {category} issue: {issue_description[:200]}"
    if handle:
        return f"{base_message} Tagging {handle} for prompt action. #CivicIssue #VishwaGuru"
    return f"{base_message} #CivicIssue #VishwaGuru"

def _get_fallback_action_plan(issue_description: str, category: str) -> dict:
    """Generate fallback action plan when AI is unavailable."""
    return {
        "whatsapp": f"Hello, I would like to report a {category} issue: {issue_description[:150]}",
        "email_subject": f"Complaint regarding {category}",
        "email_body": f"Respected Authority,\n\nI am writing to bring to your attention a {category} issue: {issue_description}.\n\nPlease take necessary action.\n\nSincerely,\nCitizen",
        "x_post": build_x_post(issue_description, category)
    }

@exponential_backoff_retry(max_retries=3, base_delay=1.0, max_delay=10.0)
async def _generate_action_plan_with_retry(issue_description: str, category: str, language: str = 'en') -> dict:
    """
    Internal function that generates action plan with retry logic.
    Raises exception on failure to allow retry decorator to work.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are a civic action assistant. A user has reported a civic issue.
    Category: {category}
    Description: {issue_description}

    Please generate the following messages in {language} language:
    1. A concise WhatsApp message (max 200 chars) that can be sent to authorities.
    2. A formal firm email subject.
    3. A formal email body (max 150 words) addressed to the relevant authority (e.g., Municipal Commissioner, Police, etc. based on category).
    4. A concise X.com post text (max 240 chars).

    Return the response in strictly valid JSON format with keys: "whatsapp", "email_subject", "email_body", "x_post".
    Do not use markdown code blocks. Just the raw JSON string.
    """

    response = await model.generate_content_async(prompt)
    text_response = response.text.strip()

    # Cleanup if markdown code blocks are returned
    if text_response.startswith("```json"):
        text_response = text_response[7:-3]
    elif text_response.startswith("```"):
        text_response = text_response[3:-3]

    text_response = text_response.strip()
    return json.loads(text_response)

async def generate_action_plan(
    issue_description: str,
    category: str,
    *args,
    **kwargs
) -> dict:
    """
    Generates an action plan (WhatsApp message, Email draft, X post) using Gemini with retry logic.
    """
    if not api_key or api_key == "dummy":
        logger.warning("No API key configured, using fallback action plan")
        return _get_fallback_action_plan(issue_description, category)

    language = 'en'
    image_path = None

    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, str) and len(arg) == 2:
            language = arg
        else:
            image_path = arg
    elif len(args) >= 2:
        language = args[0]
        image_path = args[1]

    if 'language' in kwargs:
        language = kwargs['language']
    if 'image_path' in kwargs:
        image_path = kwargs['image_path']

    try:
        plan = await _generate_action_plan_with_retry(issue_description, category, language)
        # Ensure we always have x_post
        if "x_post" not in plan or not plan.get("x_post"):
            plan["x_post"] = build_x_post(issue_description, category)
        return plan
    except Exception as e:
        logger.error(f"Gemini action plan generation failed after retries: {e}")
        return _get_fallback_action_plan(issue_description, category)

@exponential_backoff_retry(max_retries=3, base_delay=1.0, max_delay=10.0)
async def _chat_with_civic_assistant_with_retry(query: str, history_context: str = "") -> str:
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are VishwaGuru, a helpful civic assistant for Indian citizens.
    {history_context}
    User Query: {query}

    Answer the user's question about civic issues, government services, or local administration.
    If they ask about specific MLAs, tell them to use the "Find My MLA" feature.
    Keep answers concise and helpful.
    """

    response = await model.generate_content_async(prompt)
    return response.text.strip()

@alru_cache(maxsize=100)
async def chat_with_civic_assistant(query: str, history: Optional[List[dict]] = None) -> str:
    """
    Chat with the civic assistant.
    Includes retry logic with exponential backoff for transient failures.
    """
    if not api_key or api_key == "dummy":
        logger.warning("No API key configured, chat assistant offline")
        return "I am currently offline. Please try again later."

    history_context = ""
    if history:
        history_context = "Previous conversation:\n"
        for msg in history[-5:]:  # Keep last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_context += f"{role}: {content}\n"

    try:
        return await _chat_with_civic_assistant_with_retry(query, history_context)
    except Exception as e:
        logger.error(f"Gemini Chat Error after all retries: {e}", exc_info=True)
        return "I encountered an error processing your request. Please try again later."

async def analyze_issue_image(image_path: str) -> Dict[str, Any]:
    """
    Analyzes an image to detect the civic issue, category, and severity.
    """
    if not api_key or api_key == "dummy":
        return {
            "description": "AI analysis unavailable",
            "category": "Uncategorized",
            "severity": "Unknown"
        }

    try:
        if not os.path.exists(image_path):
             return {"error": "Image file not found"}

        img = PIL.Image.open(image_path)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analyze this image of a civic issue.
        Identify:
        1. A short description of the issue.
        2. The category (e.g., Pothole, Garbage, Flooding, Vandalism, Street Light, etc.).
        3. The severity (Low, Medium, High).

        Return valid JSON with keys: "description", "category", "severity".
        Do not use markdown code blocks. Just the raw JSON string.
        """

        response = await model.generate_content_async([prompt, img])
        text_response = response.text.strip()

        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        elif text_response.startswith("```"):
            text_response = text_response[3:-3]

        return json.loads(text_response)

    except Exception as e:
        logger.error(f"Gemini Image Analysis Error: {e}", exc_info=True)
        return {
            "description": "Could not analyze image",
            "category": "Unknown",
            "severity": "Unknown"
        }

async def analyze_issue_with_ai(description: str, image_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes an issue description and optional image.
    """
    if not api_key or api_key == "dummy":
        return {
             "category": "General",
             "severity": "Medium",
             "authority": "Local Municipal Corporation",
             "action_plan": "Report to local ward office."
        }

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        content = []
        prompt_text = f"""
        Analyze this civic issue report.
        Description: {description}

        Determine:
        1. The most appropriate Category.
        2. Severity Level (Low, Medium, High).
        3. Responsible Authority in India (e.g., BMC, Police, MSEB, etc.).
        4. A recommended Action Plan (short sentence).

        Return valid JSON with keys: "category", "severity", "authority", "action_plan".
        Do not use markdown code blocks. Just the raw JSON string.
        """
        content.append(prompt_text)

        if image_path and os.path.exists(image_path):
            img = PIL.Image.open(image_path)
            content.append(img)

        response = await model.generate_content_async(content)
        text_response = response.text.strip()

        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        elif text_response.startswith("```"):
            text_response = text_response[3:-3]

        return json.loads(text_response)

    except Exception as e:
        logger.error(f"Gemini Analysis Error: {e}", exc_info=True)
        return {
             "category": "General",
             "severity": "Medium",
             "authority": "Local Authority",
             "action_plan": "Please visit the nearest municipal office."
        }
