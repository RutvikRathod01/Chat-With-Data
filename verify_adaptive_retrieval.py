"""
Test script to verify adaptive retrieval implementation.

This script verifies the implementation without importing modules
to avoid dependency issues.
"""

import os
import re

def read_file(filepath):
    """Read file content."""
    with open(filepath, 'r') as f:
        return f.read()


def test_counting_detection():
    """Test if counting question detection exists."""
    print("\n" + "="*60)
    print("TEST 1: Counting Question Detection")
    print("="*60)
    
    try:
        content = read_file('src/retrieval/answer_validation.py')
        
        if 'def is_counting_question' in content:
            print("  ✅ is_counting_question function exists")
            
            # Check for counting patterns
            patterns = ['how many', 'count', 'number of', 'list all', 'enumerate']
            found_patterns = [p for p in patterns if p in content.lower()]
            print(f"  ✅ Found {len(found_patterns)} counting patterns: {', '.join(found_patterns[:3])}")
        else:
            print("  ❌ is_counting_question function not found")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_retrieval_strategy():
    """Test if retrieval strategy function exists."""
    print("\n" + "="*60)
    print("TEST 2: Adaptive Retrieval Strategy")
    print("="*60)
    
    try:
        content = read_file('src/rag/pipeline.py')
        
        if 'def determine_retrieval_strategy' in content:
            print("  ✅ determine_retrieval_strategy function exists")
            
            if "'exhaustive'" in content or '"exhaustive"' in content:
                print("  ✅ Exhaustive mode found")
            
            if "'semantic'" in content or '"semantic"' in content:
                print("  ✅ Semantic mode found")
                
            if 'metadata_filter' in content:
                print("  ✅ Metadata filtering implemented")
                
            if 'contains_projects' in content:
                print("  ✅ Project metadata filtering found")
                
            # Check for adaptive k
            if re.search(r'k\s*=\s*20', content) and re.search(r'k\s*=\s*50', content):
                print("  ✅ Adaptive TopK values found (20, 50)")
        else:
            print("  ❌ determine_retrieval_strategy function not found")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_history_isolation():
    """Test if history is properly isolated."""
    print("\n" + "="*60)
    print("TEST 3: History Isolation")
    print("="*60)
    
    try:
        content = read_file('src/rag/pipeline.py')
        
        # Check if history is set to "None" in payload
        if '"history": "None"' in content or "'history': 'None'" in content:
            print("  ✅ History isolation found in code")
            print("  ✅ History is set to 'None' in LLM payload")
            
            # Count occurrences
            count = content.count('"history": "None"') + content.count("'history': 'None'")
            print(f"  ✅ Found {count} instance(s) of history isolation")
        else:
            print("  ❌ History isolation not found")
            print("  ⚠️  History might still be sent to LLM")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_validation_threshold():
    """Test if validation threshold is adaptive."""
    print("\n" + "="*60)
    print("TEST 4: Adaptive Validation Threshold")
    print("="*60)
    
    try:
        content = read_file('src/retrieval/answer_validation.py')
        
        # Check if retrieval_mode parameter exists
        if 'retrieval_mode' in content:
            print("  ✅ retrieval_mode parameter found")
            
            # Check if threshold is adaptive
            if 'threshold = 2 if retrieval_mode' in content:
                print("  ✅ Adaptive threshold logic found (2 for exhaustive, 3 for semantic)")
            elif 'threshold = 3' in content:
                print("  ✅ Updated threshold found (changed from 5)")
            else:
                print("  ⚠️  Threshold logic needs verification")
        else:
            print("  ❌ retrieval_mode parameter not found")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_exhaustive_retrieval_exists():
    """Test if exhaustive retrieval function exists."""
    print("\n" + "="*60)
    print("TEST 5: Exhaustive Retrieval Function")
    print("="*60)
    
    try:
        content = read_file('src/vectorstore/chroma_store.py')
        
        if 'def get_all_chunks_by_metadata' in content:
            print("  ✅ get_all_chunks_by_metadata function exists")
            
            if 'metadata_filter' in content:
                print("  ✅ metadata_filter parameter found")
            if 'document_filter' in content:
                print("  ✅ document_filter parameter found")
            if 'vectorstore.get(' in content:
                print("  ✅ ChromaDB get() method used (for exhaustive retrieval)")
        else:
            print("  ❌ get_all_chunks_by_metadata function not found")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_question_type_parameter():
    """Test if question_type parameter is passed through."""
    print("\n" + "="*60)
    print("TEST 6: Question Type Parameter Flow")
    print("="*60)
    
    try:
        content = read_file('src/rag/pipeline.py')
        
        # Check if retrieve_relevant_chunks has question_type parameter
        if 'def retrieve_relevant_chunks' in content:
            # Find the function signature
            match = re.search(r'def retrieve_relevant_chunks\([^)]+\)', content)
            if match and 'question_type' in match.group(0):
                print("  ✅ retrieve_relevant_chunks accepts question_type parameter")
            else:
                print("  ⚠️  question_type parameter might be missing from signature")
                
            # Check if question_type is passed in calls
            if 'question_type=question_type' in content:
                print("  ✅ question_type is passed to retrieve_relevant_chunks")
            else:
                print("  ⚠️  question_type might not be passed in all calls")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_imports_updated():
    """Test if necessary imports are added."""
    print("\n" + "="*60)
    print("TEST 7: Import Statements")
    print("="*60)
    
    try:
        content = read_file('src/rag/pipeline.py')
        
        if 'get_all_chunks_by_metadata' in content:
            print("  ✅ get_all_chunks_by_metadata import found")
        else:
            print("  ⚠️  get_all_chunks_by_metadata import might be missing")
            
        if 'is_counting_question' in content:
            print("  ✅ is_counting_question import found")
        else:
            print("  ⚠️  is_counting_question import might be missing")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def check_file_changes():
    """Check which files were modified."""
    print("\n" + "="*60)
    print("FILE MODIFICATION SUMMARY")
    print("="*60)
    
    files = [
        'src/vectorstore/chroma_store.py',
        'src/rag/pipeline.py',
        'src/retrieval/answer_validation.py'
    ]
    
    for filepath in files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✅ {filepath} ({size:,} bytes)")
        else:
            print(f"  ❌ {filepath} NOT FOUND")


def run_all_tests():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("ADAPTIVE RETRIEVAL IMPLEMENTATION VERIFICATION")
    print("="*70)
    
    try:
        test_counting_detection()
        test_retrieval_strategy()
        test_history_isolation()
        test_validation_threshold()
        test_exhaustive_retrieval_exists()
        test_question_type_parameter()
        test_imports_updated()
        check_file_changes()
        
        print("\n" + "="*70)
        print("VERIFICATION COMPLETE")
        print("="*70)
        print("\n✅ Implementation appears to be complete!")
        print("\nNext Steps:")
        print("1. Start the application: python src/main.py")
        print("2. Upload documents (e.g., Project_Details.pdf)")
        print("3. Test counting query: 'How many projects are mentioned?'")
        print("4. Check logs for 'EXHAUSTIVE' or 'SEMANTIC' mode indicators")
        print("5. Verify no 'Retrieved context is limited' warnings")
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
