// script.js
document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const resultSection = document.getElementById("result");
    const outputText = document.getElementById("outputText");
    const outputClauses = document.getElementById("outputClauses");

    try {
        // Display a loading state
        outputText.textContent = "Extracting text, please wait...";
        outputClauses.innerHTML = "<li>Extracting key clauses, please wait...</li>";
        resultSection.classList.remove("hidden");

        const response = await fetch("http://127.0.0.1:8000/extract-text/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();

        // Display extracted text
        outputText.textContent = result.extracted_text;

        // Display key clauses
        outputClauses.innerHTML = ""; // Clear previous content
        result.key_clauses.forEach((clause) => {
            const listItem = document.createElement("li");
            listItem.textContent = clause;
            outputClauses.appendChild(listItem);
        });
    } catch (error) {
        alert(`An error occurred: ${error.message}`);
        resultSection.classList.add("hidden");
    }
});
