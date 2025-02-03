const profileImageContainer = document.getElementById("profileImageContainer");
const profileUpload = document.getElementById("profileUpload");
const profileImage = document.getElementById("profileImage");
const profileImageModal = document.getElementById("profileImageModal");
const profileImageCloseBtn = profileImageModal.querySelector(
  ".picture-modal-close"
);
const uploadBtn = document.getElementById("uploadBtn");
const existingImages = document.getElementById("existingImages");
const uploadPreview = document.getElementById("uploadPreview");

window.addEventListener("load", () => {
  const savedHeaderName = localStorage.getItem("headerName") || "John Doe";
  const savedProfileImage =
    localStorage.getItem("profileImage") ||
    "/static/images/profile_pictures/profile.jpg";

  document.getElementById("headerName").textContent = savedHeaderName;
  document.getElementById("profileImage").src = savedProfileImage;

  loadExistingImages();
  loadBackgroundVideos();
  loadBackgroundMusic();

  const apiKey = localStorage.getItem("elevenLabsKey");
  if (apiKey) {
    document.getElementById("elevenLabsKey").value = apiKey;
    fetchVoiceIds();
  }
});

function saveSettings() {
  const currentName =
    document.getElementById("headerName").textContent.trim() || "John Doe";
  const currentImage = document.getElementById("profileImage").src;
  const senderVoice = document.getElementById("senderVoice").value;
  const receiverVoice = document.getElementById("receiverVoice").value;

  localStorage.setItem("headerName", currentName);
  localStorage.setItem("profileImage", currentImage);
  localStorage.setItem("senderVoice", senderVoice);
  localStorage.setItem("receiverVoice", receiverVoice);
}

profileUpload.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      uploadPreview.src = e.target.result;
      uploadPreview.style.display = "block";
      uploadBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  } else {
    uploadPreview.style.display = "none";
    uploadBtn.disabled = true;
  }
});

profileImageContainer.addEventListener("click", () => {
  profileImageModal.style.display = "block";
  loadExistingImages();
  uploadPreview.style.display = "none";
  uploadBtn.disabled = true;
  profileUpload.value = "";
});

profileImageCloseBtn.addEventListener("click", () => {
  profileImageModal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === profileImageModal) {
    profileImageModal.style.display = "none";
  }
});

async function loadExistingImages() {
  try {
    const response = await fetch("/api/profile-pictures");
    const images = await response.json();

    existingImages.innerHTML = images
      .map(
        (image) => `
                <div class="image-item">
                    <img src="/static/images/profile_pictures/${image}" onclick="selectProfileImage('/static/images/profile_pictures/${image}')" class="${
          profileImage.src.includes(image) ? "selected" : ""
        }">
                </div>
            `
      )
      .join("");
  } catch (error) {
    console.error("Error loading existing images:", error);
  }
}

function selectProfileImage(src) {
  profileImage.src = src;
  localStorage.setItem("profileImage", src);
  saveSettings();

  document.querySelectorAll(".image-grid img").forEach((img) => {
    img.classList.toggle("selected", img.src === src);
  });

  profileImageModal.style.display = "none";
}

uploadBtn.addEventListener("click", async () => {
  const file = profileUpload.files[0];
  if (!file) {
    alert("Please select a file first");
    return;
  }

  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await fetch("/api/upload-profile-picture", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Upload failed");

    const data = await response.json();
    profileImage.src = data.image_path;
    localStorage.setItem("profileImage", data.image_path);
    saveSettings();

    uploadPreview.style.display = "none";
    uploadBtn.disabled = true;
    profileUpload.value = "";

    await loadExistingImages();
  } catch (error) {
    console.error("Error uploading image:", error);
    alert("Failed to upload image");
  }
});

headerName.addEventListener("blur", () => {
  if (!headerName.textContent.trim()) {
    headerName.textContent = "John Doe";
  }
  saveSettings();
});

headerName.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    headerName.blur();
  }
});
