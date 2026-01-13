# Features & Capabilities

This intelligent RAG (Retrieval-Augmented Generation) system serves as a knowledgeable assistant for your documents. Below is a comprehensive list of all supported features and functionalities.

## Core Capabilities

### 📄 Document Processing
- **Format Support**: Handles **PDF**, **Word (DOCX)**, and **Excel (XLSX)** files.
- **Entity Extraction**: Automatically identifies and tags key information including:
  - **Projects** & Initiatives
  - **People** & Stakeholders
  - **Dates**, Timelines, & Deadlines
  - **Locations** & Geographies
  - **Key Concepts**
- **Mid-Conversation Uploads**: **Add-on document support** allows you to upload extra files into a *running chat* without losing context.
- **Multi-Document Chat**: Seamlessly query across 10+ documents with a **single query**. The system intelligently aggregates answers from all available files.

### 💬 Natural Language Q&A
- **Intelligent Answering**: Ask questions in plain English or other languages.
- **Smart CITATIONS**: Every answer includes smart, precise **source references** (document name & page number) so you can verify facts.
- **Response Synthesis**: Generates cohesive answers by combining information from multiple chunks and documents.
- **User-Friendly AI**: Designed to be helpful, polite, and capable of handling greetings and small talk naturally.

---

## Session & Interface Management

### 🛠️ Session Control
- **Auto-Naming**: Sessions are automatically named based on uploaded files.
- **Custom Renaming**: **Rename sessions** to meaningful titles (e.g., "Q1 Financials") for better organization.
- **Sorting & Organization**: Sessions are sortable by name or update time, making it easy to manage large workspaces.
- **Clear & Delete**: 
  - **Clear Chat**: Wipe conversation history while retaining documents.
  - **Delete Session**: Completely remove a session and its data.

### 📊 Status & Tracking
- **Document Count**: Visible counters show exactly how many documents are in each session.
- **Message Count**: Track conversation depth with message counters.
- **Robust Error Handling**: The system handles upload errors or invalid files gracefully, ensuring the **chat never crashes** and you can continue working.

---

## Smart Intelligence Features

### 🧠 Adaptive Retrieval & Ranking
- **Adaptive Strategy**: Automatically switches between:
  - **Semantic Mode**: For specific fact-based questions.
  - **Exhaustive Mode**: For counting and listing tasks (retrieves *all* matching data).
- **Cross-Encoder Re-Ranking**: Uses a specialized AI model to score and re-rank document chunks, ensuring only the most highly relevant information is used.
- **Hybrid Search**: Combines **Semantic Search** (meaning) and **Keyword Search** (exact text) for maximum accuracy.

### 🔍 Metadata-Powered Precision
- **Smart Filtering**: Remove repeated or duplicate content automatically.
- **Metadata Filters**: Can narrow searches to specific documents, page numbers, or entity types (e.g., "only in Budget.pdf").
- **Smart Counting**: Uses extracted metadata to accurately count items (e.g., "How many projects?") without missing data.

---

## Advanced Query Handling

### 🔄 Multi-Intent & Logic
- **Query Rewriting**: The system intelligently expands and clarifies your questions (e.g., changing "What about timelines?" to "What are the timelines for Project X?") for better search results.
- **Complex Decomposition**: Breaks down compound questions (e.g., "Budget AND Timeline") into separate sub-queries.
- **Pronoun Resolution**: Understands "it", "them", or "that" using conversation history.

### 🛡️ Accuracy & Validation
- **Smart Validation**: An AI validator specifically checks answer completeness and warns if information appears missing (e.g., "Found 3 projects, but context suggests 5 exist").
- **Context Isolation**: Chat history is used for understanding context but *not* mixed into the knowledge base, preventing "data contamination" from previous questions.

---

## Summary of Supported Use Cases

| Use Case | Example Query |
| :--- | :--- |
| **All-in-One Query** | "Compare the timelines of Project A and Project B from all files." |
| **Specific Facts** | "Who is the project manager mentioned in the contract?" |
| **Counting & Listing** | "How many total risks are identified across the 3 reports?" |
| **Document Scoping** | "Summarize only the 'Executive Summary' in Report_v2.pdf." |
| **Verification** | "Where is the $500k budget mentioned?" (Check sources) |
| **Cross-Doc Analysis**| "What is the difference in budget between the two proposals?" |
