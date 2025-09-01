import React, { useState, useRef } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { FileUpload, FileItem } from './FileUpload';

interface ChatInputProps {
  onSendMessage: (message: string, files?: FileItem[]) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState<FileItem[]>([]);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() || files.length > 0) {
      onSendMessage(message.trim(), files);
      setMessage('');
      setFiles([]);
      setShowFileUpload(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        {/* File Upload Area */}
        {showFileUpload && (
          <div className="mb-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <FileUpload files={files} onFilesChange={setFiles} />
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end space-x-3">
            <button
              type="button"
              onClick={() => setShowFileUpload(!showFileUpload)}
              className={`flex-shrink-0 p-3 rounded-xl transition-all duration-200 ${
                showFileUpload 
                  ? 'bg-emerald-500 text-white' 
                  : 'bg-gray-100 text-gray-500 hover:bg-blue-600 hover:text-white'
              }`}
            >
              <Paperclip className="w-5 h-5" />
            </button>

            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                disabled={disabled}
                className="w-full bg-white text-gray-800 placeholder-gray-400 rounded-xl px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 transition-all duration-200 shadow-sm"
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
              
              <button
                type="submit"
                disabled={disabled || (!message.trim() && files.length === 0)}
                className="absolute right-2 bottom-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 shadow-sm"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>

          {files.length > 0 && (
            <div className="mt-2 text-xs text-gray-500">
              {files.length} file{files.length > 1 ? 's' : ''} attached
            </div>
          )}
        </form>
      </div>
    </div>
  );
};