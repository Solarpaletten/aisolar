'use client'

import React, { useState } from 'react'
import { Sun, Moon } from 'lucide-react'
import AISolarCompressor from './AISolarCompressor'
import AISolarTranscriber from './AISolarTranscriber'

export default function AISolarTabs() {
  const [activeTab, setActiveTab] = useState<'compress' | 'transcribe'>('compress')
  const [darkMode, setDarkMode] = useState(false)

  return (
    <div className={`h-screen overflow-y-auto transition-colors duration-300 ${
      darkMode 
        ? 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900' 
        : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50'
    }`}>
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Заголовок и кнопки */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} flex items-center gap-3`}>
              🌞 AISOLAR
              <span className="text-sm font-normal px-3 py-1 bg-purple-600 text-white rounded-full">
                v2.0
              </span>
            </h1>
            <p className={`mt-2 ${darkMode ? 'text-purple-300' : 'text-purple-600'} font-medium`}>
              AI-транскрибация видео в текст
            </p>
          </div>

          {/* Кнопка Dark Mode */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`p-3 rounded-lg transition-colors ${
              darkMode 
                ? 'bg-slate-800 hover:bg-slate-700 text-yellow-400' 
                : 'bg-white hover:bg-gray-100 text-gray-700'
            }`}
            title={darkMode ? 'Светлая тема' : 'Тёмная тема'}
          >
            {darkMode ? <Sun size={24} /> : <Moon size={24} />}
          </button>
        </div>

        {/* Вкладки */}
        <div className={`flex gap-4 border-b-2 ${
          darkMode ? 'border-slate-700' : 'border-gray-200'
        }`}>
          <button
            onClick={() => setActiveTab('compress')}
            className={`px-6 py-3 font-semibold transition-all duration-200 relative ${
              activeTab === 'compress'
                ? darkMode
                  ? 'text-purple-400'
                  : 'text-purple-600'
                : darkMode
                  ? 'text-gray-400 hover:text-gray-300'
                  : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <span className="flex items-center gap-2">
              🗜️ Сжать файл
            </span>
            {activeTab === 'compress' && (
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-t-full" />
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('transcribe')}
            className={`px-6 py-3 font-semibold transition-all duration-200 relative ${
              activeTab === 'transcribe'
                ? darkMode
                  ? 'text-purple-400'
                  : 'text-purple-600'
                : darkMode
                  ? 'text-gray-400 hover:text-gray-300'
                  : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <span className="flex items-center gap-2">
              🎬 Транскрибация
            </span>
            {activeTab === 'transcribe' && (
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-t-full" />
            )}
          </button>
        </div>

        {/* Контент вкладок */}
        <div className="animate-fadeIn">
          {activeTab === 'compress' ? (
            <AISolarCompressor darkMode={darkMode} />
          ) : (
            <AISolarTranscriber darkMode={darkMode} />
          )}
        </div>
      </div>
    </div>
  )
}