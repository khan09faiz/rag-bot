import React from 'react';
import { Settings, MessageSquare } from 'lucide-react';

interface HeaderProps {
  onToggleSettings: () => void;
  isSettingsOpen: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSettings, isSettingsOpen }) => {
  return (
  <header className="bg-gray-900 border-b border-gray-900 px-6 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="flex items-center justify-center w-8 h-8 bg-orange-500 rounded-lg">
          <MessageSquare className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-gradient">ProcessVenue AI</h1>
          <p className="text-sm text-gradient">Intelligent Assistant</p>
        </div>
      </div>
      
      <button
        onClick={onToggleSettings}
        className={`p-2 rounded-lg transition-all duration-200 ${
          isSettingsOpen 
            ? 'bg-orange-500 text-white' 
            : 'bg-gray-800 text-orange-300 hover:bg-orange-600 hover:text-white'
        }`}
      >
        <Settings className="w-5 h-5" />
      </button>
    </header>
  );
};