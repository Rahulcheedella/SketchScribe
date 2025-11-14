document.addEventListener("DOMContentLoaded", () => {
    
    // Get all the elements
    const audioForm = document.getElementById("audio-form");
    const transcribeButton = document.getElementById("transcribe-button");
    const generateButton = document.getElementById("generate-button");
    const audioFileInput = document.getElementById("audio-file");
    const promptInput = document.getElementById("prompt-input");
    
    const loadingDiv = document.getElementById("loading");
    const loadingText = document.getElementById("loading-text");
    const generatedImage = document.getElementById("generated-image");

    /**
     * Handle the audio transcription
     */
    audioForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Stop form from submitting
        
        const file = audioFileInput.files[0];
        if (!file) {
            alert("Please select an audio file first.");
            return;
        }

        const language = document.querySelector('input[name="language"]:checked').value;

        // Show loading spinner
        showLoading("Transcribing audio...");
        generatedImage.src = ""; // Clear old image

        const formData = new FormData();
        formData.append("audioFile", file);
        formData.append("language", language);

        try {
            const response = await fetch("/transcribe-audio", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                // Populate the text area with the result
                promptInput.value = data.prompt;
                // You could also display `data.transcribed_text` in another box if you want
            } else {
                throw new Error(data.error || "Transcription failed.");
            }
        } catch (error) {
            alert("Error: " + error.message);
        } finally {
            hideLoading();
        }
    });

    /**
     * Handle the image generation
     */
    generateButton.addEventListener("click", async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert("Please type a prompt or transcribe audio first.");
            return;
        }

        // Show loading spinner
        showLoading("Generating image... This may take a minute.");
        generatedImage.src = ""; // Clear old image

        try {
            const response = await fetch("/generate-image", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt: prompt }),
            });

            const data = await response.json();

            if (response.ok) {
                // Set the image source
                // Add timestamp to bust browser cache
                generatedImage.src = data.image_url + "?t=" + new Date().getTime();
            } else {
                throw new Error(data.error || "Image generation failed.");
            }
        } catch (error) {
            alert("Error: " + error.message);
        } finally {
            hideLoading();
        }
    });

    // --- Helper Functions ---
    function showLoading(message) {
        loadingText.textContent = message;
        loadingDiv.classList.remove("hidden");
        transcribeButton.disabled = true;
        generateButton.disabled = true;
    }

    function hideLoading() {
        loadingDiv.classList.add("hidden");
        transcribeButton.disabled = false;
        generateButton.disabled = false;
    }

    generateButton.addEventListener("click", async () => {
    const prompt = promptInput.value.trim();
    const language = document.querySelector('input[name="language"]:checked').value;

    if (!prompt) {
        alert("Please type a prompt or transcribe audio first.");
        return;
    }

    showLoading("Generating image... This may take a minute.");
    generatedImage.src = "";

    try {
        const response = await fetch("/generate-image", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt, language: language }),
        });

        const data = await response.json();

        if (response.ok && data.image_url) {
            generatedImage.src = data.image_url + "?t=" + new Date().getTime();
        } else {
            throw new Error(data.error || "Image generation failed.");
        }
    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        hideLoading();
    }
});


});