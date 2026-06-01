const { exec, spawn } = require('child_process');
const path = require('path');

const FACIAL_APP_DIR = path.join(__dirname, 'facial_app');
const SCRIPTS_DIR = path.join(FACIAL_APP_DIR, 'scripts');

// Intentar usar el binario de Python dentro del venv si existe, de lo contrario usar el global
const VENV_PATH = process.platform === 'win32' 
    ? path.join(FACIAL_APP_DIR, 'venv', 'Scripts', 'python.exe')
    : path.join(FACIAL_APP_DIR, 'venv', 'bin', 'python3');

const fs = require('fs');
const PYTHON_EXE = fs.existsSync(VENV_PATH) ? VENV_PATH : (process.platform === 'win32' ? 'python' : 'python3');

/**
 * Gestión del Proceso Persistente de Verificación
 */
let verifierProcess = null;
let verifierCallbacks = [];

function getVerifierProcess() {
    if (verifierProcess && !verifierProcess.killed) return verifierProcess;

    const scriptPath = path.join(SCRIPTS_DIR, 'verify_web.py');
    console.log(`[Verifier] Iniciando proceso persistente con ${PYTHON_EXE}...`);
    
    verifierProcess = spawn(PYTHON_EXE, [scriptPath], {
        cwd: FACIAL_APP_DIR,
        shell: process.platform === 'win32'
    });

    let buffer = '';
    verifierProcess.stdout.on('data', (data) => {
        buffer += data.toString();
        // El script de Python envía un JSON por línea (con flush)
        if (buffer.includes('\n')) {
            const lines = buffer.split('\n');
            // Procesar todas las líneas completas excepto la última (que puede estar incompleta)
            for (let i = 0; i < lines.length - 1; i++) {
                const line = lines[i].trim();
                if (!line) continue;
                
                const callback = verifierCallbacks.shift();
                if (callback) {
                    try {
                        callback.resolve(JSON.parse(line));
                    } catch (e) {
                        callback.reject("Error parseando respuesta de Python");
                    }
                }
            }
            buffer = lines[lines.length - 1];
        }
    });

    verifierProcess.stderr.on('data', (data) => {
        console.error(`[PY VERIFIER ERROR] ${data}`);
    });

    verifierProcess.on('close', (code) => {
        console.log(`[Verifier] Proceso cerrado con código ${code}`);
        verifierProcess = null;
    });

    return verifierProcess;
}

/**
 * Ejecuta un script de Python (para procesos largos como procesar o entrenar)
 */
function runPythonScript(scriptName, args = []) {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(SCRIPTS_DIR, scriptName);
        console.log(`\n--- INICIANDO SCRIPT: ${scriptName} ---`);
        
        const pyProcess = spawn(PYTHON_EXE, [scriptPath, ...args], { 
            cwd: FACIAL_APP_DIR,
            shell: process.platform === 'win32'
        });

        let output = '';
        pyProcess.stdout.on('data', (data) => {
            const str = data.toString();
            process.stdout.write(`[PY STDOUT] ${str}`);
            output += str;
        });

        pyProcess.stderr.on('data', (data) => {
            process.stderr.write(`[PY STDERR] ${data}`);
        });

        pyProcess.on('close', (code) => {
            if (code === 0) resolve(output);
            else reject(`Fallo con código ${code}`);
        });
    });
}

module.exports = {
    processImages: () => runPythonScript('process_images.py'),
    
    trainModel: async () => {
        // Matar el proceso de verificación antes de entrenar para liberar memoria
        // y asegurar que se recargue el nuevo modelo después.
        if (verifierProcess) {
            console.log("[Verifier] Deteniendo proceso para permitir entrenamiento y recarga...");
            verifierProcess.kill();
            verifierProcess = null;
            verifierCallbacks = [];
        }
        return runPythonScript('train_model.py');
    },
    
    openFaceApp: () => {
        const scriptPath = path.join(SCRIPTS_DIR, 'face_app.py');
        const pyProcess = spawn(PYTHON_EXE, [scriptPath], { 
            cwd: FACIAL_APP_DIR,
            detached: true, 
            stdio: 'inherit',
            shell: process.platform === 'win32'
        });
        pyProcess.unref();
        return Promise.resolve("App abierta.");
    },

    verifyFrame: (base64Image) => {
        return new Promise((resolve, reject) => {
            const proc = getVerifierProcess();
            // Guardamos el callback para cuando Python responda a este frame específico
            verifierCallbacks.push({ resolve, reject });
            
            // Enviamos el base64 en una sola línea (Python leerá hasta el \n)
            // Eliminamos saltos de línea del base64 para evitar errores de lectura en Python
            const singleLineBase64 = base64Image.replace(/\r?\n|\r/g, "");
            proc.stdin.write(singleLineBase64 + '\n');
        });
    },

    saveRegistrationFrame: (name, base64Image, count) => {
        // El guardado sigue siendo individual (spawn) porque es ocasional
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(SCRIPTS_DIR, 'save_face.py');
            const pyProcess = spawn(PYTHON_EXE, [scriptPath, name, count], { 
                cwd: FACIAL_APP_DIR,
                shell: process.platform === 'win32'
            });

            let output = '';
            pyProcess.stdout.on('data', (data) => output += data.toString());
            pyProcess.on('close', (code) => {
                if (code === 0) resolve(JSON.parse(output));
                else reject("Fallo en guardado");
            });

            pyProcess.stdin.write(base64Image);
            pyProcess.stdin.end();
        });
    }
};
