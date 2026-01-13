import { useRef, useEffect, createRef } from 'react'
import Message from './Message'
import TypingIndicator from './TypingIndicator'
import { useChat } from '../context/ChatContext'

const MessageList = ({ messages }) => {
  const { sendingMessage, searchHighlight, setSearchHighlight } = useChat()
  const messageRefs = useRef([])

  // Initialize refs for each message
  useEffect(() => {
    messageRefs.current = messages.map((_, i) => messageRefs.current[i] || createRef())
  }, [messages])

  // Handle search highlight - scroll to first match and clear after 3 seconds
  useEffect(() => {
    if (searchHighlight?.query && searchHighlight?.timestamp) {
      // Find first message that contains the search query
      const matchIndex = messages.findIndex(msg => 
        msg.content && msg.content.toLowerCase().includes(searchHighlight.query.toLowerCase())
      )

      if (matchIndex !== -1 && messageRefs.current[matchIndex]?.current) {
        // Scroll to the matched message with smooth behavior after a short delay
        const scrollTimer = setTimeout(() => {
          messageRefs.current[matchIndex].current?.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
          })
        }, 300)

        // Clear highlight after 3 seconds
        const clearTimer = setTimeout(() => {
          setSearchHighlight(null)
        }, 3000)

        return () => {
          clearTimeout(scrollTimer)
          clearTimeout(clearTimer)
        }
      }
    }
  }, [searchHighlight?.timestamp, messages, setSearchHighlight])

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      {messages.map((message, index) => (
        <Message 
          key={index} 
          message={message}
          ref={messageRefs.current[index]}
          highlightQuery={searchHighlight?.query || null}
        />
      ))}
      
      {sendingMessage && <TypingIndicator />}
    </div>
  )
}

export default MessageList
