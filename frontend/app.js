document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIcon = document.getElementById('loading-icon');

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            appendMessage('user', message);
            messageInput.value = '';
            showLoading();
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                appendMessage('assistant', data.response);
                hideLoading();
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage('error', 'Oops! Something went wrong.');
                hideLoading();
            });
        }
    }

    function appendMessage(role, content) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        messageElement.textContent = `${role === 'user' ? 'You: ' : 'Assistant: '}${content}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showLoading() {
        loadingIcon.style.display = 'inline-block';
    }

    function hideLoading() {
        loadingIcon.style.display = 'none';
    }
});
