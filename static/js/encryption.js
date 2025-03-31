// Función para cifrar el archivo antes de ser subido
function encryptFile(file, secretKey) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = function() {
            const fileData = reader.result;
            const encryptedData = encrypt(fileData, secretKey);
            resolve(new Blob([encryptedData], { type: file.type }));
        };

        reader.onerror = function(error) {
            reject(error);
        };

        reader.readAsArrayBuffer(file);
    });
}

// Función de cifrado (simple, puedes usar una librería como CryptoJS o algo más avanzado)
function encrypt(data, secretKey) {
    const encodedData = new TextEncoder().encode(data);
    const encryptedData = encodedData.map(byte => byte ^ secretKey.charCodeAt(0)); // Cifrado simple XOR
    return new Uint8Array(encryptedData);
}

// Subir archivo cifrado
const uploadForm = document.getElementById('upload-form');
uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    const secretKey = "your-secret-key"; // Define tu clave secreta aquí

    if (file) {
        const encryptedFile = await encryptFile(file, secretKey);

        // Subir el archivo cifrado al servidor
        const formData = new FormData();
        formData.append("file", encryptedFile, file.name);

        fetch('/upload', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
          .then(data => alert('Archivo subido con éxito'))
          .catch(error => alert('Error al subir el archivo'));
    }
});
