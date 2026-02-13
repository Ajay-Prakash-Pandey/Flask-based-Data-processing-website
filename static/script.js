async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const resultBox = document.getElementById("result");
    const output = document.getElementById("output");

    if (!fileInput.files.length) {
        output.textContent = "Error: Please select a CSV file!";
        resultBox.style.display = "block";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/api/data/upload", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            sessionStorage.setItem('processingResult', JSON.stringify(data));
            window.location.href = '/result';
        } else {
            output.textContent = "Error: " + (data.error || "Unknown error");
            resultBox.style.display = "block";
        }
    } catch (error) {
        output.textContent = "Error: " + error.message;
        resultBox.style.display = "block";
    }
}
