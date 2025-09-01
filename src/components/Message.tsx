import React from 'react';
import { User, Bot, CheckCheck, Info } from 'lucide-react';

export interface MessageType {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  sent?: boolean; // true if sent, false if not
}

interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  return (
    <div className={`flex items-start space-x-3 ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
        message.isUser ? 'bg-blue-600' : 'bg-gray-600'
      }`}>
        {message.isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      
      <div className={`max-w-[70%] ${message.isUser ? 'text-right' : ''}`}>
        <div className={`inline-block px-4 py-3 rounded-2xl relative ${
          message.isUser 
            ? 'bg-black text-white border border-gray-700 rounded-br-md' 
            : 'bg-black text-white border border-gray-700 rounded-bl-md'
        }`}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap flex-1">{message.content}</p>
          {message.isUser && (
            <span className="absolute bottom-1 right-2 flex items-center">
              {message.sent === false ? (
                <span className="inline-flex items-center justify-center w-3 h-3 rounded-full border border-orange-300 bg-black text-orange-300">
                  <Info className="w-2 h-2" />
                </span>
              ) : (
                <CheckCheck className="w-3 h-3 text-orange-300" />
              )}
            </span>
          )}
        </div>
        <p className="text-xs text-orange-300 mt-1 px-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};