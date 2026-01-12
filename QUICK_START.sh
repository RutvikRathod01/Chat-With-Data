#!/bin/bash

# Quick Start: Mid-Conversation Document Upload Feature
# This script helps you get started with testing the new feature

echo "=================================================="
echo "Mid-Conversation Document Upload - Quick Start"
echo "=================================================="
echo ""

# Check if in correct directory
if [ ! -f "src/api_server.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   (Chat-With-Data/)"
    exit 1
fi

echo "✓ Running from correct directory"
echo ""

# Step 1: Check Python environment
echo "Step 1: Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Step 2: Run tests (optional but recommended)
echo "Step 2: Would you like to run the test suite? (y/n)"
read -r RUN_TESTS

if [ "$RUN_TESTS" = "y" ] || [ "$RUN_TESTS" = "Y" ]; then
    echo ""
    echo "Running tests..."
    $PYTHON_CMD test_mid_conversation_upload.py
    TEST_EXIT=$?
    echo ""
    if [ $TEST_EXIT -eq 0 ]; then
        echo "✅ All tests passed!"
    else
        echo "⚠️  Some tests failed, but you can still proceed"
        echo "   The feature should work, but review test output"
    fi
    echo ""
fi

# Step 3: Instructions for starting servers
echo "=================================================="
echo "Step 3: Starting the Application"
echo "=================================================="
echo ""
echo "You need to start TWO servers:"
echo ""
echo "Terminal 1 - Backend Server:"
echo "  cd src"
echo "  python api_server.py"
echo ""
echo "Terminal 2 - Frontend Server:"
echo "  cd frontend"
echo "  npm run dev"
echo ""

# Step 4: Usage instructions
echo "=================================================="
echo "Step 4: How to Use the Feature"
echo "=================================================="
echo ""
echo "1. Open your browser to: http://localhost:5173"
echo ""
echo "2. Upload initial document(s):"
echo "   - Click 'Select files' button"
echo "   - Choose PDF, DOCX, or XLSX files"
echo "   - Click 'Upload and Process'"
echo ""
echo "3. Start chatting:"
echo "   - Ask questions about your documents"
echo "   - Get AI responses"
echo ""
echo "4. Add more documents (NEW FEATURE!):"
echo "   - Look for the '+' button in the message input area"
echo "   - Click it to add more documents"
echo "   - Select additional files"
echo "   - Continue your conversation with all documents!"
echo ""

# Step 5: Example workflow
echo "=================================================="
echo "Example Workflow"
echo "=================================================="
echo ""
echo "Scenario: Budget Analysis"
echo ""
echo "1. Upload: Budget_Q1.pdf"
echo "   Ask: 'What was our Q1 spending?'"
echo "   → Get answer about Q1"
echo ""
echo "2. Click '+' button, upload: Budget_Q2.pdf"
echo "   System shows: '📎 Added 1 document(s)'"
echo ""
echo "3. Ask: 'Compare Q1 and Q2 spending'"
echo "   → Get comparative analysis using BOTH documents!"
echo ""

# Step 6: Troubleshooting
echo "=================================================="
echo "Troubleshooting"
echo "=================================================="
echo ""
echo "If something doesn't work:"
echo ""
echo "1. Check server logs in terminals"
echo "2. Check browser console (F12 → Console tab)"
echo "3. Verify both servers are running"
echo "4. Try refreshing the browser"
echo "5. Check MID_CONVERSATION_UPLOAD_FEATURE.md for details"
echo ""

# Final message
echo "=================================================="
echo "Ready to Go! 🚀"
echo "=================================================="
echo ""
echo "Start your servers and try the new feature!"
echo "Documentation: MID_CONVERSATION_UPLOAD_FEATURE.md"
echo "Tests: test_mid_conversation_upload.py"
echo ""
echo "Happy chatting! 💬"
echo ""
