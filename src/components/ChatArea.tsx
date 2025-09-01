import React, { useRef, useEffect } from 'react';
import { Message, MessageType } from './Message';
import { TypingIndicator } from './TypingIndicator';

interface ChatAreaProps {
  messages: MessageType[];
  isTyping: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, isTyping }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="max-w-4xl mx-auto p-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <span className="text-2xl">🤖</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to ProcessVenue AI</h2>
            <p className="text-gray-500 max-w-md">
              Start a conversation by typing a message below. You can also upload files to analyze or discuss.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
            {isTyping && <TypingIndicator />}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};