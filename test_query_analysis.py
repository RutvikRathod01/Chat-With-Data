"""
Test script to verify query analysis improvements for list/count queries.
"""
import sys
sys.path.insert(0, 'src')

from retrieval.question_decomposition import analyze_query

# Test queries that should trigger exhaustive retrieval
test_queries = [
    "list out all projects name",
    "how many projects are there",
    "what are all the locations mentioned",
    "give me names of all team members",
    "summarize all project budgets",
    "what projects exist",
    "show all timelines",
    # Semantic queries (for comparison)
    "what is the budget of AI-Powered Document Intelligence Platform",
    "who is the project lead",
]

print("=" * 80)
print("Testing Query Analysis")
print("=" * 80)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    result = analyze_query(query)
    for sq in result:
        strategy = sq.get("strategy", "unknown")
        qtype = sq.get("type", "unknown")
        print(f"  → Strategy: {strategy}, Type: {qtype}")
        if strategy == "exhaustive":
            print("  ✓ Correctly classified as EXHAUSTIVE")
        elif strategy == "semantic" and any(kw in query.lower() for kw in ["list", "all", "how many", "what are", "give me"]):
            print("  ✗ WARNING: Should be EXHAUSTIVE but classified as semantic")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
