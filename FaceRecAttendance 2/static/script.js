function showAlert(message, type) {
    const alertBox = document.getElementById('alert');
    alertBox.innerHTML = message;
    alertBox.className = 'alert ' + (type === 'success' ? 'success' : 'error');
    alertBox.style.display = 'block';

    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 3000); // Hide after 3 seconds
}

function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const studentNameInput = document.getElementById('studentNameInput').value;
    
    if (!fileInput.files.length || !studentNameInput) {
        showAlert('Please select a file and enter a name or roll number.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.message, 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error uploading file.', 'error');
    });
}

document.getElementById('captureBtn').addEventListener('click', () => {
    fetch('/capture', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message, data.message.includes('No match') ? 'error' : 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error capturing image.', 'error');
        });
});

document.getElementById('shutdownBtn').addEventListener('click', () => {
    fetch('/shutdown', { method: 'POST' })
        .then(response => {
            showAlert('Camera shut down successfully.', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error shutting down camera.', 'error');
        });
});
