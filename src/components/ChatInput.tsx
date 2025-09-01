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
  <div className="border-t border-gray-900 bg-gray-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* File Upload Area */}
        {/* Show file upload if no files uploaded */}
        {showFileUpload && files.length === 0 && (
          <div className="mb-4 p-2 bg-gray-900 rounded-xl border border-gray-700 relative flex flex-col items-center justify-center">
            {/* Cross icon to close upload tab, always visible at top-right edge */}
            <button
              type="button"
              className="absolute -top-3 -right-3 p-2 bg-black border border-gray-700 shadow rounded-full text-gray-400 hover:text-orange-500 hover:bg-gray-800 z-10"
              onClick={() => setShowFileUpload(false)}
              aria-label="Close upload tab"
              style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
            </button>
            <div className="w-full flex flex-col items-center justify-center gap-2">
              <label htmlFor="file-upload" className="flex items-center gap-2 px-3 py-2 bg-black border border-gray-700 rounded-lg text-orange-400 cursor-pointer hover:bg-gray-800 transition-all duration-200 text-sm font-medium shadow">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M4 12V8a4 4 0 014-4h8a4 4 0 014 4v4M16 12v4M8 12v4" /></svg>
                Upload File
              </label>
              <input
                id="file-upload"
                type="file"
                multiple
                onChange={e => {
                  const selectedFiles = Array.from(e.target.files || []);
                  const newFiles = selectedFiles.map(file => ({
                    id: Math.random().toString(36).substr(2, 9),
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    preview: (file.type.startsWith('image/') || file.type === 'application/pdf') ? URL.createObjectURL(file) : undefined
                  }));
                  setFiles([...files, ...newFiles]);
                }}
                className="hidden"
              />
              <div className="w-full mt-2 flex flex-col items-center justify-center">
                <div className="w-full border-2 border-dashed border-orange-400 rounded-lg p-4 text-center text-sm text-gray-300 bg-black cursor-pointer hover:border-orange-500 transition-all duration-200">
                  Drag & Drop files here
                </div>
              </div>
            </div>
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
          <div className="flex items-center">
            <div className="flex flex-1 items-center bg-white border border-gray-300 rounded-xl shadow-sm px-2 py-1">
              <button
                type="button"
                onClick={() => setShowFileUpload(!showFileUpload)}
                className={`flex-shrink-0 p-2 rounded-lg transition-all duration-200 mr-2 ${
                  showFileUpload 
                    ? 'bg-orange-500 text-white' 
                    : 'bg-gray-100 text-orange-400 hover:bg-orange-600 hover:text-white'
                }`}
                aria-label="Attach file"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <textarea
                ref={textareaRef}
                value={message}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                disabled={disabled}
                className="flex-1 bg-transparent text-gray-800 placeholder-gray-400 px-2 py-2 resize-none focus:outline-none focus:ring-0 border-none"
                style={{ minHeight: '40px', maxHeight: '120px' }}
              />
              <button
                type="submit"
                disabled={disabled || (!message.trim() && files.length === 0)}
                className="ml-2 p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 shadow-sm flex items-center justify-center"
                aria-label="Send message"
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