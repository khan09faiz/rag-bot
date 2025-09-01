import React from 'react';
import { X, Download, FileText, Image, File, Eye } from 'lucide-react';
import { FileItem } from './FileUpload';

interface FilePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  file: FileItem | null;
}

export const FilePreviewModal: React.FC<FilePreviewModalProps> = ({ 
  isOpen, 
  onClose, 
  file 
}) => {
  if (!isOpen || !file) return null;

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="w-6 h-6" />;
    if (type.includes('text/') || type.includes('application/json')) return <FileText className="w-6 h-6" />;
    return <File className="w-6 h-6" />;
  };

  const isImage = file.type.startsWith('image/');
  const isText = file.type.includes('text/') || file.type.includes('application/json');

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-slate-50 to-gray-50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg text-blue-700">
              {getFileIcon(file.type)}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">File Preview</h2>
              <p className="text-sm text-gray-500">Document analysis ready</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200">
              <Download className="w-5 h-5" />
            </button>
            <button 
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* File Details */}
        <div className="p-6 border-b border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">File Name</p>
              <p className="text-sm font-medium text-gray-800 break-all">{file.name}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">File Size</p>
              <p className="text-sm text-gray-700">{formatFileSize(file.size)}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">File Type</p>
              <p className="text-sm text-gray-700">{file.type || 'Unknown'}</p>
            </div>
          </div>
        </div>

        {/* File Content Preview */}
        <div className="p-6 overflow-y-auto max-h-96">
          <div className="flex items-center space-x-2 mb-4">
            <Eye className="w-4 h-4 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-800">Content Preview</h3>
          </div>

          {isImage && file.preview ? (
            <div className="flex justify-center">
              <img 
                src={file.preview} 
                alt={file.name}
                className="max-w-full max-h-80 rounded-xl shadow-lg border border-gray-200"
              />
            </div>
          ) : isText ? (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-3">
                <FileText className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Text Document</span>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4 font-mono text-sm text-gray-700 max-h-64 overflow-y-auto">
                <p className="text-gray-500 italic">Content preview will be available after processing...</p>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-8 text-center">
              <div className="flex flex-col items-center space-y-3">
                {getFileIcon(file.type)}
                <div>
                  <p className="text-sm font-medium text-gray-700">Preview not available</p>
                  <p className="text-xs text-gray-500">This file type cannot be previewed directly</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-6 border-t border-gray-200 bg-gradient-to-r from-slate-50 to-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Ready for analysis</span>
            </div>
            
            <div className="flex space-x-3">
              <button 
                onClick={onClose}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors duration-200"
              >
                Close
              </button>
              <button className="px-6 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-800 transition-all duration-200 shadow-sm hover:shadow-md">
                Analyze Document
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};