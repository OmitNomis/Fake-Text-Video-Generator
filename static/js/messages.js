let currentOptionsMenu = null;

function createOptionsMenu() {
  const menu = document.createElement("div");
  menu.className = "message-options";
  menu.innerHTML = `
        <button class="edit">Edit</button>
        <button class="switch">Switch Side</button>
        <button class="add-textbox-above">Add Textbox Above</button>
        <button class="add-textbox-below">Add Textbox Below</button>
        <button class="sound-effect">Sound Effects</button>
        <button class="delete">Delete</button>
    `;
  return menu;
}

function hideOptionsMenu() {
  if (currentOptionsMenu) {
    currentOptionsMenu.style.display = "none";
  }
}

function handleMessageClick(e) {
  const messageDiv = e.target.closest(".message");
  if (!messageDiv) return;

  hideOptionsMenu();

  const optionsMenu = createOptionsMenu();
  document.body.appendChild(optionsMenu);
  currentOptionsMenu = optionsMenu;

  const rect = messageDiv.getBoundingClientRect();

  optionsMenu.style.position = "fixed";
  optionsMenu.style.display = "block";
  optionsMenu.style.top = `${rect.bottom}px`;

  if (messageDiv.classList.contains("sender")) {
    optionsMenu.style.right = `${window.innerWidth - rect.right}px`;
    optionsMenu.style.left = "auto";
  } else {
    optionsMenu.style.left = `${rect.left}px`;
    optionsMenu.style.right = "auto";
  }

  optionsMenu.querySelector(".edit").onclick = (e) => {
    e.stopPropagation();
    messageDiv.contentEditable = true;
    messageDiv.focus();
    hideOptionsMenu();

    messageDiv.addEventListener("input", () => {
      updateMessagesArray();
    });

    messageDiv.onblur = () => {
      messageDiv.contentEditable = false;
      updateMessagesArray();
    };
  };

  optionsMenu.querySelector(".switch").onclick = (e) => {
    e.stopPropagation();
    const isSenderMessage = messageDiv.classList.contains("sender");
    messageDiv.classList.toggle("sender");
    messageDiv.classList.toggle("receiver");

    const isFirstMessage =
      messageDiv.parentNode.querySelector(".message") === messageDiv;
    if (isSenderMessage) {
      messageDiv.setAttribute(
        "data-sound-effect",
        isFirstMessage ? "notification" : "receive"
      );
    } else {
      messageDiv.setAttribute("data-sound-effect", "send");
    }

    const index = Array.from(messageDiv.parentNode.children).indexOf(
      messageDiv
    );
    if (index !== -1 && messages[index]) {
      messages[index].is_sender = !isSenderMessage;
    }
    hideOptionsMenu();
  };

  optionsMenu.querySelector(".add-textbox-above").onclick = (e) => {
    e.stopPropagation();
    const newMessage = document.createElement("div");
    const messageId = Date.now();
    newMessage.className = `message ${
      messageDiv.classList.contains("sender") ? "sender" : "receiver"
    }`;
    newMessage.setAttribute("data-id", messageId);
    messageDiv.parentNode.insertBefore(newMessage, messageDiv);

    newMessage.contentEditable = true;
    newMessage.focus();

    newMessage.addEventListener("input", () => {
      updateMessagesArray();
    });

    newMessage.onblur = () => {
      newMessage.contentEditable = false;
      if (!newMessage.textContent.trim()) {
        newMessage.remove();
      }
      updateMessagesArray();
    };

    hideOptionsMenu();
  };

  optionsMenu.querySelector(".add-textbox-below").onclick = (e) => {
    e.stopPropagation();
    const newMessage = document.createElement("div");
    const messageId = Date.now();
    newMessage.className = `message ${
      messageDiv.classList.contains("sender") ? "sender" : "receiver"
    }`;
    newMessage.setAttribute("data-id", messageId);

    if (messageDiv.nextSibling) {
      messageDiv.parentNode.insertBefore(newMessage, messageDiv.nextSibling);
    } else {
      messageDiv.parentNode.appendChild(newMessage);
    }

    newMessage.contentEditable = true;
    newMessage.focus();

    newMessage.addEventListener("input", () => {
      updateMessagesArray();
    });

    newMessage.onblur = () => {
      newMessage.contentEditable = false;
      if (!newMessage.textContent.trim()) {
        newMessage.remove();
      }
      updateMessagesArray();
    };

    hideOptionsMenu();
  };

  optionsMenu.querySelector(".sound-effect").onclick = (e) => {
    e.stopPropagation();

    const existingSubmenu = document.querySelector(".sound-effect-submenu");
    if (existingSubmenu) existingSubmenu.remove();

    const submenu = createSoundEffectSubmenu(messageDiv);
    document.body.appendChild(submenu);

    const buttonRect = e.target.getBoundingClientRect();

    submenu.style.position = "fixed";
    submenu.style.left = `${buttonRect.right}px`;
    submenu.style.top = `${buttonRect.top}px`;

    submenu.querySelectorAll(".effect-option").forEach((option) => {
      option.onclick = (event) => {
        event.stopPropagation();
        const selectedEffect = event.target.dataset.effect;

        messageDiv.setAttribute(
          "data-sound-effect",
          selectedEffect === "none" ? "" : selectedEffect
        );

        updateMessagesArray();

        submenu.querySelectorAll(".effect-option").forEach((opt) => {
          opt.textContent = `${
            opt.dataset.effect.charAt(0).toUpperCase() +
            opt.dataset.effect.slice(1)
          } ${opt.dataset.effect === selectedEffect ? "✓" : ""}`;
        });
      };
    });

    document.addEventListener("click", function closeSubmenu(event) {
      if (!submenu.contains(event.target) && !e.target.contains(event.target)) {
        submenu.remove();
        hideOptionsMenu();
        document.removeEventListener("click", closeSubmenu);
      }
    });
  };

  optionsMenu.querySelector(".delete").onclick = (e) => {
    e.stopPropagation();
    const index = Array.from(messageDiv.parentNode.children).indexOf(
      messageDiv
    );
    if (index !== -1) {
      messages.splice(index, 1);
      messageDiv.remove();
    }
    hideOptionsMenu();
  };
}

document.addEventListener("click", (e) => {
  if (!e.target.closest(".message") && !e.target.closest(".message-options")) {
    hideOptionsMenu();
  }
});

messageContainer.addEventListener("click", handleMessageClick);

function createSoundEffectSubmenu(messageDiv) {
  const submenu = document.createElement("div");
  submenu.className = "sound-effect-submenu";

  const currentEffect = messageDiv.getAttribute("data-sound-effect") || "none";

  submenu.innerHTML = `
        <button class="effect-option" data-effect="none">None ${
          currentEffect === "none" ? "✓" : ""
        }</button>
        <button class="effect-option" data-effect="vineboom">Vineboom ${
          currentEffect === "vineboom" ? "✓" : ""
        }</button>
        <button class="effect-option" data-effect="notification">Notification ${
          currentEffect === "notification" ? "✓" : ""
        }</button>
        <button class="effect-option" data-effect="rizz">Rizz ${
          currentEffect === "rizz" ? "✓" : ""
        }</button>
        <button class="effect-option" data-effect="send">Send ${
          currentEffect === "send" ? "✓" : ""
        }</button>
        <button class="effect-option" data-effect="receive">Receive ${
          currentEffect === "receive" ? "✓" : ""
        }</button>
        <button class="effect-option" data-effect="pop">Pop ${
          currentEffect === "bleh" ? "✓" : ""
        }</button>
    `;
  return submenu;
}

document.querySelectorAll(".preview-video").forEach((video) => {
  video.addEventListener("mouseover", function () {
    this.play();
  });

  video.addEventListener("mouseout", function () {
    this.pause();
    this.currentTime = 0;
  });
});
