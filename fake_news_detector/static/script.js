
function previewNewsMedia(event, type) {
    let file = event.target.files[0];
    if (!file) return;

    let reader = new FileReader();
    reader.onload = function (e) {
        if (type === "image") {
            let imagePreview = document.getElementById("imagePreview");
            imagePreview.src = e.target.result;
            imagePreview.style.display = "block";
            document.getElementById("videoPreview").style.display = "none"; 
        } else if (type === "video") {
            let videoPreview = document.getElementById("videoPreview");
            videoPreview.src = e.target.result;
            videoPreview.style.display = "block";
            document.getElementById("imagePreview").style.display = "none"; 
        }
    };
    reader.readAsDataURL(file);
}

//  News Post 
function uploadNewsPost() {
    let newsPostSection = document.getElementById("newsPostSection");
    let newsText = document.getElementById("newsTextInput").value.trim();
    let imagePreview = document.getElementById("imagePreview");
    let videoPreview = document.getElementById("videoPreview");

    let imageSrc = imagePreview.src || "";
    let videoSrc = videoPreview.src || "";

    // Remove default 'src' (e.g., about:blank or empty string)
    let validImage = imagePreview.style.display === "block" && imageSrc.startsWith("data:image");
    let validVideo = videoPreview.style.display === "block" && videoSrc.startsWith("data:video");

    if (!newsText && !validImage && !validVideo) {
        alert("Please add text, image, or video before posting.");
        return;
    }

    let newPost = document.createElement("div");
    newPost.classList.add("news-post");
    newPost.style.border = "4px solid black";
    newPost.style.backgroundColor = "#bec3f4";
    newPost.style.display = "block";

    if (validImage) {
        let imgElement = document.createElement("img");
        imgElement.src = imageSrc;
        imgElement.style.maxWidth = "100%";
        imgElement.style.margin = "10px 0";
        newPost.appendChild(imgElement);
    }

    if (validVideo) {
        let videoElement = document.createElement("video");
        videoElement.src = videoSrc;
        videoElement.controls = true;
        videoElement.style.maxWidth = "100%";
        videoElement.style.margin = "10px 0";
        newPost.appendChild(videoElement);
    }

    if (newsText) {
        let textElement = document.createElement("p");
        textElement.innerText = newsText;
        newPost.appendChild(textElement);
    }

    let deleteButton = document.createElement("button");
    deleteButton.innerText = "Delete";
    deleteButton.onclick = function () {
        newPost.remove();
    };
    newPost.appendChild(deleteButton);

    newsPostSection.prepend(newPost);

    // Reset Inputs
    document.getElementById("newsTextInput").value = "";
    imagePreview.src = "";
    imagePreview.style.display = "none";
    videoPreview.src = "";
    videoPreview.style.display = "none";
    document.getElementById("newsImageInput").value = "";
    document.getElementById("newsVideoInput").value = "";
}
