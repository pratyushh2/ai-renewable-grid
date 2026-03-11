// Rule-based logic for GridAI Copilot

let chatBox, chatInput, chatSubmit;

document.addEventListener('DOMContentLoaded', () => {
    chatBox = document.getElementById('chat-box');
    chatInput = document.getElementById('chat-input');
    chatSubmit = document.getElementById('chat-submit');

    if(chatSubmit) {
        chatSubmit.addEventListener('click', handleChatSubmit);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleChatSubmit();
        });
    }
});

// Expose internal function to global for inline onclick
window.sendPill = function(text) {
    if(!chatInput) return;
    chatInput.value = text;
    handleChatSubmit();
};

function addMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.style.marginBottom = '1rem';
    
    if(sender === 'user') {
        msgDiv.innerHTML = `<strong>You:</strong> ${text}`;
        msgDiv.style.color = 'var(--text-secondary)';
    } else {
        msgDiv.innerHTML = `<strong>🤖 Copilot:</strong> ${text}`;
        msgDiv.style.color = 'var(--text-primary)';
    }
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleChatSubmit() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    addMessage('user', text);
    chatInput.value = '';
    
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.style.marginBottom = '1rem';
    typingDiv.style.color = 'var(--text-secondary)';
    typingDiv.innerHTML = `<strong>🤖 Copilot:</strong> <i class="fas fa-circle-notch fa-spin"></i> Analyzing grid...`;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        });
        const data = await response.json();
        
        document.getElementById(typingId).remove();
        addMessage('bot', data.response);
    } catch(e) {
        document.getElementById(typingId).remove();
        addMessage('bot', "Connection to Copilot backend failed.");
    }
}
