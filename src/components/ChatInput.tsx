import React, { useState, useRef } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { FileUpload, FileItem } from './FileUpload';
import { FilePreviewModal } from './FilePreviewModal';

interface ChatInputProps {
  onSendMessage: (message: string, files?: FileItem[]) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState<FileItem[]>([]);
  const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() || files.length > 0) {
      onSendMessage(message.trim(), files);
      setMessage('');
      setFiles([]);
  // Do not hide file upload after sending message, keep it toggled by user
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
  <div className="border-t border-gray-900 bg-black p-4">
      <div className="max-w-4xl mx-auto">
        {/* File Upload Area */}
        {/* Show file upload if no files uploaded */}
        {showFileUpload && files.length === 0 && ( 
          <div className="mb-4 p-4 bg-gray-50 rounded-xl border border-gray-200 relative">
            {/* Cross icon to close upload tab, always visible at top-right edge */}
            <button
              type="button"
              className="absolute -top-3 -right-3 p-2 bg-white border border-gray-300 shadow rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 z-10"
              onClick={() => setShowFileUpload(false)}
              aria-label="Close upload tab"
              style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
            </button>
            <FileUpload files={files} onFilesChange={setFiles} />
          </div>
        )}

        {/* Show uploaded PDF above chat input, allow remove and preview */}
        {files.length > 0 && files.map(file => file.type === 'application/pdf' ? (
          <div key={file.id} className="mb-4 flex items-center bg-white border border-gray-200 rounded-xl p-3 shadow-sm">
            <iframe
              src={file.preview}
              title={file.name}
              className="w-32 h-20 rounded border border-gray-200 mr-4"
              style={{ minWidth: '120px', minHeight: '80px' }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
              <div className="flex items-center space-x-2 mt-1">
                <button
                  className="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
                  onClick={() => {
                    setPreviewFile(file);
                    setIsModalOpen(true);
                  }}
                >Preview</button>
        {/* PDF Preview Modal */}
        <FilePreviewModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setPreviewFile(null);
          }}
          file={previewFile}
        />
                <button
                  className="px-2 py-1 text-xs bg-red-50 text-red-700 rounded hover:bg-red-100"
                    onClick={() => {
                      setFiles(prev => prev.filter(f => f.id !== file.id));
                      // Always keep chat input visible, do not show upload option again
                      setShowFileUpload(false);
                    }}
                >Remove</button>
              </div>
            </div>
          </div>
        ) : null)}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={() => setShowFileUpload(!showFileUpload)}
              className={`flex-shrink-0 p-3 rounded-xl transition-all duration-200 ${
                showFileUpload 
                  ? 'bg-orange-500 text-white' 
                  : 'bg-gray-800 text-orange-300 hover:bg-orange-600 hover:text-white'
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
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-700 disabled:cursor-not-allowed transition-all duration-200 shadow-sm flex items-center justify-center"
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