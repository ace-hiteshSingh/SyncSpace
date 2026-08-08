const socket = io();
let currentUserId = null;
let currentFriendId = null;
let typingTimeout = null;
let recorder = null;
let audioChunks = [];
let replyText = "";
let emojiPickerOpen = false;
const EMOJIS = ["😀", "😁", "😂", "🥹", "😍", "😘", "😎", "🤝", "👏", "🙏", "🔥", "🎉", "❤️", "💚", "👍", "👎", "✅", "💬", "🚀", "✨", "🤔"];

function emitConversation(event) {
    if (currentFriendId) socket.emit(event, { friend_id: currentFriendId });
}

function initializeChat(userId, friendId) {
    currentUserId = Number(userId);
    currentFriendId = Number(friendId);
    const form = document.getElementById("chat-form");
    if (!form) return;
    const messageInput = document.getElementById("message-input");
    const cancelReplyButton = document.getElementById("cancel-reply");
    form.addEventListener("submit", sendMessage);
    messageInput.addEventListener("input", handleTyping);
    document.getElementById("attachment-button").addEventListener("click", () => document.getElementById("file-input").click());
    document.getElementById("file-input").addEventListener("change", uploadSelectedFile);
    document.getElementById("voice-button").addEventListener("click", toggleRecording);
    document.getElementById("emoji-button").addEventListener("click", toggleEmojiPicker);
    if (cancelReplyButton) {
        cancelReplyButton.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            clearReply();
        });
    }
    form.addEventListener("click", event => {
        if (event.target.closest("#cancel-reply")) {
            event.preventDefault();
            event.stopPropagation();
            clearReply();
        }
    });
    document.querySelectorAll(".reply-message").forEach(button => button.addEventListener("click", () => setReply(button.closest(".message"))));
    document.querySelectorAll(".copy-message").forEach(button => button.addEventListener("click", () => copyMessage(button.closest(".message"))));
    messageInput.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            event.preventDefault();
            clearReply();
            return;
        }
        handleComposerKeydown(event);
    });
    renderEmojiPicker();
    openConversation();
    scrollToBottom();
}

function openConversation() {
    if (!currentUserId || !currentFriendId || !socket.connected) return;
    emitConversation("join");
    emitConversation("conversation_opened");
}
socket.on("connect", openConversation);

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById("message-input");
    let message = input.value.trim();
    if (replyText) message = `↪ ${replyText}\n${message}`.trim();
    if (!message) return;
    socket.emit("send_message", { receiver_id: currentFriendId, message });
    input.value = "";
    input.style.height = "";
    clearReply();
    emitConversation("stop_typing");
}

function handleTyping() {
    emitConversation("typing");
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => emitConversation("stop_typing"), 1200);
}

function handleComposerKeydown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        document.getElementById("chat-form").requestSubmit();
    }
}

function renderEmojiPicker() {
    const picker = document.getElementById("emoji-picker");
    if (!picker) return;
    picker.innerHTML = "";
    EMOJIS.forEach(emoji => {
        const button = document.createElement("button");
        button.type = "button"; button.textContent = emoji;
        button.addEventListener("click", () => {
            const input = document.getElementById("message-input");
            input.value += emoji; input.focus();
            picker.style.display = "none";
        });
        picker.appendChild(button);
    });
    picker.style.display = "none";
}

function toggleEmojiPicker(event) {
    event?.preventDefault();
    event?.stopPropagation();
    const picker = document.getElementById("emoji-picker");
    if (!picker) return;
    picker.style.display = picker.style.display === "grid" ? "none" : "grid";
}

function setReply(message) {
    replyText = message.querySelector(".message-content")?.innerText.trim().slice(0, 130) || "Attachment";
    const preview = document.getElementById("reply-preview");
    const replyTextNode = document.getElementById("reply-text");
    if (replyTextNode) replyTextNode.textContent = replyText;
    if (preview) preview.hidden = false;
    document.getElementById("message-input").focus();
}
function clearReply() { replyText = ""; const preview = document.getElementById("reply-preview"); if (preview) preview.hidden = true; }
async function copyMessage(message) {
    const text = message.querySelector(".message-content")?.innerText.trim();
    if (!text) return;
    try { await navigator.clipboard.writeText(text); } catch { showError("Unable to copy this message."); }
}

async function uploadSelectedFile(event) {
    const file = event.target.files[0];
    if (file) await uploadFile(file);
    event.target.value = "";
}

async function uploadFile(file) {
    const data = new FormData();
    data.append("file", file, file.name);
    try {
        const response = await fetch(document.querySelector(".chat-container").dataset.uploadUrl, { method: "POST", body: data });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error || "Upload failed.");
    } catch (error) { showError(error.message); }
}

async function toggleRecording() {
    const button = document.getElementById("voice-button");
    if (recorder?.state === "recording") { recorder.stop(); return; }
    if (!navigator.mediaDevices || !window.MediaRecorder) return showError("Voice notes are not supported in this browser.");
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];
        recorder = new MediaRecorder(stream);
        recorder.ondataavailable = event => { if (event.data.size) audioChunks.push(event.data); };
        recorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            button.classList.remove("is-recording");
            await uploadFile(new File([new Blob(audioChunks, { type: recorder.mimeType || "audio/webm" })], "voice-note.webm", { type: recorder.mimeType || "audio/webm" }));
        };
        recorder.start();
        button.classList.add("is-recording");
    } catch { showError("Microphone access is needed to record a voice note."); }
}

socket.on("connect", () => {
    if (currentFriendId) {
        emitConversation("join");
        emitConversation("conversation_opened");
    }
});

socket.on("receive_message", data => {
    const isCurrentConversation = currentUserId && currentFriendId &&
        ((Number(data.sender_id) === currentUserId && Number(data.receiver_id) === currentFriendId) ||
         (Number(data.sender_id) === currentFriendId && Number(data.receiver_id) === currentUserId));
    if (isCurrentConversation && !document.getElementById(`message-${data.id}`)) {
        appendMessage(data);
        // A message that arrives while this conversation is visible has been
        // seen immediately. Persist that state and notify the sender.
        if (Number(data.sender_id) !== currentUserId) emitConversation("conversation_opened");
    } else if (!currentFriendId) updateChatList(data);
});
socket.on("messages_read", data => data.message_ids.forEach(id => { const status = document.getElementById(`read-status-${id}`); if (status) status.textContent = "✓✓"; }));
socket.on("user_online", data => updateStatus(data, "Online", "status-online"));
socket.on("user_offline", data => updateStatus(data, `Last seen ${data.last_seen}`, "status-offline"));
socket.on("show_typing", data => { if (Number(data.user_id) === currentFriendId) { const node = document.getElementById("typing-indicator"); node.textContent = `${data.username} is typing…`; node.style.display = "block"; } });
socket.on("hide_typing", data => { if (Number(data.user_id) === currentFriendId) document.getElementById("typing-indicator").style.display = "none"; });
socket.on("chat_error", data => showError(data.message));

function appendMessage(data) {
    document.getElementById("empty-chat")?.remove();
    const mine = Number(data.sender_id) === currentUserId;
    const message = document.createElement("div");
    message.id = `message-${data.id}`;
    message.className = `message ${mine ? "sent" : "received"}`;
    const content = document.createElement("div"); content.className = "message-content";
    if (data.message) { const text = document.createElement("span"); text.textContent = data.message; content.appendChild(text); }
    if (data.attachment) content.appendChild(createAttachment(data.attachment));
    const footer = document.createElement("div"); footer.className = "message-footer";
    footer.innerHTML = `<span class="message-time">${data.time}</span>${mine ? `<span id="read-status-${data.id}" class="read-status">${data.is_read ? "✓✓" : "✓"}</span>` : ""}`;
    message.append(content, footer);
    addMessageActionHandlers(message);
    document.getElementById("chat-messages").appendChild(message);
    scrollToBottom();
}

function addMessageActionHandlers(message) {
    const actions = document.createElement("div"); actions.className = "message-actions";
    [["reply", "Reply", () => setReply(message)], ["copy", "Copy", () => copyMessage(message)]].forEach(([icon, label, handler]) => {
        const button = document.createElement("button"); button.type = "button"; button.setAttribute("aria-label", label); button.innerHTML = `<i data-lucide="${icon}"></i>`; button.addEventListener("click", handler); actions.appendChild(button);
    });
    message.appendChild(actions);
    if (window.lucide) lucide.createIcons({ nodes: [actions] });
}

function updateChatList(data) {
    const list = document.getElementById("chat-list");
    const container = document.querySelector(".chat-list-container");
    if (!list || !container) return;
    const currentId = Number(container.dataset.currentUserId);
    const friendId = Number(data.sender_id) === currentId ? Number(data.receiver_id) : Number(data.sender_id);
    const friendName = Number(data.sender_id) === currentId ? data.receiver_name : data.sender_name;
    let card = list.querySelector(`[data-chat-user-id="${friendId}"]`);
    if (!card) {
        card = document.createElement("a"); card.className = "chat-card"; card.dataset.chatUserId = friendId; card.dataset.chatName = (friendName || "").toLowerCase(); card.href = `/chat/${friendId}`;
        card.innerHTML = `<div class="user-avatar"></div><div class="chat-info"><div class="chat-top"><h3></h3><span class="chat-time"></span></div><p class="chat-preview"></p></div>`;
        card.querySelector(".user-avatar").textContent = (friendName || "?")[0].toUpperCase(); card.querySelector("h3").textContent = friendName || "Conversation";
    }
    card.querySelector(".chat-preview").textContent = Number(data.sender_id) === currentId ? `You: ${data.message || "Attachment"}` : (data.message || "Attachment");
    card.querySelector(".chat-time").textContent = data.time;
    if (Number(data.sender_id) !== currentId) {
        let badge = card.querySelector(".unread-badge"); if (!badge) { badge = document.createElement("div"); badge.className = "unread-badge"; card.appendChild(badge); }
        badge.textContent = String(Number(badge.textContent || 0) + 1);
    }
    list.prepend(card); document.getElementById("empty-chat-list")?.setAttribute("hidden", "");
}

document.getElementById("chat-list-search")?.addEventListener("input", event => {
    const query = event.target.value.trim().toLowerCase();
    document.querySelectorAll(".chat-card").forEach(card => { card.hidden = !card.dataset.chatName.includes(query); });
});

function createAttachment(file) {
    if (file.type === "voice") { const audio = document.createElement("audio"); audio.controls = true; audio.src = file.url; return audio; }
    const link = document.createElement("a"); link.href = file.url; link.target = "_blank"; link.rel = "noopener";
    if (file.type === "image") { const image = document.createElement("img"); image.className = "chat-image"; image.src = file.url; image.alt = file.name; link.appendChild(image); }
    else { link.className = "attachment-link"; link.textContent = `↗ ${file.name}`; }
    return link;
}

function updateStatus(data, text, className) {
    if (!currentFriendId || Number(data.user_id) !== currentFriendId) return;
    const status = document.getElementById("friend-status");
    if (!status) return;
    status.textContent = text;
    status.className = className;
}
function showError(message) { window.alert(message); }
function scrollToBottom() { const box = document.getElementById("chat-messages"); if (box) requestAnimationFrame(() => { box.scrollTop = box.scrollHeight; }); }
