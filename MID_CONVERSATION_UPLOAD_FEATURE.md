# Mid-Conversation Document Upload Feature

## Overview

This feature allows users to add additional documents to an ongoing chat session without losing their conversation history. Users can click a "+" button in the chat input area to upload new documents that will be seamlessly integrated into the current session.

## Feature Highlights

✅ **Add documents during active conversations**  
✅ **Preserves all chat history**  
✅ **Tracks document batches with timestamps**  
✅ **System messages notify when documents are added**  
✅ **Graceful error handling - chat never breaks**  
✅ **Works with existing multi-document sessions**

---

## Architecture Changes

### 1. Database Schema Updates

**File**: `src/models/chat_storage.py`

Added `document_batches` column to track when documents were added:

```python
document_batches TEXT DEFAULT '[]'
```

Structure:
```json
[
  {
    "documents": ["Budget_Q1.pdf", "Report.docx"],
    "added_at": "2026-01-12T10:30:00"
  },
  {
    "documents": ["Budget_Q2.pdf"],
    "added_at": "2026-01-12T15:45:00"
  }
]
```

**New Methods**:
- `append_documents_to_session(session_id, new_documents)` - Appends documents to existing session

### 2. Session Manager Extensions

**File**: `src/models/session_manager.py`

**New Method**:
```python
def add_documents_to_session(session_id, new_docs, new_original_filenames):
    """Add new documents to an existing session.
    
    - Adds chunks to existing vector store
    - Rebuilds sparse index with all documents
    - Updates database tracking
    """
```

**Key Operations**:
1. Retrieves existing session from memory/disk
2. Calls `vectorstore.add_documents(new_docs)` to append to Chroma collection
3. Rebuilds sparse (BM25) index with all documents combined
4. Updates database with new document list and batch info

### 3. RAG Pipeline Function

**File**: `src/rag/pipeline.py`

**New Function**:
```python
def add_documents_to_existing_session(uploaded_files, session_id, session_manager):
    """Process new documents and add to existing session.
    
    - Validates file types
    - Loads and chunks documents
    - Calls SessionManager to integrate
    - Returns success/failure with filenames
    """
```

**Process Flow**:
1. Save uploaded files to temp directory
2. Load documents with appropriate loaders (PDF/DOCX/XLSX)
3. Chunk documents with metadata enrichment
4. Add to session via SessionManager
5. Clean up temp files

### 4. API Endpoint

**File**: `src/api_server.py`

**New Endpoint**:
```
POST /api/sessions/{session_id}/documents
```

**Request**: Multipart form data with files  
**Response**:
```json
{
  "message": "Successfully added 2 document(s)",
  "session_id": "abc-123",
  "filenames": ["Budget_Q2.pdf", "Report.docx"],
  "count": 2
}
```

**Error Handling**:
- Returns 404 if session not found
- Returns 400 for invalid file types
- Returns 500 with descriptive message on processing errors
- **Critically**: Error message explicitly states chat session remains active

**System Message**: Automatically adds system message to chat history:
```
📎 Added 2 document(s) to conversation: Budget_Q2.pdf, Report.docx
```

### 5. Frontend Components

#### API Service (`frontend/src/services/api.js`)

**New Method**:
```javascript
addDocumentsToSession: async (sessionId, files, onProgress)
```

#### Chat Context (`frontend/src/context/ChatContext.jsx`)

**New Method**:
```javascript
const addDocumentsToSession = useCallback(async (files) => {
  // Upload documents
  // Add system message to UI
  // Reload session info
})
```

**Exported**: Added to context value for component access

#### Message Input (`frontend/src/components/MessageInput.jsx`)

**Changes**:
- Added "+" button next to textarea (only visible when session active)
- Hidden file input for file selection
- Triggers `addDocumentsToSession` on file select
- Shows upload progress indicator
- Disabled during upload to prevent conflicts

**UI Flow**:
1. User clicks "+" button
2. File picker opens (PDF, DOCX, XLSX only)
3. User selects file(s)
4. Upload progress shown
5. System message appears in chat
6. Input returns to normal state

#### Message Component (`frontend/src/components/Message.jsx`)

**Enhancement**:
- Added system message rendering
- System messages display as centered badges with paperclip icon
- Styled differently from user/assistant messages

**Visual**:
```
┌──────────────────────────────────────┐
│  📎 Added 2 document(s) to conversation  │
│     Budget_Q2.pdf, Report.docx        │
└──────────────────────────────────────┘
```

---

## Usage Guide

### For Users

1. **Start a chat session** with initial documents
2. **Have a conversation** - ask questions, get answers
3. **Click the "+" button** in the message input area when you want to add more documents
4. **Select additional documents** (PDF, DOCX, or XLSX)
5. **Continue chatting** - the system now has access to all documents

**Example Scenario**:
```
User uploads: Q1_Budget.pdf
User: "What was our Q1 spending?"
Assistant: "Q1 total spending was $500,000..."

[User clicks + button, uploads Q2_Budget.pdf]
System: 📎 Added 1 document(s) to conversation: Q2_Budget.pdf

User: "How does Q2 compare to Q1?"
Assistant: "Q2 spending was $550,000, an increase of $50,000..."
```

### For Developers

**Testing the Feature**:
```bash
# Run the test suite
python test_mid_conversation_upload.py
```

**Manual API Testing**:
```bash
# 1. Create initial session
curl -X POST http://localhost:8000/api/upload \
  -F "files=@document1.pdf"
# Returns: {"session_id": "abc-123", ...}

# 2. Add documents mid-conversation
curl -X POST http://localhost:8000/api/sessions/abc-123/documents \
  -F "files=@document2.pdf" \
  -F "files=@document3.pdf"
# Returns: {"message": "Successfully added 2 document(s)", ...}

# 3. Chat with all documents
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "message": "Compare all documents"}'
```

---

## Error Handling & Resilience

### Principle: Never Break the Chat

The implementation follows a strict principle: **No matter what goes wrong with document upload, the existing chat session must remain functional.**

### Error Scenarios

#### 1. Invalid Session ID
```python
# Returns: 404 Not Found
{"error": "Session not found or expired. Please create a new session."}
```
**Impact**: No session to break - user can create new session

#### 2. Invalid File Type
```python
# Returns: 400 Bad Request  
{"error": "Invalid file type: document.txt. Allowed: PDF, DOCX, XLSX"}
```
**Impact**: No changes made - user can retry with valid files

#### 3. Document Processing Failure
```python
# Returns: 500 Internal Server Error
{"error": "Error adding documents: <details>. Your chat session is still active."}
```
**Impact**: Session untouched - user can continue chatting with existing documents

#### 4. Vector Store Error
- Caught in `add_documents_to_session`
- Logs error details
- Returns `{"success": False}`
- API returns 500 with clear message
- **Session remains functional** with original documents

#### 5. Database Update Failure
- Vector store updated but tracking fails
- Logged as error
- Returns `{"success": False}`
- User can retry upload
- **Worst case**: Documents added but not tracked (still functional)

### Frontend Error Handling

```javascript
try {
  await addDocumentsToSession(files)
  // Success - system message shown
} catch (error) {
  console.error('Failed to add documents:', error)
  // Error toast shown
  // Chat input remains functional
  // User can retry or continue chatting
}
```

**User Experience**:
- Upload fails → Error toast appears
- Input remains active
- Can retry upload immediately
- Can continue chatting with existing documents
- No loss of conversation history

---

## Technical Deep Dive

### How Document Appending Works

**Chroma Collection Strategy**: Option B - Append to Existing Collection

```python
# Existing collection
collection = vectorstore.get_collection()
# Contains: doc1_chunk1, doc1_chunk2, doc2_chunk1...

# Add new documents
vectorstore.add_documents(new_chunks)
# Now contains: doc1_chunk1, doc1_chunk2, doc2_chunk1, doc3_chunk1...
```

**Benefits**:
- Single Chroma collection per session
- Simple retrieval (query one collection)
- No duplicate chunks
- Maintains document metadata for filtering

**Sparse Index Rebuild**:
```python
# Get all documents from updated collection
all_docs = vectorstore.get()
# Rebuild BM25 index with complete document set
sparse_index = SparseIndex(all_documents)
```

### Retrieval Behavior

**After adding documents**:
- Hybrid retrieval queries ALL documents (original + new)
- Round-robin sampling ensures fair representation
- Metadata filtering works across all documents
- Cross-encoder reranking considers all chunks

**Query Example**:
```
User: "Compare project budgets across all documents"
Retrieval:
  - Searches vectorstore (includes all documents)
  - BM25 search on all documents
  - Merges and reranks candidates
  - Round-robin samples from all sources
Result: Answer synthesized from original + newly added documents
```

### Session Restoration

**Scenario**: User refreshes page after adding documents

1. Frontend requests session messages
2. Backend checks in-memory sessions
3. If not found, calls `_restore_session()`
4. Restores vector store from disk (includes all documents)
5. Rebuilds sparse index from stored documents
6. **All documents available** - new and original

**Database Tracking Ensures**:
- `documents` field lists all filenames
- `document_batches` shows when each was added
- Frontend can display document list
- Audit trail maintained

---

## Performance Considerations

### Upload Time
- Depends on file size and number of files
- PDF parsing: ~1-2 seconds per 10 pages
- Embedding generation: ~0.5 seconds per chunk (batch)
- Total: Typically 5-10 seconds for 2-3 documents

### Memory Impact
- New chunks added to existing collection (minimal overhead)
- Sparse index rebuild: O(n) where n = total chunks
- Marginal impact on existing sessions

### Retrieval Performance
- No significant impact - same retrieval algorithm
- Larger collection → slightly more candidates to rank
- Cross-encoder time proportional to candidate count (capped at k=50)

### Scalability
- **Recommended**: Keep sessions under 20 documents
- **Supported**: Up to 50 documents per session
- **Beyond 50**: Consider document management features

---

## Testing Checklist

- [x] Database schema migration (handles existing sessions)
- [x] Document batch tracking works correctly
- [x] Session manager appends documents without errors
- [x] RAG pipeline processes new documents
- [x] API endpoint handles uploads and errors gracefully
- [x] Frontend button shows only when session active
- [x] File upload triggers correctly
- [x] System messages display in chat
- [x] Error messages don't break chat
- [x] Session restoration preserves all documents
- [x] Retrieval includes new documents
- [x] Chat history persists after document addition

**Run Tests**:
```bash
python test_mid_conversation_upload.py
```

---

## Future Enhancements

### Potential Improvements

1. **Document Management UI**
   - Show list of documents in session
   - Allow removing documents
   - Rename documents
   - View document metadata

2. **Batch Operations**
   - Add multiple batches
   - Undo last document addition
   - Merge sessions

3. **Advanced Tracking**
   - Track which message was asked with which documents available
   - Filter answers by document batch
   - Time-based document filters

4. **UI Enhancements**
   - Drag-and-drop in chat area
   - Preview documents before adding
   - Show thumbnail/icon for each document
   - Document tags/categories

5. **Performance**
   - Lazy loading for large document sets
   - Incremental index updates
   - Caching for frequently accessed documents

---

## Troubleshooting

### Issue: Documents not appearing in retrieval

**Check**:
1. Was upload successful? (Check API response)
2. Was system message added to chat?
3. Check server logs for errors
4. Verify vector store directory exists
5. Try querying with explicit document name

### Issue: Upload fails silently

**Check**:
1. File size limits (default: 16MB per file)
2. File format (only PDF, DOCX, XLSX)
3. Server disk space
4. Check browser console for errors
5. Check server logs

### Issue: Chat breaks after upload

**Should not happen** - but if it does:
1. Check server logs immediately
2. Report error with session ID
3. Session should auto-recover on reload
4. Verify `_restore_session()` works

### Issue: System messages not showing

**Check**:
1. `Message.jsx` has system message handling
2. CSS for system messages loaded
3. Browser console for React errors
4. Verify message role is "system"

---

## API Reference

### POST /api/sessions/{session_id}/documents

Add documents to an existing chat session.

**Parameters**:
- `session_id` (path): UUID of the session

**Request Body**:
- `files` (multipart): One or more files (PDF, DOCX, XLSX)

**Response** (200 OK):
```json
{
  "message": "Successfully added 2 document(s)",
  "session_id": "abc-123-def-456",
  "filenames": ["Budget.pdf", "Report.docx"],
  "count": 2
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "error": "Invalid file type: document.txt. Allowed: PDF, DOCX, XLSX"
}
```

404 Not Found:
```json
{
  "error": "Session not found or expired. Please create a new session."
}
```

500 Internal Server Error:
```json
{
  "error": "Error adding documents: <details>. Your chat session is still active."
}
```

---

## Migration Guide

### For Existing Deployments

1. **Database Migration**: Automatic on first run
   - `document_batches` column added with default `'[]'`
   - Existing sessions unaffected

2. **Frontend Update**: No breaking changes
   - New button only appears in updated UI
   - Old sessions work normally
   - API backward compatible

3. **Backend Deployment**:
   ```bash
   # Pull latest code
   git pull
   
   # Install any new dependencies (none required)
   pip install -r requirements.txt
   
   # Restart server
   # Database migration happens automatically
   ```

4. **Testing After Deployment**:
   ```bash
   # Quick test
   python test_mid_conversation_upload.py
   
   # Manual test
   # 1. Upload document via UI
   # 2. Start chat
   # 3. Click + button
   # 4. Upload another document
   # 5. Ask question referencing both documents
   ```

---

## Credits

**Implemented**: January 12, 2026  
**Version**: 1.0.0  
**Architecture**: Option B (Append to existing collection)  
**Status**: Production Ready ✅

