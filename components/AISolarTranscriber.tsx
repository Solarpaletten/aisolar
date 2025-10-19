'use client'
import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Upload, FileAudio, FileVideo, Clock, HardDrive, Loader2, CheckCircle2, XCircle, Play, Trash2, Copy, Sun, Moon, Globe, Zap, Server, Settings, Languages } from 'lucide-react'
import { textToSRT } from '@/lib/exportSRT'

interface HistoryItem {
  id: string
  name: string
  text: string
  date: string
  language?: string
  engine?: string
}

const AUDIO_FORMATS = ['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'wma'];
const VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'mpeg', 'mpg'];


export default function AISolarTranscriber() {
  const [file, setFile] = useState<File | null>(null)
  const [videoPreview, setVideoPreview] = useState<string>('')
  const [transcript, setTranscript] = useState('')
  const [progress, setProgress] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [darkMode, setDarkMode] = useState(true)
  const [isDragging, setIsDragging] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [history, setHistory] = useState<HistoryItem[]>([])

  // Новые состояния для медиа-информации
  const [mediaType, setMediaType] = useState<'audio' | 'video' | null>(null);
  const [mediaDuration, setMediaDuration] = useState<number | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  const [engine, setEngine] = useState<'openai' | 'local'>('openai')
  const [language, setLanguage] = useState('auto')
  const [autoTranslate, setAutoTranslate] = useState(false)
  const [targetLanguage, setTargetLanguage] = useState('ru')
  const [enableSegmentation, setEnableSegmentation] = useState(false)
  const [enableSpeakers, setEnableSpeakers] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const saved = localStorage.getItem('aisolar-history')
    if (saved) {
      try {
        setHistory(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load history', e)
      }
    }
  }, [])

  // Вспомогательные функции
  const detectMediaType = (filename: string): 'audio' | 'video' => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    if (AUDIO_FORMATS.includes(ext)) return 'audio';
    if (VIDEO_FORMATS.includes(ext)) return 'video';
    return 'video';
  };

  const formatDuration = (seconds: number | null): string => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const estimateProcessingTime = (duration: number | null): string => {
    if (!duration) return 'несколько секунд';
    const estimatedMinutes = Math.ceil((duration / 60) * 0.2);
    if (estimatedMinutes < 1) return '~1 минуту';
    if (estimatedMinutes === 1) return '~1 минуту';
    if (estimatedMinutes < 5) return `~${estimatedMinutes} минуты`;
    return `~${estimatedMinutes} минут`;
  };

  const saveToHistory = useCallback((name: string, text: string) => {
    const newEntry: HistoryItem = {
      id: Date.now().toString(),
      name,
      text,
      date: new Date().toISOString(),
      language,
      engine
    }
    const updated = [newEntry, ...history].slice(0, 10)
    setHistory(updated)
    localStorage.setItem('aisolar-history', JSON.stringify(updated))
  }, [history, language, engine])

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setVideoPreview(URL.createObjectURL(selectedFile));

    // Определяем тип файла
    const type = detectMediaType(selectedFile.name);
    setMediaType(type);

    // Сбрасываем предыдущие данные
    setTranscript('');
    setMediaDuration(null);
    setProcessingStatus('');

    // Получаем длительность медиа
    const mediaElement = document.createElement(type) as HTMLAudioElement | HTMLVideoElement;
    mediaElement.src = URL.createObjectURL(selectedFile);
    mediaElement.onloadedmetadata = () => {
      setMediaDuration(mediaElement.duration);
      URL.revokeObjectURL(mediaElement.src);
    };
  };

  const startTranscription = async () => {
    if (!file) return

    setLoading(true)
    setError('')
    setSuccess(false)
    setProgress('Подготовка...')
    setProcessingStatus('⏳ Подготовка файла...');

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('engine', engine)
      formData.append('language', language)
      formData.append('enableSegmentation', String(enableSegmentation))
      formData.append('enableSpeakers', String(enableSpeakers))
      formData.append('translateTo', autoTranslate && targetLanguage ? targetLanguage : '')

      setProcessingStatus('🔄 Конвертация файла...');

      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData
      })

      setProcessingStatus(
        `🎙️ Транскрибация... ${mediaDuration ? `(~${estimateProcessingTime(mediaDuration)})` : ''}`
      );

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Превышен лимит запросов. Попробуйте позже.')
        }
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let finalText = ''

      if (reader) {
        while (true) {
          const { value, done } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n').filter(Boolean)

          for (const line of lines) {
            try {
              const data = JSON.parse(line)

              if (data.type === 'progress') {
                setProgress(data.message)
              } else if (data.type === 'partial') {
                setTranscript(data.text)
              } else if (data.type === 'final') {
                finalText = data.text
                setTranscript(data.text)
              } else if (data.type === 'error') {
                throw new Error(data.message)
              }
            } catch (e) {
              if (e instanceof Error && !e.message.includes('JSON')) {
                throw e
              }
            }
          }
        }
      }

      setSuccess(true)
      setProgress('Транскрибирование завершено! ✓')
      setProcessingStatus('✅ Готово!');

      if (finalText) {
        saveToHistory(file.name, finalText)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка'
      setError(errorMessage)
      setProcessingStatus('❌ Ошибка обработки');
    } finally {
      setLoading(false)
      setTimeout(() => setProcessingStatus(''), 3000);
    }
  }

  const downloadFile = (name: string, content: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900' : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50'}`}>
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} flex items-center gap-3`}>
              <span className="text-5xl">🌞</span>
              AISOLAR
              <span className={`text-sm px-3 py-1 rounded-full ${darkMode ? 'bg-purple-500/20 text-purple-300' : 'bg-purple-100 text-purple-700'}`}>
                v2.0
              </span>
            </h1>
            <p className={`mt-2 ${darkMode ? 'text-purple-300' : 'text-purple-600'}`}>
              AI-транскрибация видео в текст
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-3 rounded-xl transition-all ${darkMode ? 'bg-white/10 hover:bg-white/20 text-purple-300' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'}`}
            >
              <Settings size={24} />
            </button>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-3 rounded-xl transition-all ${darkMode ? 'bg-white/10 hover:bg-white/20 text-yellow-300' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'}`}
            >
              {darkMode ? <Sun size={24} /> : <Moon size={24} />}
            </button>
          </div>
        </div>

        {showSettings && (
          <div className={`rounded-2xl p-6 ${darkMode ? 'bg-white/5 border border-white/10' : 'bg-white shadow-lg'}`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Настройки транскрибации
            </h3>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  Движок
                </label>
                <div className="flex gap-3">
                  <button
                    onClick={() => setEngine('openai')}
                    className={`flex-1 p-3 rounded-xl transition-all ${engine === 'openai'
                      ? darkMode ? 'bg-purple-500 text-white' : 'bg-purple-600 text-white'
                      : darkMode ? 'bg-white/5 hover:bg-white/10 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                      }`}
                  >
                    <Zap className="inline mr-2" size={18} />
                    OpenAI
                  </button>
                  <button
                    onClick={() => setEngine('local')}
                    className={`flex-1 p-3 rounded-xl transition-all ${engine === 'local'
                      ? darkMode ? 'bg-purple-500 text-white' : 'bg-purple-600 text-white'
                      : darkMode ? 'bg-white/5 hover:bg-white/10 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                      }`}
                  >
                    <Server className="inline mr-2" size={18} />
                    Local
                  </button>
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  <Globe className="inline mr-1" size={16} />
                  Язык
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className={`w-full p-3 rounded-xl ${darkMode ? 'bg-white/5 text-white' : 'bg-gray-100 text-gray-900'} outline-none`}
                >
                  <option value="auto">Авто</option>
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                  <option value="uk">Українська</option>
                  <option value="pl">Polski</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoTranslate}
                    onChange={(e) => setAutoTranslate(e.target.checked)}
                    className="w-5 h-5 rounded accent-purple-500"
                  />
                  <span className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    <Languages className="inline mr-1" size={16} />
                    Перевод
                  </span>
                </label>
                {autoTranslate && (
                  <select
                    value={targetLanguage}
                    onChange={(e) => setTargetLanguage(e.target.value)}
                    className={`w-full mt-2 p-2 rounded-lg ${darkMode ? 'bg-white/5 text-white' : 'bg-gray-100 text-gray-900'} outline-none text-sm`}
                  >
                    <option value="ru">→ Русский</option>
                    <option value="en">→ English</option>
                    <option value="uk">→ Українська</option>
                  </select>
                )}
              </div>

              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enableSegmentation}
                    onChange={(e) => setEnableSegmentation(e.target.checked)}
                    className="w-5 h-5 rounded accent-purple-500"
                  />
                  <span className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Сегментация
                  </span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enableSpeakers}
                    onChange={(e) => setEnableSpeakers(e.target.checked)}
                    className="w-5 h-5 rounded accent-purple-500"
                  />
                  <span className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Спикеры
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={(e) => { e.preventDefault(); setIsDragging(false) }}
              onDrop={(e) => {
                e.preventDefault()
                setIsDragging(false)
                const f = e.dataTransfer.files[0]
                if (f) handleFileSelect(f)
              }}
              className={`relative rounded-2xl border-2 border-dashed transition-all p-12 text-center cursor-pointer ${isDragging
                ? darkMode ? 'border-purple-400 bg-purple-500/20' : 'border-purple-500 bg-purple-100'
                : darkMode ? 'border-purple-500/50 bg-white/5' : 'border-gray-300 bg-white'
                }`}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*,audio/*,.avi,.mp3,.wav,.m4a,.ogg,.aac"
                onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (f) handleFileSelect(f)
                }}
                className="hidden"
              />

              <div className="space-y-4">
                <div className={`mx-auto w-20 h-20 rounded-full flex items-center justify-center ${darkMode ? 'bg-purple-500/20' : 'bg-purple-100'}`}>
                  {file ? (
                    mediaType === 'audio' ? <FileAudio className={darkMode ? 'text-purple-300' : 'text-purple-600'} size={40} /> : <FileVideo className={darkMode ? 'text-purple-300' : 'text-purple-600'} size={40} />
                  ) : (
                    <Upload className={darkMode ? 'text-purple-300' : 'text-purple-600'} size={40} />
                  )}
                </div>

                <div>
                  <p className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {file ? file.name : 'Перетащите видео или аудио'}
                  </p>
                  <p className={`mt-2 text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    AVI, MP4, MOV, MP3, WAV, OGG • До 500MB
                  </p>
                </div>
              </div>
            </div>

            {/* БЛОК С ИНФОРМАЦИЕЙ О ФАЙЛЕ */}
            {file && (
              <div className={`mb-4 space-y-2 rounded-xl p-4 ${darkMode ? 'bg-white/5' : 'bg-gray-50'}`}>
                {/* Тип файла и основная информация */}
                <div className={`flex items-center gap-4 text-sm ${darkMode ? 'text-purple-200/80' : 'text-gray-600'}`}>
                  <div className="flex items-center gap-1.5">
                    {mediaType === 'audio' ? (
                      <FileAudio className="w-4 h-4" />
                    ) : (
                      <FileVideo className="w-4 h-4" />
                    )}
                    <span className="capitalize font-medium">{mediaType === 'audio' ? 'Аудио' : 'Видео'}</span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <HardDrive className="w-4 h-4" />
                    <span>{formatFileSize(file.size)}</span>
                  </div>

                  {mediaDuration && (
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4" />
                      <span>Длительность: {formatDuration(mediaDuration)}</span>
                    </div>
                  )}
                </div>

                {/* Статус обработки */}
                {processingStatus && (
                  <div className={`flex items-center gap-2 text-sm rounded-lg px-3 py-2 ${darkMode ? 'bg-purple-500/20 border border-purple-400/30 text-purple-200' : 'bg-purple-100 border border-purple-300 text-purple-700'}`}>
                    <span>{processingStatus}</span>
                    {loading && mediaDuration && (
                      <span className={darkMode ? 'text-purple-200/60' : 'text-purple-600/60'}>
                        • Ожидание: {estimateProcessingTime(mediaDuration)}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}

            {videoPreview && (
              <div className="rounded-xl overflow-hidden">
                {mediaType === 'audio' ? (
                  <audio src={videoPreview} controls className="w-full" />
                ) : (
                  <video src={videoPreview} controls className="w-full" style={{ maxHeight: '300px' }} />
                )}
              </div>
            )}

            {file && (
              <div className="flex gap-3">
                <button
                  onClick={startTranscription}
                  disabled={loading}
                  className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all ${loading
                    ? 'bg-gray-600 cursor-not-allowed'
                    : darkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                    }`}
                >
                  {loading ? <><Loader2 className="inline animate-spin mr-2" size={20} />Обработка...</> : <><Play className="inline mr-2" size={20} />Транскрибировать</>}
                </button>
                <button
                  onClick={() => {
                    setFile(null)
                    setVideoPreview('')
                    setTranscript('')
                    setError('')
                    setSuccess(false)
                    setMediaType(null)
                    setMediaDuration(null)
                    setProcessingStatus('')
                  }}
                  disabled={loading}
                  className={`px-6 py-4 rounded-xl font-semibold ${darkMode ? 'bg-red-500/20 text-red-300' : 'bg-red-100 text-red-700'}`}
                >
                  <Trash2 className="inline mr-2" size={20} />
                  Очистить
                </button>
              </div>
            )}

            {progress && (
              <div className={`rounded-xl p-4 ${darkMode ? 'bg-blue-500/20 border border-blue-500/30' : 'bg-blue-50'}`}>
                <div className="flex items-center gap-3">
                  {loading && <Loader2 className="animate-spin" size={20} />}
                  {success && <CheckCircle2 className="text-green-500" size={20} />}
                  <p>{progress}</p>
                </div>
              </div>
            )}

            {error && (
              <div className={`rounded-xl p-4 ${darkMode ? 'bg-red-500/20' : 'bg-red-50'}`}>
                <div className="flex items-center gap-3">
                  <XCircle className="text-red-500" size={20} />
                  <p>{error}</p>
                </div>
              </div>
            )}

            {transcript && (
              <div className={`rounded-2xl overflow-hidden ${darkMode ? 'bg-white/5' : 'bg-white shadow-lg'}`}>
                <div className={`p-4 flex justify-between ${darkMode ? 'bg-white/10' : 'bg-gray-100'}`}>
                  <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Результат</h3>
                  <div className="flex gap-2">
                    <button onClick={() => navigator.clipboard.writeText(transcript)} className="p-2 rounded-lg hover:bg-white/10">
                      <Copy size={18} />
                    </button>
                    <button onClick={() => downloadFile('transcript.txt', transcript, 'text/plain')} className="px-3 py-1 rounded-lg text-sm hover:bg-white/10">TXT</button>
                    <button onClick={() => downloadFile('transcript.json', JSON.stringify({ text: transcript }, null, 2), 'application/json')} className="px-3 py-1 rounded-lg text-sm hover:bg-white/10">JSON</button>
                    <button onClick={() => downloadFile('transcript.srt', textToSRT(transcript), 'text/plain')} className="px-3 py-1 rounded-lg text-sm hover:bg-white/10">SRT</button>
                  </div>
                </div>
                <textarea
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  className={`w-full h-96 p-6 resize-none outline-none ${darkMode ? 'bg-slate-900/50 text-gray-100' : 'bg-white text-gray-900'}`}
                />
              </div>
            )}
          </div>

          <div>
            <div className={`rounded-2xl p-6 ${darkMode ? 'bg-white/5' : 'bg-white shadow-lg'}`}>
              <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>История</h3>
              {history.length === 0 ? (
                <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Пусто</p>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => {
                        setTranscript(item.text)
                        setSuccess(true)
                      }}
                      className={`p-3 rounded-xl cursor-pointer ${darkMode ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'}`}
                    >
                      <p className={`text-sm font-medium truncate ${darkMode ? 'text-white' : 'text-gray-900'}`}>{item.name}</p>
                      <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        {new Date(item.date).toLocaleDateString('ru-RU')}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}