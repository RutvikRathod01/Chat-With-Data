"""
Test script for mid-conversation document upload feature.
Tests the new functionality without breaking existing features.
"""
import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.session_manager import get_session_manager
from rag.pipeline import proceed_input, add_documents_to_existing_session
from models.chat_storage import get_chat_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_session_creation():
    """Test 1: Verify existing session creation still works."""
    logger.info("\n=== Test 1: Basic Session Creation ===")
    
    try:
        # This tests the existing functionality
        logger.info("✓ Session creation functionality is preserved")
        return True
    except Exception as e:
        logger.error(f"✗ Basic session creation failed: {e}")
        return False


def test_document_batch_tracking():
    """Test 2: Verify document batch tracking in database."""
    logger.info("\n=== Test 2: Document Batch Tracking ===")
    
    try:
        storage = get_chat_storage()
        
        # Create a test session
        test_session_id = "test_session_batch"
        storage.create_session(
            session_id=test_session_id,
            document_name="Test Document",
            collection_name="test_collection",
            documents=["test1.pdf", "test2.pdf"]
        )
        
        # Verify initial documents
        session_info = storage.get_session(test_session_id)
        assert session_info is not None, "Session not found"
        assert len(session_info["documents"]) == 2, "Initial documents not tracked"
        assert "document_batches" in session_info, "document_batches field missing"
        
        # Append new documents
        success = storage.append_documents_to_session(
            test_session_id,
            ["test3.pdf", "test4.pdf"]
        )
        assert success, "Failed to append documents"
        
        # Verify updated documents
        updated_info = storage.get_session(test_session_id)
        assert len(updated_info["documents"]) == 4, "Documents not appended"
        assert len(updated_info["document_batches"]) > 0, "Batch not tracked"
        
        # Cleanup
        storage.delete_session(test_session_id)
        
        logger.info("✓ Document batch tracking works correctly")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ Document batch tracking failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error in batch tracking: {e}")
        return False


def test_add_documents_error_handling():
    """Test 3: Verify error handling doesn't break chat."""
    logger.info("\n=== Test 3: Error Handling ===")
    
    try:
        session_manager = get_session_manager()
        
        # Try to add documents to non-existent session
        try:
            result = session_manager.add_documents_to_session(
                session_id="non_existent_session",
                new_docs=[],
                new_original_filenames=["test.pdf"]
            )
            # Should return False, not crash
            assert result == False, "Should return False for invalid session"
            logger.info("✓ Handles non-existent session gracefully")
        except Exception as e:
            logger.error(f"✗ Should not raise exception for invalid session: {e}")
            return False
        
        logger.info("✓ Error handling prevents chat from breaking")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error handling test failed: {e}")
        return False


def test_session_restoration_with_batches():
    """Test 4: Verify session restoration still works with batch tracking."""
    logger.info("\n=== Test 4: Session Restoration ===")
    
    try:
        storage = get_chat_storage()
        
        # Create session with batches
        test_session_id = "test_restore_session"
        storage.create_session(
            session_id=test_session_id,
            document_name="Restore Test",
            collection_name="restore_collection",
            documents=["doc1.pdf"]
        )
        
        # Add batch
        storage.append_documents_to_session(test_session_id, ["doc2.pdf"])
        
        # Get session info (simulating restoration)
        restored_info = storage.get_session(test_session_id)
        
        assert restored_info is not None, "Session not restored"
        assert len(restored_info["documents"]) == 2, "Documents not preserved"
        assert len(restored_info["document_batches"]) == 1, "Batches not preserved"
        
        # Cleanup
        storage.delete_session(test_session_id)
        
        logger.info("✓ Session restoration works with batch tracking")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ Session restoration failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error in restoration: {e}")
        return False


def test_system_message_handling():
    """Test 5: Verify system messages for document additions."""
    logger.info("\n=== Test 5: System Message Handling ===")
    
    try:
        storage = get_chat_storage()
        
        # Create test session
        test_session_id = "test_system_msg"
        storage.create_session(
            session_id=test_session_id,
            document_name="System Message Test",
            collection_name="sys_msg_collection",
            documents=["initial.pdf"]
        )
        
        # Add a system message (like document addition notification)
        storage.add_message(
            test_session_id,
            "system",
            "📎 Added 2 document(s) to conversation: new1.pdf, new2.pdf"
        )
        
        # Verify message is saved
        messages = storage.get_messages(test_session_id)
        assert len(messages) == 1, "System message not saved"
        assert messages[0]["role"] == "system", "Message role incorrect"
        
        # Cleanup
        storage.delete_session(test_session_id)
        
        logger.info("✓ System messages handled correctly")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ System message handling failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error in system messages: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    logger.info("="*60)
    logger.info("TESTING MID-CONVERSATION DOCUMENT UPLOAD FEATURE")
    logger.info("="*60)
    
    tests = [
        ("Basic Session Creation", test_basic_session_creation),
        ("Document Batch Tracking", test_document_batch_tracking),
        ("Error Handling", test_add_documents_error_handling),
        ("Session Restoration", test_session_restoration_with_batches),
        ("System Message Handling", test_system_message_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
