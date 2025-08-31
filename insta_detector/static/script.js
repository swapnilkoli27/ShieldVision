function openUploadModal() {
    document.getElementById("uploadModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("uploadModal").style.display = "none";
}

function openPhotoPicker() {
    document.getElementById("photoInput").click();
    closeModal();
}

function openVideoPicker() {
    document.getElementById("videoInput").click();
    closeModal();
}
function addText() {
    const chatContainer = document.createElement("div");
    chatContainer.id = "chatContainer";

    const input = document.createElement("textarea");
    input.id = "chatInput";
    input.placeholder = "Type your message...";

    const postButton = document.createElement("button");
    postButton.innerText = "Post";
    postButton.id = "postButton";

    const deleteButton = document.createElement("button");
    deleteButton.innerText = "Delete";
    deleteButton.id = "deleteButton";

    postButton.addEventListener("click", function () {
        const message = input.value.trim();
        if (message !== "") {
            const messageContainer = document.createElement("div");
            messageContainer.classList.add("messageContainer");

            const messageBox = document.createElement("p");
            messageBox.innerText = message;
            messageBox.classList.add("messageText");

            const deletePostButton = document.createElement("button");
            deletePostButton.innerText = "Delete";
            deletePostButton.classList.add("deletePostButton");
            deletePostButton.addEventListener("click", function () {
                messageContainer.remove();
            });

            messageContainer.appendChild(messageBox);
            messageContainer.appendChild(deletePostButton);
            document.body.appendChild(messageContainer);
        }
        chatContainer.remove(); 
    });

    deleteButton.addEventListener("click", function () {
        chatContainer.remove();
    });

    chatContainer.appendChild(input);
    chatContainer.appendChild(postButton);
    chatContainer.appendChild(deleteButton);
    document.body.appendChild(chatContainer);
}



function postMessage(messageText) {
    const messagesDiv = document.getElementById("messages");


    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message-box");

  
    const messageSpan = document.createElement("span");
    messageSpan.innerText = messageText;



    const deleteBtn = document.createElement("button");
    deleteBtn.innerText = "Delete";
    deleteBtn.onclick = function () {
        messagesDiv.removeChild(messageDiv);
    };

    messageDiv.appendChild(messageSpan);
    messageDiv.appendChild(deleteBtn);
    messagesDiv.appendChild(messageDiv);
}


function startCamera() {
    closeModal();
    let video = document.getElementById("cameraStream");
    let captureButton = document.getElementById("captureButton");

    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            video.style.display = "block";
            captureButton.style.display = "block";
            video.play();
        })
        .catch(() => {
            alert("Camera access denied!");
        });
}


function capturePhoto() {
    let video = document.getElementById("cameraStream");
    let canvas = document.getElementById("canvas");
    let context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    let imageData = canvas.toDataURL("image/png");
    previewCapturedImage(imageData);


    video.srcObject.getTracks().forEach(track => track.stop());
    video.style.display = "none";
    document.getElementById("captureButton").style.display = "none";
    
}

function previewCapturedImage(imageData) {
    let previewImage = document.getElementById("previewImage");
    previewImage.src = imageData;
    previewImage.style.display = "block";
    
    document.getElementById("postPreview").style.display = "block";
}



function previewPost(event, type) {
    let file = event.target.files[0];
    if (!file) return;

    let reader = new FileReader();
    reader.onload = function (e) {
        let previewImage = document.getElementById("previewImage");
        let previewVideo = document.getElementById("previewVideo");

        if (type === "image") {
            previewImage.src = e.target.result;
            previewImage.style.display = "block";
            previewVideo.style.display = "none";
        } else if (type === "video") {
            previewVideo.src = e.target.result;  
            previewVideo.style.display = "block";
            previewVideo.controls = true;
            previewImage.style.display = "none";
        }

        document.getElementById("postPreview").style.display = "block";
    };
    reader.readAsDataURL(file);
}

async function submitPost() {
    const previewImage = document.getElementById("previewImage");
    const previewVideo = document.getElementById("previewVideo");
    const caption = document.getElementById("captionInput").value.trim();
    const postContainer = document.getElementById("posts");

    const username = "user_123";
    const profilePic = "static/assets/prop.jpg";

    const newPost = document.createElement("div");
    newPost.classList.add("post");

    const userInfo = document.createElement("div");
    userInfo.classList.add("user-info");

    const profileImg = document.createElement("img");
    profileImg.src = profilePic;
    profileImg.classList.add("profile-pic");

    const usernameElement = document.createElement("span");
    usernameElement.classList.add("username");
    usernameElement.innerText = username;

    userInfo.appendChild(profileImg);
    userInfo.appendChild(usernameElement);

    const postContent = document.createElement("div");
    postContent.classList.add("post-content");

    const captionElem = document.createElement("p");
    captionElem.classList.add("caption");
    captionElem.innerText = caption;

    let fileType = null;
    let mediaBlob = null;

    if (previewImage.style.display === "block") {
        const imageBlob = await fetch(previewImage.src).then(res => res.blob());
        mediaBlob = imageBlob;
        fileType = "image";
    } else if (previewVideo.style.display === "block") {
        const videoBlob = await fetch(previewVideo.src).then(res => res.blob());
        mediaBlob = videoBlob;
        fileType = "video";
    }

    // Send to Flask for analysis
    const formData = new FormData();
    formData.append("text", caption); // Always send, even if empty
    if (fileType === "image") formData.append("image", mediaBlob, "upload.png");
    if (fileType === "video") formData.append("video", mediaBlob, "upload.mp4");

    const resultBox = document.createElement("div");
    resultBox.classList.add("messageText");
    resultBox.innerText = "Analyzing...";

    try {
        const res = await fetch("/analyze_post", {
            method: "POST",
            body: formData,
        });
    
        const data = await res.json();
        let results = [];
    
        if (data.text_result) {
            results.push(`Text: ${data.text_result}`);
        }
        if (data.image_result) {
            results.push(`Image: ${data.image_result}`);
        }
        if (data.video_result) {
            results.push(`Video: ${data.video_result}`);
        }
    
        resultBox.innerText = results.join(" | ");
    } catch (err) {
        resultBox.innerText = "❌ Analysis failed!";
        console.error(err);
    }
    

   
    if (fileType === "image") {
        const img = document.createElement("img");
        img.src = previewImage.src;
        postContent.appendChild(img);
    } else if (fileType === "video") {
        const vid = document.createElement("video");
        vid.src = previewVideo.src;
        vid.controls = true;
        postContent.appendChild(vid);
    }

    postContent.appendChild(captionElem);
    postContent.appendChild(resultBox);

    const deleteBtn = document.createElement("button");
    deleteBtn.classList.add("delete-btn");
    deleteBtn.innerText = "Delete";
    deleteBtn.onclick = () => newPost.remove();

    newPost.appendChild(userInfo);
    newPost.appendChild(postContent);
    newPost.appendChild(deleteBtn);

    postContainer.prepend(newPost);

    // Reset form
    document.getElementById("postPreview").style.display = "none";
    document.getElementById("captionInput").value = "";
    previewImage.src = "";
    previewVideo.src = "";
    previewImage.style.display = "none";
    previewVideo.style.display = "none";
}
