module.exports = [
"[project]/.next-internal/server/app/api/transcribe/route/actions.js [app-rsc] (server actions loader, ecmascript)", ((__turbopack_context__, module, exports) => {

}),
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/os [external] (os, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("os", () => require("os"));

module.exports = mod;
}),
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[externals]/child_process [external] (child_process, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("child_process", () => require("child_process"));

module.exports = mod;
}),
"[project]/app/api/transcribe/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// ==========================================
// FILE: app/api/transcribe/route.ts (WITH CHUNKING)
// ==========================================
__turbopack_context__.s([
    "POST",
    ()=>POST,
    "preferredRegion",
    ()=>preferredRegion,
    "runtime",
    ()=>runtime
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$os__$5b$external$5d$__$28$os$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/os [external] (os, cjs)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/fs [external] (fs, cjs)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/path [external] (path, cjs)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$child_process__$5b$external$5d$__$28$child_process$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/child_process [external] (child_process, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$openai$40$6$2e$0$2e$1$2f$node_modules$2f$openai$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/openai@6.0.1/node_modules/openai/index.mjs [app-route] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$openai$40$6$2e$0$2e$1$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/openai@6.0.1/node_modules/openai/client.mjs [app-route] (ecmascript) <export OpenAI as default>");
;
;
;
;
;
;
const runtime = 'nodejs';
const preferredRegion = [
    'fra1',
    'arn1',
    'ams1'
];
const MAX_FILE_SIZE_MB = 20 // Безопасный лимит для одного чанка
;
const CHUNK_DURATION_SEC = 600 // 10 минут на чанк
;
function ndjson(out, obj) {
    out.enqueue(new TextEncoder().encode(JSON.stringify(obj) + '\n'));
}
function formatElapsedTime(ms) {
    const totalSec = Math.floor(ms / 1000);
    const min = Math.floor(totalSec / 60);
    const sec = totalSec % 60;
    return `${min}м ${sec}с`;
}
async function saveBlobToTmp(file) {
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const safeName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
    const p = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join((0, __TURBOPACK__imported__module__$5b$externals$5d2f$os__$5b$external$5d$__$28$os$2c$__cjs$29$__["tmpdir"])(), `${Date.now()}-${safeName}`);
    await __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["promises"].writeFile(p, buffer);
    return p;
}
async function getAudioDuration(filePath) {
    return new Promise((resolve, reject)=>{
        const proc = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$child_process__$5b$external$5d$__$28$child_process$2c$__cjs$29$__["spawn"])('ffprobe', [
            '-v',
            'error',
            '-show_entries',
            'format=duration',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            filePath
        ]);
        let output = '';
        proc.stdout.on('data', (data)=>{
            output += data.toString();
        });
        proc.on('close', (code)=>{
            if (code === 0) {
                const duration = parseFloat(output.trim());
                resolve(isNaN(duration) ? 0 : duration);
            } else {
                reject(new Error('ffprobe failed'));
            }
        });
    });
}
async function ffmpegToWav(inputPath) {
    const out = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join((0, __TURBOPACK__imported__module__$5b$externals$5d2f$os__$5b$external$5d$__$28$os$2c$__cjs$29$__["tmpdir"])(), `${__TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].parse(inputPath).name}.wav`);
    await new Promise((resolve, reject)=>{
        const args = [
            '-i',
            inputPath,
            '-vn',
            '-ac',
            '1',
            '-ar',
            '16000',
            '-f',
            'wav',
            out
        ];
        const proc = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$child_process__$5b$external$5d$__$28$child_process$2c$__cjs$29$__["spawn"])('ffmpeg', args);
        proc.on('error', reject);
        proc.on('close', (code)=>code === 0 ? resolve() : reject(new Error(`ffmpeg failed: ${code}`)));
    });
    return out;
}
async function splitAudioToChunks(inputPath, chunkSeconds) {
    const outDir = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join((0, __TURBOPACK__imported__module__$5b$externals$5d2f$os__$5b$external$5d$__$28$os$2c$__cjs$29$__["tmpdir"])(), `chunks-${Date.now()}`);
    await __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["promises"].mkdir(outDir, {
        recursive: true
    });
    await new Promise((resolve, reject)=>{
        const args = [
            '-i',
            inputPath,
            '-f',
            'segment',
            '-segment_time',
            chunkSeconds.toString(),
            '-c',
            'copy',
            __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(outDir, 'chunk%03d.wav')
        ];
        const proc = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$child_process__$5b$external$5d$__$28$child_process$2c$__cjs$29$__["spawn"])('ffmpeg', args);
        proc.on('error', reject);
        proc.on('close', (code)=>code === 0 ? resolve() : reject(new Error('ffmpeg split failed')));
    });
    const files = await __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["promises"].readdir(outDir);
    return files.filter((f)=>f.endsWith('.wav')).sort().map((f)=>__TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(outDir, f));
}
async function transcribeOpenAI(wavPath, language) {
    const client = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$openai$40$6$2e$0$2e$1$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__["default"]({
        apiKey: process.env.OPENAI_API_KEY
    });
    const resp = await client.audio.transcriptions.create({
        file: (0, __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["createReadStream"])(wavPath),
        model: 'whisper-1',
        language: language && language !== 'auto' ? language : undefined
    });
    return {
        text: resp.text
    };
}
async function maybeTranslate(text, target) {
    if (!target || !target.trim()) return text;
    const client = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$openai$40$6$2e$0$2e$1$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__["default"]({
        apiKey: process.env.OPENAI_API_KEY
    });
    const r = await client.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [
            {
                role: 'system',
                content: `Translate the following text to ${target}. Return only the translated text.`
            },
            {
                role: 'user',
                content: text
            }
        ],
        temperature: 0
    });
    return r.choices?.[0]?.message?.content?.toString?.() || text;
}
async function POST(request) {
    const stream = new ReadableStream({
        async start (controller) {
            const startTime = Date.now();
            let timer = null;
            const tempFiles = [];
            try {
                ndjson(controller, {
                    type: 'progress',
                    message: '⏳ Подготовка файла...'
                });
                const formData = await request.formData();
                const file = formData.get('file');
                const engine = formData.get('engine') || 'openai';
                const language = formData.get('language') || 'auto';
                const translateTo = formData.get('translateTo') || '';
                if (!file) {
                    ndjson(controller, {
                        type: 'error',
                        message: 'No file provided'
                    });
                    controller.close();
                    return;
                }
                const fileSizeMB = file.size / (1024 * 1024);
                const inputPath = await saveBlobToTmp(file);
                tempFiles.push(inputPath);
                ndjson(controller, {
                    type: 'progress',
                    message: '🔄 Конвертация в WAV...'
                });
                const wavPath = await ffmpegToWav(inputPath);
                tempFiles.push(wavPath);
                // Определяем длительность
                const duration = await getAudioDuration(wavPath);
                const needsChunking = fileSizeMB > MAX_FILE_SIZE_MB || duration > CHUNK_DURATION_SEC;
                let wavFiles = [];
                if (needsChunking) {
                    ndjson(controller, {
                        type: 'progress',
                        message: `📦 Разделение на части (файл ${fileSizeMB.toFixed(1)} MB, ${Math.floor(duration / 60)} минут)...`
                    });
                    wavFiles = await splitAudioToChunks(wavPath, CHUNK_DURATION_SEC);
                    tempFiles.push(...wavFiles);
                } else {
                    wavFiles = [
                        wavPath
                    ];
                }
                ndjson(controller, {
                    type: 'progress',
                    message: '🎙️ Распознавание речи...'
                });
                timer = setInterval(()=>{
                    ndjson(controller, {
                        type: 'progress',
                        message: `🎙️ Обработка... (${formatElapsedTime(Date.now() - startTime)})`
                    });
                }, 5000);
                // Транскрибация всех чанков
                let fullText = '';
                for(let i = 0; i < wavFiles.length; i++){
                    const chunkPath = wavFiles[i];
                    if (wavFiles.length > 1) {
                        ndjson(controller, {
                            type: 'progress',
                            message: `🎙️ Обработка части ${i + 1}/${wavFiles.length}... (${formatElapsedTime(Date.now() - startTime)})`
                        });
                    }
                    const result = await transcribeOpenAI(chunkPath, language);
                    // Добавляем пробел между чанками если текст не пустой
                    if (fullText && result.text) {
                        fullText += ' ';
                    }
                    fullText += result.text;
                    // Отправляем частичный результат
                    ndjson(controller, {
                        type: 'partial',
                        text: fullText
                    });
                }
                if (timer) {
                    clearInterval(timer);
                    timer = null;
                }
                // Перевод (если нужен)
                if (translateTo) {
                    ndjson(controller, {
                        type: 'progress',
                        message: '🌐 Перевод текста...'
                    });
                    fullText = await maybeTranslate(fullText, translateTo);
                }
                // Финальный результат
                ndjson(controller, {
                    type: 'final',
                    text: fullText
                });
                ndjson(controller, {
                    type: 'progress',
                    message: `✅ Готово! (${formatElapsedTime(Date.now() - startTime)})`
                });
                // Очистка всех временных файлов
                for (const tmpFile of tempFiles){
                    await __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["promises"].unlink(tmpFile).catch(()=>{});
                }
                // Удаляем директорию с чанками
                if (needsChunking && wavFiles.length > 0) {
                    const chunkDir = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].dirname(wavFiles[0]);
                    await __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["promises"].rm(chunkDir, {
                        recursive: true,
                        force: true
                    }).catch(()=>{});
                }
                controller.close();
            } catch (error) {
                console.error('Transcription error:', error);
                if (timer) clearInterval(timer);
                ndjson(controller, {
                    type: 'error',
                    message: error.message || 'Processing failed'
                });
                // Очистка при ошибке
                for (const tmpFile of tempFiles){
                    await __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["promises"].unlink(tmpFile).catch(()=>{});
                }
                controller.close();
            }
        }
    });
    return new Response(stream, {
        headers: {
            'Content-Type': 'application/x-ndjson; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    });
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__7d93b1e9._.js.map