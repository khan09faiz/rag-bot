import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { ChatArea } from './components/ChatArea';
import { ChatInput } from './components/ChatInput';
import { SettingsPanel } from './components/SettingsPanel';
import { MessageType } from './components/Message';
import { FileItem } from './components/FileUpload';

function App() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [temperature, setTemperature] = useState(0.7);

  const handleSendMessage = useCallback(async (content: string, files?: FileItem[]) => {
    // Add user message
    const userMessage: MessageType = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: `I received your message: "${content}"${files?.length ? ` with ${files.length} file(s)` : ''}. This is a simulated response. Temperature is set to ${temperature.toFixed(2)}.`,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  }, [temperature]);

  const toggleSettings = useCallback(() => {
    setIsSettingsOpen(prev => !prev);
  }, []);

  return (
  <div className="h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex flex-col overflow-y-auto scrollbar-thin scrollbar-thumb-blue-300 scrollbar-track-blue-50">
      <Header onToggleSettings={toggleSettings} isSettingsOpen={isSettingsOpen} />
      
      <div className="flex-1 flex relative">
        <div className={`flex-1 flex flex-col transition-all duration-300 ${
          isSettingsOpen ? 'mr-80' : 'mr-0'
        }`}>
          <ChatArea messages={messages} isTyping={isTyping} />
          <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
        </div>
        
        <SettingsPanel 
          isOpen={isSettingsOpen}
          temperature={temperature}
          onTemperatureChange={setTemperature}
        />
      </div>

      {/* Overlay for mobile */}
      {isSettingsOpen && (
        <div 
          className="fixed inset-0 bg-gray-900 bg-opacity-75 z-30 lg:hidden"
          onClick={() => setIsSettingsOpen(false)}
        />
      )}
    </div>
  );
}

export default App;