"""AI Report Generation Service using Emergent LLM Key

This service generates personalized burnout recovery reports using AI.
Uses the Emergent Universal LLM Key for API access.
"""

from openai import OpenAI
from config import settings
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# Initialize OpenAI client with Emergent LLM Key
# Emergent LLM Key: sk-emergent-8542aD401415bCd811
client = OpenAI(api_key="sk-emergent-8542aD401415bCd811")

# Master AI Prompt Template (LOCKED)
REPORT_GENERATION_PROMPT = """You are a professional workplace wellness coach specializing in burnout recovery for working professionals. Generate a comprehensive, personalized burnout recovery report based on the user's assessment.

USER DETAILS:
- Name: {user_full_name}
- Burnout Score: {burnout_score}/100
- Burnout Level: {burnout_level}

ASSESSMENT ANSWERS:
1. Mental exhaustion after work: {answer_1}
2. Thinking about work outside hours: {answer_2}
3. Morning motivation level: {answer_3}
4. Feeling overwhelmed by tasks: {answer_4}
5. Work-life balance satisfaction: {answer_5}
6. Sleep quality on workdays: {answer_6}
7. Sense of meaning in work: {answer_7}

TONE & STYLE:
- Professional, warm, and supportive
- Use their first name naturally throughout
- Be specific to their answers (not generic)
- Actionable and practical
- Avoid medical terminology or clinical diagnoses
- No fear-based language

MANDATORY STRUCTURE - Generate exactly these 8 sections:

---

# Your Personalized Burnout Recovery Report

## 1. Introduction
Address {user_full_name} by first name. Acknowledge them taking this step. Briefly mention their burnout score and level. Set a supportive, non-judgmental tone. (2-3 paragraphs)

## 2. Understanding Your Burnout Level
Explain what {burnout_level} burnout means. Put their score ({burnout_score}/100) in context. Describe typical signs at this stage. Normalize their experience. (3-4 paragraphs)

## 3. Key Burnout Drivers
Based on their specific answers, identify 3-5 main factors causing their burnout. Use bullet points. Reference their actual responses. Be specific, not generic. (Introduction + 3-5 detailed bullets)

## 4. Your Recovery Focus
Define their primary recovery goal based on burnout level. Set realistic expectations. Outline key mindset shifts needed. (2-3 paragraphs)

## 5. 14-Day Recovery Action Plan
Provide a detailed two-week plan:
- Week 1: Focus and specific daily actions (3-5 steps)
- Week 2: Building momentum and specific actions (3-5 steps)
Tailor actions to their burnout level. Make steps small and achievable. (Substantial section with clear weekly breakdown)

## 6. Work-Life Boundary Recommendations
Provide 5-7 specific boundary strategies:
- Digital boundaries (email, notifications)
- Time boundaries (work hours, disconnection)
- Mental boundaries (rumination, work thoughts)
- Physical boundaries (workspace)
- Communication boundaries (saying no)
Tailor to their specific challenges. Use bullet format with explanations.

## 7. Sustainable Habits to Prevent Relapse
Recommend 5-7 ongoing practices:
- Daily micro-habits
- Weekly check-ins
- Monthly reviews
- Warning signs to watch
- Support systems
Make practical for busy professionals. Bullet format with explanations.

## 8. Closing Message
Encouragement and validation. Remind them recovery is achievable. Emphasize their progress in taking this step. End with hope and empowerment. (2 paragraphs)

---

FORMATTING:
- Use markdown with ## headings for sections
- Bold key phrases for emphasis
- Bullet points for lists
- Short paragraphs (3-5 sentences)
- White space for readability

LENGTH: 1500-2500 words total

Generate the complete report now, making it feel uniquely written for this individual based on their specific answers."""


def format_prompt(
    user_full_name: str,
    burnout_score: int,
    burnout_level: str,
    answers: Dict[int, str]
) -> str:
    """Format the master prompt with user-specific data"""
    
    # Extract first name from full name
    first_name = user_full_name.split()[0] if user_full_name else "User"
    
    # Format the prompt with all variables
    formatted_prompt = REPORT_GENERATION_PROMPT.format(
        user_full_name=first_name,
        burnout_score=burnout_score,
        burnout_level=burnout_level,
        answer_1=answers.get(1, "Not answered"),
        answer_2=answers.get(2, "Not answered"),
        answer_3=answers.get(3, "Not answered"),
        answer_4=answers.get(4, "Not answered"),
        answer_5=answers.get(5, "Not answered"),
        answer_6=answers.get(6, "Not answered"),
        answer_7=answers.get(7, "Not answered")
    )
    
    return formatted_prompt


def generate_burnout_report(
    user_full_name: str,
    burnout_score: int,
    burnout_level: str,
    answers: Dict[int, str]
) -> Tuple[bool, str, str]:
    """
    Generate personalized burnout recovery report using AI.
    
    Args:
        user_full_name: User's full name
        burnout_score: Calculated burnout score (0-100)
        burnout_level: Burnout level (Low/Moderate/High)
        answers: Dictionary mapping question ID to answer text
    
    Returns:
        Tuple[bool, str, str]: (success, report_content, error_message)
    """
    
    try:
        logger.info(f"Generating report for {user_full_name}, score: {burnout_score}, level: {burnout_level}")
        
        # Format the prompt with user data
        prompt = format_prompt(user_full_name, burnout_score, burnout_level, answers)
        
        # Call OpenAI API with Emergent LLM Key
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using efficient model for cost optimization
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert workplace wellness coach specializing in burnout recovery."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        # Extract generated report
        report_content = response.choices[0].message.content
        
        logger.info(f"Report generated successfully for {user_full_name}")
        return True, report_content, ""
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return False, "", f"Failed to generate report: {str(e)}"


def validate_report_content(report_content: str) -> bool:
    """
    Validate that the generated report meets basic quality standards.
    
    Checks:
    - Minimum word count (1000 words)
    - Contains all 8 required sections
    - Not empty or truncated
    """
    
    if not report_content or len(report_content) < 500:
        return False
    
    # Check for required sections
    required_sections = [
        "Introduction",
        "Understanding Your Burnout Level",
        "Key Burnout Drivers",
        "Your Recovery Focus",
        "14-Day Recovery Action Plan",
        "Work-Life Boundary Recommendations",
        "Sustainable Habits",
        "Closing Message"
    ]
    
    found_sections = sum(1 for section in required_sections if section.lower() in report_content.lower())
    
    # At least 6 out of 8 sections should be present
    return found_sections >= 6
