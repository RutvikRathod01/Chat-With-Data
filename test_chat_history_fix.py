"""
Test script to verify chat history is properly passed to question decomposition.
"""

from src.retrieval.question_decomposition import analyze_query

# Simulate a conversation where user asks follow-up with pronouns
chat_history = [
    {"role": "user", "content": "what is timeline of AI-Powered Document project?"},
    {"role": "assistant", "content": "The timeline for the AI-Powered Document Intelligence Platform project is 5 months."}
]

# User's follow-up question with pronoun "it"
follow_up_question = "give me Objective and keyStakeholders of it"

print("=" * 80)
print("Testing Question Decomposition with Chat History")
print("=" * 80)
print("\nChat History:")
for msg in chat_history:
    print(f"  {msg['role']}: {msg['content'][:80]}...")

print(f"\nFollow-up Question: {follow_up_question}")
print("\n" + "=" * 80)

# Analyze the question WITH chat history
result_with_history = analyze_query(
    question=follow_up_question,
    available_documents=["Project_Budget_Timeline_Locations.pdf"],
    chat_history=chat_history
)

print("\nResult WITH chat history:")
for i, sub_q in enumerate(result_with_history, 1):
    print(f"\n  Sub-question {i}:")
    print(f"    Question: {sub_q['question']}")
    print(f"    Strategy: {sub_q['strategy']}")
    print(f"    Type: {sub_q['type']}")

# Compare to WITHOUT chat history (old behavior)
print("\n" + "=" * 80)
result_without_history = analyze_query(
    question=follow_up_question,
    available_documents=["Project_Budget_Timeline_Locations.pdf"],
    chat_history=None
)

print("\nResult WITHOUT chat history (for comparison):")
for i, sub_q in enumerate(result_without_history, 1):
    print(f"\n  Sub-question {i}:")
    print(f"    Question: {sub_q['question']}")
    print(f"    Strategy: {sub_q['strategy']}")
    print(f"    Type: {sub_q['type']}")

print("\n" + "=" * 80)
print("\nExpected Improvement:")
print("  WITH history should resolve 'it' to 'AI-Powered Document project'")
print("  WITHOUT history will keep generic 'the project' reference")
print("=" * 80)
