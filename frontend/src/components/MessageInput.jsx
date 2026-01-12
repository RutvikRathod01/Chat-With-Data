import { useState, useRef, useEffect } from 'react'
import { FaArrowUp, FaStop, FaPlus, FaPaperclip } from 'react-icons/fa'
import { useChat } from '../context/ChatContext'

const MessageInput = ({ disabled }) => {
  const { sendMessage, sendingMessage, addDocumentsToSession, uploading, currentSession } = useChat()
  const [input, setInput] = useState('')
  const [showFileUpload, setShowFileUpload] = useState(false)
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 240)}px`
    }
  }, [input])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || sendingMessage || disabled) return

    const message = input.trim()
    setInput('')

    try {
      await sendMessage(message)
    } catch (error) {
      setInput(message) // Restore input on error
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    try {
      await addDocumentsToSession(files)
      setShowFileUpload(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      console.error('Failed to add documents:', error)
    }
  }

  const triggerFileUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div className="max-w-4xl mx-auto w-full p-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center bg-white border-2 border-gray-300 rounded-3xl shadow-lg focus-within:border-blue-500 transition-colors">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.xlsx"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {/* Add documents button - only show when session is active */}
          {currentSession && !disabled && (
            <button
              type="button"
              onClick={triggerFileUpload}
              disabled={uploading || sendingMessage}
              className={`ml-3 p-2 rounded-full transition-all ${
                uploading || sendingMessage
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800'
              }`}
              title="Add documents to conversation"
            >
              <FaPlus className="w-4 h-4" />
            </button>
          )}
          
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled
                ? 'Select a session or upload documents to start chatting...'
                : 'Ask a question about your documents...'
            }
            disabled={disabled || sendingMessage}
            rows={1}
            className="flex-1 px-5 py-4 bg-transparent border-none outline-none resize-none overflow-y-auto min-h-[56px] disabled:cursor-not-allowed disabled:text-gray-400"
            style={{
              maxHeight: '240px', // ~10 lines
              scrollbarWidth: 'thin',
              scrollbarColor: '#CBD5E0 transparent',
            }}
          />

          <div className="flex items-center px-3">
            {sendingMessage ? (
              <button
                type="button"
                className="p-3 bg-red-500 hover:bg-red-600 text-white rounded-full transition-all transform hover:scale-105 shadow-md"
                title="Stop generation"
              >
                <FaStop className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim() || disabled}
                className={`p-3 rounded-full transition-all transform shadow-md ${input.trim() && !disabled
                  ? 'bg-black hover:bg-gray-800 text-white hover:scale-105'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                title="Send message"
              >
                <FaArrowUp className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between mt-2 px-2 text-xs text-gray-500">
          <span>
            {currentSession 
              ? 'Press Enter to send, Shift + Enter for new line'
              : 'Select a session or upload documents to start'
            }
          </span>
          <span>{input.length} characters</span>
        </div>
        
        {/* Upload progress indicator */}
        {uploading && (
          <div className="mt-2 px-2">
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <FaPaperclip className="animate-pulse" />
              <span>Adding documents to conversation...</span>
            </div>
          </div>
        )}
      </form>
    </div>
  )
}

export default MessageInput
