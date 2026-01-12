"""
Answer validation and context completeness checking.

This module provides guardrails to detect when retrieved context might be incomplete
and warns users appropriately to avoid overconfident wrong answers.
"""

import logging
import re
from typing import List, Dict, Optional

from config.settings import USE_GROQ, USE_GEMINI, GROQ_MODEL, GEMINI_MODEL
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def get_llm():
    """Helper to get the configured LLM for validation."""
    if USE_GEMINI:
        return ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0)
    elif USE_GROQ:
        return ChatGroq(model=GROQ_MODEL, temperature=0.0)
    return None


def is_counting_question(question: str) -> bool:
    """
    DEPRECATED: Use validate_answer_with_llm() instead.
    
    Legacy regex-based detection kept for backward compatibility only.
    New code should use LLM-based validation which understands paraphrases.
    """
    question_lower = question.lower()
    
    # Generic patterns that work across all domains
    counting_patterns = [
        r'\bhow many\b',
        r'\bcount\b',
        r'\bnumber of\b',
        r'\bhow much\b',
        r'\blist all\b',
        r'\bwhat are all\b',
        r'\benumerate\b',
        r'\btotal\b',
        r'\ball\b.*\b(the|of)\b',  # "all the" or "all of" patterns
    ]
    
    for pattern in counting_patterns:
        if re.search(pattern, question_lower):
            return True
    
    return False


def validate_answer_with_llm(
    question: str, 
    answer: str, 
    context_entries: List[Dict], 
    retrieval_mode: str = "semantic"
) -> Dict:
    """
    Use LLM to dynamically validate answer quality and completeness.
    
    This replaces static heuristics with intelligent analysis that:
    - Understands paraphrased questions
    - Detects semantic incompleteness
    - Adapts to different document types
    - Provides reasoning for debugging
    
    Args:
        question: User's original question
        answer: Generated answer text
        context_entries: Retrieved context chunks
        retrieval_mode: 'semantic' or 'exhaustive'
        
    Returns:
        Dictionary with validation results and suggested warnings
    """
    try:
        llm = get_llm()
        if not llm:
            logging.warning("No LLM available for answer validation, falling back to heuristic")
            return validate_context_completeness(question, context_entries, answer, retrieval_mode)
        
        # Extract document information
        documents_seen = set()
        for entry in context_entries:
            doc = entry.get("doc")
            if doc and doc.metadata:
                doc_name = doc.metadata.get("document_name")
                if doc_name:
                    documents_seen.add(doc_name)
        
        num_documents = len(documents_seen)
        num_chunks = len(context_entries)
        doc_list = list(documents_seen) if documents_seen else ["unknown"]
        
        # Get a sample of context to help LLM understand what was retrieved
        context_sample = ""
        if context_entries:
            sample_chunks = context_entries[:3]  # First 3 chunks
            context_sample = "\n".join([
                f"- {entry['doc'].page_content[:150]}..." 
                for entry in sample_chunks if entry.get('doc')
            ])
        
        prompt = ChatPromptTemplate.from_template(
            """You are an answer quality validator for a RAG (Retrieval-Augmented Generation) system.

Task: Evaluate if the generated answer adequately addresses the user's question given the available context.

User Question: {question}

Generated Answer: {answer}

Context Information:
- Retrieved Chunks: {num_chunks}
- Source Documents: {num_documents} ({doc_list})
- Retrieval Mode: {retrieval_mode}

Sample Context (first 3 chunks):
{context_sample}

Analyze:
1. Does the answer directly address what the user asked?
2. For list/count/enumeration queries: Are all items included or is the count complete?
3. For multi-document queries: Is coverage comprehensive across relevant documents?
4. Are there indicators of uncertainty or missing information in the answer?
5. Does the retrieved context seem sufficient for a complete answer?
6. Are there obvious gaps or limitations?

Consider:
- Paraphrased requests (e.g., "enumerate all" = "list all" = "give me every")
- Implicit multi-document needs (e.g., "project costs" when multiple projects exist)
- Context limitations vs answer limitations

Output JSON (no markdown):
{{
    "is_complete": true/false,
    "confidence": "high|medium|low",
    "reasoning": "2-3 sentence explanation of assessment",
    "missing_aspects": ["aspect1", "aspect2"] or [],
    "suggested_warning": "user-facing warning message" or null,
    "num_chunks": {num_chunks},
    "num_documents": {num_documents}
}}"""
        )
        
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "question": question,
            "answer": answer,
            "num_chunks": num_chunks,
            "num_documents": num_documents,
            "doc_list": ", ".join(doc_list[:5]),  # Limit to 5 doc names
            "retrieval_mode": retrieval_mode,
            "context_sample": context_sample or "No context retrieved"
        })
        
        # Ensure backward compatibility with expected fields
        validation_result = {
            "is_complete": result.get("is_complete", True),
            "confidence": result.get("confidence", "medium"),
            "warning": result.get("suggested_warning"),
            "reasoning": result.get("reasoning", ""),
            "missing_aspects": result.get("missing_aspects", []),
            "num_chunks": num_chunks,
            "num_documents": num_documents
        }
        
        logging.info("LLM validation: is_complete=%s, confidence=%s, reasoning=%s", 
                    validation_result["is_complete"], 
                    validation_result["confidence"],
                    validation_result["reasoning"][:100])
        
        return validation_result
        
    except Exception as e:
        logging.error(f"LLM answer validation failed: {e}. Falling back to heuristic validation.")
        return validate_context_completeness(question, context_entries, answer, retrieval_mode)


def validate_context_completeness(question: str, context_entries: List[Dict], answer: str, retrieval_mode: str = "semantic") -> Dict:
    """
    LEGACY: Heuristic-based validation (fallback only).
    
    Use validate_answer_with_llm() for production - it's more accurate.
    This function is kept as a fallback when LLM is unavailable.
    
    Args:
        question: User's question
        context_entries: Retrieved context chunks
        answer: Generated answer text
        retrieval_mode: 'semantic' or 'exhaustive' - affects validation threshold
        
    Returns:
        Dictionary with:
        - is_complete: bool indicating if context seems complete
        - warning: Optional warning message to append
        - confidence: "high", "medium", or "low"
    """
    if not is_counting_question(question):
        # For non-counting questions, assume context is adequate
        return {
            "is_complete": True,
            "warning": None,
            "confidence": "high"
        }
    
    # For counting questions, analyze context coverage
    if not context_entries:
        return {
            "is_complete": False,
            "warning": "⚠️ No relevant context was found. This answer may be incomplete.",
            "confidence": "low"
        }
    
    # Check document distribution
    documents_seen = set()
    for entry in context_entries:
        doc = entry.get("doc")
        if doc and doc.metadata:
            doc_name = doc.metadata.get("document_name")
            if doc_name:
                documents_seen.add(doc_name)
    
    num_documents = len(documents_seen)
    num_chunks = len(context_entries)
    
    logging.info("Context validation: %d chunks from %d documents", num_chunks, num_documents)
    
    # Heuristics for completeness
    confidence = "high"
    warning = None
    is_complete = True
    
    # Check 1: Limited context chunks (adaptive threshold)
    # Use lower threshold for exhaustive mode since it retrieves all matching chunks
    threshold = 2 if retrieval_mode == "exhaustive" else 3
    
    if num_chunks < threshold:
        confidence = "medium"
        warning = "Note: Retrieved context is limited. If you expected more results, try rephrasing your question."
        is_complete = False
    
    # Check 2: Answer indicates uncertainty
    answer_lower = answer.lower()
    uncertainty_indicators = [
        "may not be complete",
        "might be",
        "appears to be",
        "seems to be",
        "not sure",
        "unclear",
        "may be missing",
    ]
    
    if any(indicator in answer_lower for indicator in uncertainty_indicators):
        confidence = "medium"
        if not warning:
            warning = "Note: The answer indicates some uncertainty. Consider refining your question."
    
    # Check 3: For multi-document queries, ensure we got context from multiple docs
    question_lower = question.lower()
    mentions_multiple = any(word in question_lower for word in ["both", "all", "multiple", "each", "every"])
    
    if mentions_multiple and num_documents < 2:
        confidence = "low"
        warning = "⚠️ Question asks about multiple documents, but context was retrieved from only one. Answer may be incomplete."
        is_complete = False
    
    # Check 4: Check if answer says "not available" but we have context
    if "not available" in answer_lower and num_chunks > 0:
        # This might be a false negative - context was found but didn't contain the answer
        confidence = "medium"
    
    return {
        "is_complete": is_complete,
        "warning": warning,
        "confidence": confidence,
        "num_chunks": num_chunks,
        "num_documents": num_documents
    }


def append_validation_warning(answer: str, validation_result: Dict) -> str:
    """
    Append validation warning to answer if needed.
    
    Args:
        answer: Original answer text
        validation_result: Result from validate_context_completeness
        
    Returns:
        Answer with optional warning appended
    """
    warning = validation_result.get("warning")
    
    if warning:
        # Add a line break before the warning
        return f"{answer}\n\n{warning}"
    
    return answer


__all__ = [
    "is_counting_question",
    "validate_context_completeness",
    "validate_answer_with_llm",
    "append_validation_warning",
]
