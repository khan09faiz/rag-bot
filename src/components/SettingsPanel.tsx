import React from 'react';
import { Thermometer, Settings } from 'lucide-react';

interface SettingsPanelProps {
  isOpen: boolean;
  temperature: number;
  onTemperatureChange: (value: number) => void;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({ 
  isOpen, 
  temperature, 
  onTemperatureChange 
}) => {
  return (
    <div className={`fixed right-0 top-16 bottom-0 w-80 bg-white border-l border-gray-200 transform transition-transform duration-300 ease-in-out z-40 shadow-xl ${
      isOpen ? 'translate-x-0' : 'translate-x-full'
    }`}>
      <div className="p-6 h-full overflow-y-auto">
        <div className="flex items-center space-x-2 mb-6">
          <Settings className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-800">Settings</h2>
        </div>

        {/* Temperature Control */}
        <div className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Thermometer className="w-4 h-4 text-amber-500" />
              <label className="text-sm font-medium text-gray-700">
                Temperature
              </label>
              <span className="text-xs text-gray-500 ml-auto">
                {temperature.toFixed(2)}
              </span>
            </div>
            
            <div className="space-y-2">
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={temperature}
                onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                style={{
                  background: `linear-gradient(to right, #F59E0B 0%, #F59E0B ${temperature * 100}%, #E5E7EB ${temperature * 100}%, #E5E7EB 100%)`
                }}
              />
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>0.0 (Focused)</span>
                <span>1.0 (Creative)</span>
              </div>
            </div>
            
            <p className="text-xs text-gray-500 leading-relaxed">
              Lower values make responses more focused and deterministic. Higher values increase creativity and randomness.
            </p>
          </div>

          {/* Additional Settings Placeholder */}
          <div className="border-t border-gray-200 pt-4 mt-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Model Settings</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Model</span>
                <span className="text-sm text-blue-600 font-medium">GPT-4</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Max Tokens</span>
                <span className="text-sm text-gray-500">4096</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};