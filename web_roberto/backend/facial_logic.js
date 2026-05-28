const { exec } = require('child_process');
const path = require('path');

const FACIAL_APP_DIR = path.join(__dirname, 'facial_app');

/**
 * Ejecuta un script de bash en el directorio facial_app.
 * @param {string} scriptName Nombre del archivo .sh
 */
function runFacialScript(scriptName) {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(FACIAL_APP_DIR, scriptName);
        console.log(`Ejecutando script: ${scriptPath}`);
        
        // Usamos bash explícitamente y nos aseguramos de estar en el directorio correcto
        exec(`bash ${scriptName}`, { cwd: FACIAL_APP_DIR }, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error ejecutando ${scriptName}:`, error);
                return reject({ error, stderr });
            }
            console.log(`Resultado de ${scriptName}:`, stdout);
            resolve(stdout);
        });
    });
}

module.exports = {
    processImages: () => runFacialScript('process_raw.sh'),
    trainModel: () => runFacialScript('train.sh'),
    openFaceApp: () => runFacialScript('face_app.sh'),
    verifyFrame: (base64Image) => {
        return new Promise((resolve, reject) => {
            const pythonPath = path.join(FACIAL_APP_DIR, 'venv/bin/python3');
            const scriptPath = path.join(FACIAL_APP_DIR, 'scripts/verify_web.py');
            
            const { spawn } = require('child_process');
            const py = spawn(pythonPath, [scriptPath], { cwd: FACIAL_APP_DIR });
            
            let output = '';
            py.stdout.on('data', (data) => output += data.toString());
            py.stderr.on('data', (data) => console.error(`Py Error: ${data}`));
            
            py.on('close', (code) => {
                try {
                    resolve(JSON.parse(output));
                } catch (e) {
                    reject({ error: "No se pudo procesar la respuesta del modelo", details: output });
                }
            });

            py.stdin.write(base64Image);
            py.stdin.end();
        });
    }
};
