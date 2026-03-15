import { NextRequest } from 'next/server'
import { writeFile, readFile, unlink } from 'fs/promises'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'
import { existsSync } from 'fs'

const execAsync = promisify(exec)

export const runtime = 'nodejs'
export const maxDuration = 300 // 5 минут максимум

export async function POST(request: NextRequest) {
    const inputPath = path.join('/tmp', `input-${Date.now()}`)
    const outputPath = path.join('/tmp', `compressed-${Date.now()}.mp3`)

    try {
        // Получаем файл
        const formData = await request.formData()
        const file = formData.get('file') as File

        if (!file) {
            return Response.json({ error: 'Файл не найден' }, { status: 400 })
        }

        // Сохраняем оригинальный файл
        const buffer = Buffer.from(await file.arrayBuffer())
        const originalSize = buffer.length

        // Определяем расширение файла
        const fileExt = file.name.split('.').pop()?.toLowerCase() || 'unknown'
        const inputFilePath = `${inputPath}.${fileExt}`

        await writeFile(inputFilePath, buffer)

        console.log(`📁 Файл сохранён: ${inputFilePath} (${(originalSize / 1024 / 1024).toFixed(2)} MB)`)

        // Сжимаем через ffmpeg с оптимальными параметрами для речи
        const ffmpegCommand = [
            'ffmpeg',
            '-i', `"${inputFilePath}"`,
            '-vn',                    // Убрать видео
            '-ar', '16000',           // 16 kHz
            '-ac', '1',               // Mono
            '-codec:a', 'libmp3lame',
            '-b:a', '12k',            // 12 kbps для максимального сжатия
            '-f', 'mp3',              // Принудительно MP3
            '-y',
            `"${outputPath}"`
        ].join(' ')

        console.log(`🗜️ Запуск сжатия: ${ffmpegCommand}`)

        try {
            const { stdout, stderr } = await execAsync(ffmpegCommand)
            if (stderr) {
                console.log('FFmpeg stderr:', stderr)
            }
        } catch (execError: any) {
            console.error('❌ Ошибка ffmpeg:', execError.stderr || execError.message)
            throw new Error(`Ошибка сжатия: ${execError.message}`)
        }

        // Проверяем что файл создан
        if (!existsSync(outputPath)) {
            throw new Error('Сжатый файл не был создан')
        }

        // Читаем сжатый файл
        const compressedBuffer = await readFile(outputPath)
        const compressedSize = compressedBuffer.length

        console.log(`✅ Сжатие завершено:`)
        console.log(`   Оригинал: ${(originalSize / 1024 / 1024).toFixed(2)} MB`)
        console.log(`   Сжато: ${(compressedSize / 1024 / 1024).toFixed(2)} MB`)
        console.log(`   Уменьшение: ${(originalSize / compressedSize).toFixed(1)}x раз`)

        // Удаляем временные файлы
        try {
            await unlink(inputFilePath)
            await unlink(outputPath)
        } catch (cleanupError) {
            console.error('⚠️ Ошибка очистки временных файлов:', cleanupError)
        }

        // Возвращаем сжатый файл
        return new Response(compressedBuffer, {
            headers: {
                'Content-Type': 'audio/mpeg',
                'Content-Disposition': `attachment; filename="compressed-${file.name.split('.')[0]}.mp3"`,
                'X-Original-Size': String(originalSize),
                'X-Compressed-Size': String(compressedSize),
                'Cache-Control': 'no-store'
            }
        })

    } catch (error: any) {
        console.error('❌ Критическая ошибка сжатия:', error)

        // Очищаем временные файлы в случае ошибки
        try {
            const files = [
                inputPath,
                `${inputPath}.mp3`,
                `${inputPath}.mp4`,
                `${inputPath}.m4a`,
                `${inputPath}.wav`,
                `${inputPath}.ogg`,
                `${inputPath}.avi`,
                `${inputPath}.mov`,
                `${inputPath}.mkv`,
                outputPath
            ]

            for (const file of files) {
                if (existsSync(file)) {
                    await unlink(file)
                }
            }
        } catch (cleanupError) {
            console.error('⚠️ Ошибка очистки после сбоя:', cleanupError)
        }

        return Response.json(
            { error: error.message || 'Ошибка при сжатии файла' },
            { status: 500 }
        )
    }
}