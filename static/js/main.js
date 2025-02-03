let messages = [];
let isSender = true;
let isGenerating = false;

const messageInput = document.getElementById("messageInput");
const messageContainer = document.getElementById("messageContainer");
const chatContainer = document.getElementById("chatContainer");
const senderToggle = document.getElementById("senderToggle");
const addMessageBtn = document.getElementById("addMessage");
const generateBtn = document.getElementById("generateBtn");

function scrollToBottom() {
  messageContainer.scrollTop = messageContainer.scrollHeight;
}

function updateMessagesArray() {
  const dynamicContainer = document.querySelector(".dynamic-container");
  messages = Array.from(dynamicContainer.children)
    .map((messageDiv) => ({
      id: messageDiv.getAttribute("data-id") || Date.now(),
      text: messageDiv.textContent.trim(),
      is_sender: messageDiv.classList.contains("sender"),
      soundEffect: messageDiv.getAttribute("data-sound-effect") || null,
    }))
    .filter((msg) => msg.text);

  console.log("Updated messages array:", messages);
}

function importFromJSON(json) {
  if (!json) return;

  try {
    const data = JSON.parse(json);
    if (!Array.isArray(data)) {
      throw new Error("Invalid JSON data");
    }

    const dynamicContainer = document.querySelector(".dynamic-container");
    dynamicContainer.innerHTML = "";

    data.forEach((msg) => {
      const messageDiv = document.createElement("div");
      messageDiv.className = `message ${msg.is_sender ? "sender" : "receiver"}`;
      const cleanedText = msg.text.replace(/\*/g, "");
      messageDiv.textContent = cleanedText;
      messageDiv.setAttribute("data-id", msg.id);
      messageDiv.setAttribute("data-sound-effect", msg.soundEffect || "");
      dynamicContainer.appendChild(messageDiv);
    });

    updateMessagesArray();
    scrollToBottom();
  } catch (error) {
    console.error("Error importing JSON:", error);
    alert("Failed to import JSON data. Please check the format.");
  }
}

function addMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isSender ? "sender" : "receiver"}`;
  messageDiv.textContent = text;
  messageDiv.setAttribute("data-id", Date.now());

  const isFirstMessage =
    messageContainer.querySelector(".dynamic-container").children.length === 0;
  if (isSender) {
    messageDiv.setAttribute("data-sound-effect", "send");
  } else {
    messageDiv.setAttribute(
      "data-sound-effect",
      isFirstMessage ? "notification" : "receive"
    );
  }

  const dynamicContainer = document.querySelector(".dynamic-container");
  dynamicContainer.appendChild(messageDiv);

  updateMessagesArray();

  messageInput.value = "";
  messageInput.focus();
  scrollToBottom();
}

messageInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") addMessage();
});

senderToggle.addEventListener("click", () => {
  isSender = !isSender;
  senderToggle.classList.toggle("receiver");
});

addMessageBtn.addEventListener("click", addMessage);
generateBtn.addEventListener("click", async () => {
  if (isGenerating) return;
  isGenerating = true;
  generateBtn.textContent = "Generating...";

  const loadingOverlay = document.getElementById("loadingOverlay");
  loadingOverlay.style.display = "flex";
  updateProgress(0);

  try {
    updateMessagesArray();
    addLog("Starting video generation...", "info");
    updateProgress(5);

    addLog("Processing messages and preparing audio generation...", "info");
    updateProgress(10);

    const requestData = {
      messages: messages,
      profileImage: localStorage.getItem("profileImage") || "",
      headerName: localStorage.getItem("headerName") || "John Doe",
      voiceSettings: {
        apiKey: document.getElementById("elevenLabsKey").value,
        sender: document.getElementById("senderVoice").value,
        receiver: document.getElementById("receiverVoice").value,
      },
      backgroundVideo: document.querySelector(
        'input[name="background"]:checked'
      ).value,
      backgroundMusic: document.querySelector(
        'input[name="background-music"]:checked'
      ).value,
    };
    console.log(requestData);
    let messageCount = messages.length;
    let progressPerMessage = 70 / messageCount;

    messages.forEach((msg, index) => {
      addLog(
        `Generating audio for message ${
          index + 1
        }/${messageCount}: "${msg.text.substring(0, 30)}${
          msg.text.length > 30 ? "..." : ""
        }"`,
        "info"
      );
      updateProgress(10 + progressPerMessage * (index + 1));
    });

    addLog("Starting video rendering...", "info");
    updateProgress(80);

    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Video generation failed");
    }

    const data = await response.json();
    updateProgress(100);
    addLog("Video generated successfully!", "success");
  } catch (error) {
    console.error("Error:", error);
    addLog(`Error: ${error.message}`, "error");
    alert("Failed to generate video: " + error.message);
  } finally {
    setTimeout(() => {
      loadingOverlay.style.display = "none";
      generateBtn.textContent = "Generate Video";
      isGenerating = false;
    }, 2000);
  }
});

window.addEventListener("load", scrollToBottom);

function updateProgress(percent) {
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  progressBar.style.width = `${percent}%`;
  progressText.textContent = `${Math.round(percent)}%`;
}

function addLog(message, type = "info") {
  const logContent = document.querySelector(".log-content");
  const entry = document.createElement("div");
  entry.className = `log-entry ${type}`;
  entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
  logContent.appendChild(entry);
  entry.scrollIntoView({ behavior: "smooth" });
}
