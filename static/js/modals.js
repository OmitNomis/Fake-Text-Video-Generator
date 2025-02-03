const importBtn = document.getElementById("importBtn");
const importJsonModal = document.getElementById("importJsonModal");
const importJsonCloseBtn = importJsonModal.querySelector(
  ".json-import-modal-close"
);
const confirmImport = document.getElementById("confirmImport");
const jsonInput = document.getElementById("jsonInput");

importBtn.onclick = () => {
  importJsonModal.style.display = "block";
};

importJsonCloseBtn.onclick = () => {
  importJsonModal.style.display = "none";
};

window.onclick = (event) => {
  if (event.target == importJsonModal) {
    importJsonModal.style.display = "none";
  }
};

confirmImport.onclick = () => {
  const jsonData = jsonInput.value;
  if (!jsonData.trim()) {
    alert("Please enter JSON data");
    return;
  }

  try {
    JSON.parse(jsonData);
    importFromJSON(jsonData);
    importJsonModal.style.display = "none";
    jsonInput.value = "";
  } catch (error) {
    alert("Invalid JSON format");
  }
};

jsonInput.addEventListener("paste", (e) => {
  e.preventDefault();
  const paste = e.clipboardData.getData("text");
  try {
    const json = JSON.parse(paste);
    jsonInput.value = JSON.stringify(json, null, 4);
  } catch (error) {
    jsonInput.value = paste;
  }
});

async function loadBackgroundVideos() {
  try {
    const response = await fetch("/api/background-videos");
    const videos = await response.json();

    const container = document.getElementById("videoPreviewsContainer");
    container.innerHTML = videos
      .map(
        (video, index) => `
                <label class="video-option">
                    <input type="radio" name="background" value="${video}" ${
          index === 0 ? "checked" : ""
        }>
                    <video src="/static/videos/${video}" loop muted class="preview-video"></video>
                    <label>${video.replace(/\.[^/.]+$/, "")}</label>
                </label>
            `
      )
      .join("");

    document.querySelectorAll(".preview-video").forEach((video) => {
      video.parentElement.addEventListener("click", () => {
        const input = video.parentElement.querySelector('input[type="radio"]');
        input.checked = true;
      });

      video.addEventListener("mouseover", function () {
        this.play();
      });

      video.addEventListener("mouseout", function () {
        this.pause();
        this.currentTime = 0;
      });
    });
  } catch (error) {
    console.error("Error loading background videos:", error);
  }
}

async function loadBackgroundMusic() {
  try {
    const response = await fetch("/api/background-music");
    const music = await response.json();

    const container = document.getElementById("musicPreviewsContainer");
    container.innerHTML = "";

    const fragment = document.createDocumentFragment();

    const noneOption = document.createElement("label");
    noneOption.className = "music-option";
    noneOption.innerHTML = `
            <input type="radio" name="background-music" value="none" checked>
            <span class="music-name">None</span>
        `;
    fragment.appendChild(noneOption);

    if (music.length > 0) {
      music.forEach((track) => {
        const label = document.createElement("label");
        label.className = "music-option";
        label.innerHTML = `
                    <input type="radio" name="background-music" value="${track}">
                    <span class="music-name">${track.replace(
                      /\.[^/.]+$/,
                      ""
                    )}</span>
                    <audio src="/static/music/${track}" class="preview-audio"></audio>
                    <button class="play-pause-btn" type="button">▶</button>
                `;
        fragment.appendChild(label);
      });
    }

    container.appendChild(fragment);

    document.querySelectorAll(".music-option").forEach((option) => {
      const audio = option.querySelector(".preview-audio");
      const playPauseBtn = option.querySelector(".play-pause-btn");

      if (playPauseBtn) {
        playPauseBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();

          if (audio.paused) {
            audio.play();
            playPauseBtn.textContent = "⏸";
          } else {
            audio.pause();
            playPauseBtn.textContent = "▶";
          }
        });
      }

      option.addEventListener("click", () => {
        const input = option.querySelector('input[type="radio"]');
        if (input) {
          input.checked = true;
        }
      });
    });
  } catch (error) {
    console.error("Error loading background music:", error);
  }
}

document.querySelectorAll(".tab-button").forEach((button) => {
  button.addEventListener("click", () => {
    document
      .querySelectorAll(".tab-button")
      .forEach((btn) => btn.classList.remove("active"));
    document
      .querySelectorAll(".tab-content")
      .forEach((content) => content.classList.remove("active"));

    button.classList.add("active");
    document
      .getElementById(`${button.dataset.tab}-tab`)
      .classList.add("active");
  });
});
