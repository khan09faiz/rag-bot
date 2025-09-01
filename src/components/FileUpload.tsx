import React, { useCallback, useState } from 'react';
import { Upload, X, FileText, Image, File } from 'lucide-react';
import { FilePreviewModal } from './FilePreviewModal';

export interface FileItem {
  id: string;
  name: string;
  size: number;
  type: string;
  preview?: string;
}

interface FileUploadProps {
  files: FileItem[];
  onFilesChange: (files: FileItem[]) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ files, onFilesChange }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    const newFiles: FileItem[] = droppedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));
    
    onFilesChange([...files, ...newFiles]);
  }, [files, onFilesChange]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    const newFiles: FileItem[] = selectedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));
    
    onFilesChange([...files, ...newFiles]);
  }, [files, onFilesChange]);

  const removeFile = useCallback((fileId: string) => {
    onFilesChange(files.filter(f => f.id !== fileId));
  }, [files, onFilesChange]);

  const openFilePreview = useCallback((file: FileItem) => {
    setSelectedFile(file);
    setIsModalOpen(true);
  }, []);

  const closeFilePreview = useCallback(() => {
    setIsModalOpen(false);
    setSelectedFile(null);
  }, []);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="w-4 h-4" />;
    if (type.includes('text/') || type.includes('application/json')) return <FileText className="w-4 h-4" />;
    return <File className="w-4 h-4" />;
  };

  return (
    <div className="space-y-3">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all duration-200 cursor-pointer ${
          isDragOver 
            ? 'border-emerald-500 bg-emerald-50' 
            : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
        }`}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <Upload className={`w-8 h-8 mx-auto mb-2 transition-colors ${
          isDragOver ? 'text-emerald-500' : 'text-gray-500'
        }`} />
        
        <p className={`text-sm font-medium ${isDragOver ? 'text-emerald-600' : 'text-gray-700'}`}>
          {isDragOver ? 'Drop files here' : 'Drop files here or click to upload'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Supports images, text files, and documents
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-800">Preview your docs</h4>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {files.length} file{files.length > 1 ? 's' : ''}
            </span>
          </div>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {files.map((file) => (
              <div 
                key={file.id} 
                className="flex items-center space-x-3 bg-white border border-gray-200 rounded-lg p-3 shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer hover:border-blue-300"
                onClick={() => openFilePreview(file)}
              >
                <div className="text-gray-500">
                  {getFileIcon(file.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
                  <div className="flex items-center space-x-2">
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                      Ready to analyze
                    </span>
                  </div>
                </div>
                
                {file.preview && (
                  <div className="relative">
                    <img 
                    src={file.preview} 
                    alt={file.name}
                      className="w-10 h-10 rounded-lg object-cover border border-gray-200"
                    />
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white"></div>
                  </div>
                )}
                
                <button
                  onClick={() => removeFile(file.id)}
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(file.id);
                  }}
                  className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all duration-200 rounded-lg"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-700 flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
              Your documents are ready for analysis. Send your message to begin processing.
            </p>
          </div>
        </div>
      )}

      <FilePreviewModal 
        isOpen={isModalOpen}
        onClose={closeFilePreview}
        file={selectedFile}
      />
    </div>
  );
};