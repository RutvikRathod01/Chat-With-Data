"""
Question decomposition module for handling multi-intent queries.

This module breaks down complex questions into simpler sub-questions that can
be processed independently and then synthesized into a comprehensive answer.
"""

import logging
from typing import List, Dict, Optional, Any

from config.settings import USE_GROQ, USE_GEMINI, GROQ_MODEL, GEMINI_MODEL
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def get_llm():
    """Helper to get the configured LLM."""
    if USE_GEMINI:
        return ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0)
    elif USE_GROQ:
        return ChatGroq(model=GROQ_MODEL, temperature=0.0)
    return None


def analyze_query(question: str) -> List[Dict[str, Any]]:
    """
    Analyze a user query using an LLM to:
    1. Decompose multi-intent questions.
    2. Determine the best retrieval strategy (Exhaustive vs Semantic).
    3. Extract metadata filters (e.g. project names, entities).
    
    This replaces static keyword matching with intelligent understanding.
    """
    # Fast path: simple questions probably don't need LLM
    if len(question.split()) < 5 and "and" not in question.lower():
        # Even for fast path, we return the new structure
        return [{"question": question, "type": "general", "strategy": "semantic", "filters": {}}]

    logging.info("Analyzing query with LLM: %s", question)
    
    try:
        llm = get_llm()
        if not llm:
             # Fallback to basic structure if no LLM
             return [{"question": question, "type": "general", "strategy": "semantic", "filters": {}}]

        prompt = ChatPromptTemplate.from_template(
            """Analyze the following user question for a RAG system.
            
            Tasks:
            1. If it contains multiple distinct questions, break it down.
            2. IMPORTANT: When breaking down questions, resolve pronouns (like "them", "it", "they") 
               by adding context from the original question. For example:
               - "How many projects? Give me names of them" → "How many projects?", "Give me names of the projects"
               - "Who is the lead? What is their role?" → "Who is the lead?", "What is the role of the lead?"
            3. For each question, decide the retrieval strategy:
               - "exhaustive": For "how many", "list all", "summarize all", "what are the projects", or counting/listing queries.
               - "semantic": For specific fact retrieval like "details of Project X", "who is the lead", "what is the budget".
            4. Extract filters ONLY for explicit structural attributes (e.g. "section: budget", "type: table").
               IMPORTANT: Do NOT create metadata filters for 'project', 'person', 'location', or 'date'. 
               These are handled by the search content, not metadata keys. Return empty filters {} for these.
            
            Output strictly JSON:
            {{
                "sub_questions": [
                    {{
                        "question": "text of sub question with pronouns resolved",
                        "type": "count|list|timeline|general",
                        "strategy": "exhaustive|semantic",
                        "filters": {{}}
                    }}
                ]
            }}
            
            User Question: {question}
            """
        )
        
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({"question": question})
        
        sub_questions = result.get("sub_questions", [])
        
        if not sub_questions:
            return [{"question": question, "type": "general", "strategy": "semantic", "filters": {}}]
            
        logging.info("LLM Analysis Result: %s", sub_questions)
        return sub_questions

    except Exception as e:
        logging.error(f"LLM query analysis failed: {e}. Returning default.")
        return [{"question": question, "type": "general", "strategy": "semantic", "filters": {}}]


def decompose_question(question: str) -> List[Dict[str, Any]]:
    """Backward compatibility wrapper."""
    return analyze_query(question)


def detect_multi_intent_question(question: str) -> bool:
    """Deprecated: Logic is now handled by analyze_query."""
    return " and " in question.lower() or "?" in question.replace(question[-1], "")


def extract_document_filter_from_question(question: str) -> Optional[str]:
    """
    Extract document name if the question explicitly mentions a document.
    """
    import re
    question_lower = question.lower()
    
    # Common patterns for document references
    patterns = [
        r'in\s+([a-zA-Z0-9_\-\.]+\.(?:pdf|docx?|xlsx?))',
        r'from\s+([a-zA-Z0-9_\-\.]+\.(?:pdf|docx?|xlsx?))',
        r'(?:document|file)\s+([a-zA-Z0-9_\-\.]+\.(?:pdf|docx?|xlsx?))',
        r'([a-zA-Z0-9_\-\.]+\.(?:pdf|docx?|xlsx?))',  # Just the filename
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            doc_name = match.group(1)
            logging.info("Extracted document filter: %s", doc_name)
            return doc_name
    
    return None


def synthesize_answers(sub_answers: List[Dict[str, str]], original_question: str) -> str:
    """
    Synthesize multiple sub-answers into a coherent response.
    Combines all sub-answers intelligently without losing information.
    """
    if not sub_answers:
        return "No information found for this question."
    
    if len(sub_answers) == 1:
        return sub_answers[0]["answer"]
    
    # Build a structured response
    parts = []
    has_complete_answer = False
    
    for idx, sub_answer in enumerate(sub_answers, 1):
        answer_text = sub_answer.get("answer", "").strip()
        question_type = sub_answer.get("type", "general")
        
        # Skip truly empty answers
        if not answer_text:
            continue
        
        # Check if answer has useful content (not just "not available")
        answer_lower = answer_text.lower()
        is_empty_answer = (
            answer_text == "not available" or 
            answer_text == "Not available" or
            answer_lower == "the information is not available in the provided documents."
        )
        
        # If answer has content beyond "not available", include it
        if not is_empty_answer:
            has_complete_answer = True
            parts.append(answer_text)
        elif len(sub_answers) == 1:
            # If it's the only answer, include it even if empty
            parts.append(answer_text)
    
    if not parts:
        return "The requested information is not available in the provided documents."
    
    # Join with appropriate spacing
    # If we have multiple parts, add line breaks for readability
    if len(parts) > 1:
        result = "\n\n".join(parts)
    else:
        result = parts[0]
    
    return result


__all__ = [
    "detect_multi_intent_question",
    "decompose_question",
    "analyze_query",
    "extract_document_filter_from_question",
    "synthesize_answers",
]
