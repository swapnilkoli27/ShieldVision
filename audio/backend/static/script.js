let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let mediaStream;

async function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(mediaStream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            const audioURL = URL.createObjectURL(audioBlob);
            sendToBackend(audioBlob, audioURL);

            document.querySelector(".fa-microphone").style.color = "black";
            stopMicrophone();
        };

        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        document.querySelector(".fa-microphone").style.color = "red";

    } catch (error) {
        console.error("Error accessing microphone:", error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        isRecording = false;
    }
}

function stopMicrophone() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
}

document.getElementById("audioUpload").addEventListener("change", function (event) {
    let file = event.target.files[0];
    if (file) {
        let audioURL = URL.createObjectURL(file);
        sendToBackend(file, audioURL);
    }
});

function sendToBackend(file, audioURL) {
    let formData = new FormData();
    formData.append("file", file);

    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        addAudioToChat(audioURL, data.result);
    })
    .catch(error => {
        console.error("Error:", error);
        addAudioToChat(audioURL, "Error processing");
    });
}

function addAudioToChat(audioURL, resultText) {
    let audioContainer = document.createElement("div");
    let audioElement = document.createElement("audio");
    audioElement.src = audioURL;
    audioElement.controls = true;
    audioElement.style.width = "45%";

    let result = document.createElement("h4");
    result.textContent = "Prediction: " + resultText;
    result.style.color = (resultText.includes("Real") ? "green" : "red");

    let deleteBtn = document.createElement("span");
    deleteBtn.textContent = "Delete";
    deleteBtn.classList.add("delete-btn");
    deleteBtn.onclick = function () {
        audioContainer.remove();
    };

    audioContainer.appendChild(audioElement);
    audioContainer.appendChild(result);
    audioContainer.appendChild(deleteBtn);

    document.querySelector(".first3-box").appendChild(audioContainer);
}
