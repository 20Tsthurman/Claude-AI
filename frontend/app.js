const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const loadingIcon = document.getElementById('loading-icon');

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const message = messageInput.value.trim();
    if (message !== '') {
        appendMessage('user', message);
        messageInput.value = '';
        showLoadingIcon();

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        })
        .then(response => response.json())
        .then(data => {
            hideLoadingIcon();
            appendMessage('assistant', data.response);
        })
        .catch(error => {
            hideLoadingIcon();
            console.error('Error:', error);
            appendMessage('error', 'Oops! Something went wrong.');
        });
    }
}

function appendMessage(role, content) {
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${role}`;
    messageElement.innerHTML = `
        <p class="message-role">${role === 'user' ? 'You' : 'Assistant'}</p>
        <p class="message-content">${content}</p>
    `;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoadingIcon() {
    loadingIcon.style.display = 'inline-block';
}

function hideLoadingIcon() {
    loadingIcon.style.display = 'none';
}