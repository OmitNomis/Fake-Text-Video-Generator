let voiceMap = {};

async function fetchVoiceIds() {
  const apiKey = document.getElementById("elevenLabsKey").value.trim();
  if (!apiKey) {
    alert("Please enter your ElevenLabs API key");
    return;
  }

  try {
    const response = await fetch("/api/fetch-voices", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ apiKey: apiKey }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch voices");
    }

    const voices = await response.json();

    const senderVoice = document.getElementById("senderVoice");
    const receiverVoice = document.getElementById("receiverVoice");
    senderVoice.innerHTML = '<option value="">Select a voice</option>';
    receiverVoice.innerHTML = '<option value="">Select a voice</option>';

    const savedSenderVoice = localStorage.getItem("senderVoice");
    const savedReceiverVoice = localStorage.getItem("receiverVoice");

    voices.forEach((voice) => {
      const senderOption = document.createElement("option");
      senderOption.value = voice.voice_id;
      senderOption.textContent = voice.name;
      senderOption.selected = voice.voice_id === savedSenderVoice;
      senderVoice.appendChild(senderOption);

      const receiverOption = document.createElement("option");
      receiverOption.value = voice.voice_id;
      receiverOption.textContent = voice.name;
      receiverOption.selected = voice.voice_id === savedReceiverVoice;
      receiverVoice.appendChild(receiverOption);
    });

    localStorage.setItem("elevenLabsKey", apiKey);
    saveSettings();

    alert("Voice IDs successfully fetched!");
  } catch (error) {
    console.error("Error fetching voices:", error);
    alert("Failed to fetch voices. Please check your API key.");
  }
}

document.getElementById("senderVoice").addEventListener("change", saveSettings);
document
  .getElementById("receiverVoice")
  .addEventListener("change", saveSettings);
