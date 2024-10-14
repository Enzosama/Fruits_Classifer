// Custom JavaScript to improve the interface and add drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const fileUploader = document.getElementById('file-uploader');
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        fileUploader.classList.add('dragover');
    }

    function unhighlight() {
        fileUploader.classList.remove('dragover');
    }

    function handleDrop(e) {
        unhighlight();
        let dt = e.dataTransfer;
        let files = dt.files;
        if (files.length) {
            handleFiles(files);
        } else {
            // No files, try to get image URL
            let imageUrl = dt.getData('text/html');
            if (imageUrl) {
                let rex = /src="?([^"\s]+)"?\s*/;
                let url, res;
                url = rex.exec(imageUrl);
                if (url && url.length > 1) {
                    url = url[1];
                    handleImageUrl(url);
                }
            }
        }
    }

    function handleFiles(files) {
        ([...files]).forEach(uploadFile);
    }

    function uploadFile(file) {
        let imageType = /^image\//;
        if (!imageType.test(file.type)) {
            console.log('File is not an image.');
            return;
        }

        let formData = new FormData();
        formData.append('file', file);
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(() => {
            window.location.reload();
        })
        .catch(error => console.error('Error:', error));
    }

    function handleImageUrl(url) {
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'url=' + encodeURIComponent(url)
        })
        .then(() => {
            window.location.reload();
        })
        .catch(error => console.error('Error:', error));
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUploader.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        fileUploader.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileUploader.addEventListener(eventName, unhighlight, false);
    });

    fileUploader.addEventListener('drop', handleDrop, false);
});