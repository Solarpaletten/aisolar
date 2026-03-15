'use client'

import React, { useState, useRef } from 'react'
import { Upload, FileAudio, FileVideo, HardDrive, Loader2, CheckCircle2, Download, Trash2 } from 'lucide-react'

interface CompressorProps {
  darkMode: boolean
}

interface CompressionResult {
  originalSize: number
  compressedSize: number
  filename: string
  downloadUrl: string
}

export default function AISolarCompressor({ darkMode }: CompressorProps) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CompressionResult | null>(null)
  const [progress, setProgress] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const formatFileSize = (bytes: number): string => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
      setProgress('')
    }
  }

  const handleCompress = async () => {
    if (!file) return

    setLoading(true)
    setProgress('🔄 Подготовка файла...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      setProgress('🗜️ Сжимаем файл...')
      
      const response = await fetch('/api/compress', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Ошибка сжатия')
      }

      const blob = await response.blob()
      const originalSize = parseInt(response.headers.get('X-Original-Size') || '0')
      const compressedSize = parseInt(response.headers.get('X-Compressed-Size') || '0')
      
      const downloadUrl = URL.createObjectURL(blob)
      
      setResult({
        originalSize,
        compressedSize,
        filename: `compressed-${file.name.split('.')[0]}.mp3`,
        downloadUrl
      })

      setProgress('✅ Сжатие завершено!')

    } catch (error) {
      console.error('Ошибка сжатия:', error)
      setProgress('❌ Ошибка при сжатии файла')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setFile(null)
    setResult(null)
    setProgress('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const isAudio = file?.type.startsWith('audio/')
  const isVideo = file?.type.startsWith('video/')

  return (
    <div className="space-y-6">
      {/* Загрузка файла */}
      <div className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
        darkMode 
          ? 'border-purple-500/50 hover:border-purple-400 bg-slate-800/50' 
          : 'border-purple-300 hover:border-purple-400 bg-white'
      }`}>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,video/*,.m4a,.mp3,.wav,.ogg,.mp4,.avi,.mov,.mkv"
          onChange={handleFileSelect}
          className="hidden"
          id="compress-upload"
        />
        <label htmlFor="compress-upload" className="cursor-pointer block">
          <div className="flex flex-col items-center gap-4">
            <div className={`p-4 rounded-full ${
              darkMode ? 'bg-purple-900/50' : 'bg-purple-100'
            }`}>
              <Upload size={48} className={darkMode ? 'text-purple-400' : 'text-purple-600'} />
            </div>
            <div>
              <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                Загрузите аудио или видео файл
              </p>
              <p className={`text-sm mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Поддерживаются: MP3, WAV, M4A, OGG, MP4, AVI, MOV, MKV
              </p>
            </div>
          </div>
        </label>
      </div>

      {/* Информация о файле */}
      {file && (
        <div className={`rounded-2xl p-6 ${
          darkMode ? 'bg-slate-800/50' : 'bg-white'
        } shadow-lg`}>
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl ${
              darkMode ? 'bg-purple-900/50' : 'bg-purple-100'
            }`}>
              {isAudio ? (
                <FileAudio size={32} className={darkMode ? 'text-purple-400' : 'text-purple-600'} />
              ) : (
                <FileVideo size={32} className={darkMode ? 'text-purple-400' : 'text-purple-600'} />
              )}
            </div>
            <div className="flex-1">
              <h3 className={`font-semibold text-lg ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                {file.name}
              </h3>
              <div className={`flex gap-4 mt-2 text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                <span className="flex items-center gap-1">
                  <HardDrive size={16} />
                  {formatFileSize(file.size)}
                </span>
                <span className="capitalize">
                  {isAudio ? '🎵 Аудио' : '🎥 Видео'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Кнопки действий */}
      {file && !result && (
        <div className="flex gap-3">
          <button
            onClick={handleCompress}
            disabled={loading}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all transform hover:scale-105 ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
            } text-white shadow-lg`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 size={20} className="animate-spin" />
                Сжимаем...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                🗜️ Сжать файл
              </span>
            )}
          </button>
          
          <button
            onClick={handleClear}
            disabled={loading}
            className={`px-6 py-4 rounded-xl font-semibold transition-all ${
              darkMode
                ? 'bg-red-900/50 hover:bg-red-800/50 text-red-400'
                : 'bg-red-100 hover:bg-red-200 text-red-600'
            }`}
          >
            <Trash2 size={20} />
          </button>
        </div>
      )}

      {/* Прогресс */}
      {loading && progress && (
        <div className={`rounded-xl p-4 ${
          darkMode ? 'bg-blue-900/30' : 'bg-blue-50'
        } border ${darkMode ? 'border-blue-500/30' : 'border-blue-200'}`}>
          <p className={`text-center ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>
            {progress}
          </p>
        </div>
      )}

      {/* Результат сжатия */}
      {result && (
        <div className={`rounded-2xl p-6 ${
          darkMode ? 'bg-green-900/30' : 'bg-green-50'
        } border-2 ${darkMode ? 'border-green-500/50' : 'border-green-200'}`}>
          <div className="flex items-start gap-3 mb-4">
            <CheckCircle2 size={24} className={darkMode ? 'text-green-400' : 'text-green-600'} />
            <div className="flex-1">
              <h3 className={`font-bold text-lg ${darkMode ? 'text-green-300' : 'text-green-800'}`}>
                ✅ Файл успешно сжат!
              </h3>
              <div className={`mt-3 space-y-2 ${darkMode ? 'text-green-200' : 'text-green-700'}`}>
                <p className="flex justify-between">
                  <span>Оригинал:</span>
                  <span className="font-semibold">{formatFileSize(result.originalSize)}</span>
                </p>
                <p className="flex justify-between">
                  <span>Сжато:</span>
                  <span className="font-semibold">{formatFileSize(result.compressedSize)}</span>
                </p>
                <div className={`pt-2 border-t ${darkMode ? 'border-green-700' : 'border-green-300'}`}>
                  <p className="flex justify-between items-center">
                    <span>Уменьшение:</span>
                    <span className="font-bold text-xl">
                      ↓ {(result.originalSize / result.compressedSize).toFixed(1)}x раз
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Кнопки */}
          <div className="flex gap-3 mt-4">
            <a
              href={result.downloadUrl}
              download={result.filename}
              className="flex-1 py-3 px-6 rounded-xl font-semibold text-center transition-all transform hover:scale-105 bg-green-600 hover:bg-green-700 text-white shadow-lg flex items-center justify-center gap-2"
            >
              <Download size={20} />
              Скачать сжатый файл
            </a>
            <button
              onClick={handleClear}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                darkMode
                  ? 'bg-slate-700 hover:bg-slate-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
              }`}
            >
              Новый файл
            </button>
          </div>
        </div>
      )}

      {/* Информация о сжатии */}
      {!file && (
        <div className={`rounded-xl p-6 ${
          darkMode ? 'bg-slate-800/30' : 'bg-purple-50'
        } border ${darkMode ? 'border-slate-700' : 'border-purple-200'}`}>
          <h3 className={`font-semibold mb-3 ${darkMode ? 'text-purple-300' : 'text-purple-900'}`}>
            💡 Как это работает?
          </h3>
          <ul className={`space-y-2 text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
            <li>✅ Сжатие до MP3 формата с оптимальными параметрами</li>
            <li>✅ Уменьшение размера в 5-10 раз без потери качества речи</li>
            <li>✅ Идеально для последующей транскрибации</li>
            <li>✅ Быстрая обработка больших файлов</li>
          </ul>
        </div>
      )}
    </div>
  )
}