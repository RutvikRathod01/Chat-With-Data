import { useState } from 'react'
import { FaBars, FaRobot, FaFile } from 'react-icons/fa'
import { useChat } from '../context/ChatContext'

const Header = ({ onMenuClick }) => {
  const { currentSession, messages } = useChat()
  const [docTooltip, setDocTooltip] = useState(null)

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm relative z-30">
        <div className="flex items-center space-x-3">
          {/* Mobile toggle button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            <FaBars className="w-5 h-5 text-gray-600" />
          </button>

          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <FaRobot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 leading-tight">
                {currentSession ? currentSession.document_name : 'Chat with Documents'}
              </h1>
              {currentSession && (
                <div className="flex items-center space-x-2 text-xs text-gray-500 mt-0.5">
                  <span>
                    {messages.length} {messages.length === 1 ? 'message' : 'messages'}
                  </span>

                  {currentSession.documents && currentSession.documents.length > 0 && (
                    <>
                      <span>•</span>
                      <div
                        className="flex items-center space-x-1 cursor-help hover:text-blue-600 transition-colors"
                        onMouseEnter={(e) => {
                          const rect = e.currentTarget.getBoundingClientRect()
                          setDocTooltip({
                            x: rect.left,
                            y: rect.bottom + 5,
                            documents: currentSession.documents
                          })
                        }}
                        onMouseLeave={() => setDocTooltip(null)}
                      >
                        <FaFile className="w-3 h-3" />
                        <span>
                          {currentSession.documents.length} {currentSession.documents.length === 1 ? 'Document' : 'Documents'}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Online</span>
          </div>
        </div>
      </header>

      {/* Document List Tooltip */}
      {docTooltip && (
        <div
          className="fixed z-[100] bg-gray-900 text-white border border-gray-700 rounded-lg shadow-xl p-3 min-w-[200px] max-w-xs pointer-events-none"
          style={{ top: docTooltip.y, left: docTooltip.x }}
        >
          <div className="text-xs font-semibold text-gray-400 mb-2 border-b border-gray-700 pb-1">
            Attached Documents
          </div>
          <ul className="space-y-1 max-h-48 overflow-y-auto scrollbar-thin">
            {docTooltip.documents.map((doc, i) => (
              <li key={i} className="text-xs text-gray-300 truncate flex items-center space-x-2">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
                <span className="truncate">{doc}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  )
}

export default Header
