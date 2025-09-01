import React from 'react';
import { Settings, MessageSquare } from 'lucide-react';

interface HeaderProps {
  onToggleSettings: () => void;
  isSettingsOpen: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSettings, isSettingsOpen }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="flex items-center justify-center w-8 h-8 bg-blue-700 rounded-lg">
          <MessageSquare className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-gray-800">ProcessVenue AI</h1>
          <p className="text-sm text-gray-500">Intelligent Assistant</p>
        </div>
      </div>
      
      <button
        onClick={onToggleSettings}
        className={`p-2 rounded-lg transition-all duration-200 ${
          isSettingsOpen 
            ? 'bg-blue-700 text-white' 
            : 'bg-gray-100 text-gray-500 hover:bg-blue-600 hover:text-white'
        }`}
      >
        <Settings className="w-5 h-5" />
      </button>
    </header>
  );
};