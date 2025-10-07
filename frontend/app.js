const API_BASE_URL = 'http://localhost:8000/api/v1';

let sessionId = null;
let activeMode = 'chat';

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const capabilitiesList = document.getElementById('capabilitiesList');
const activeModeDisplay = document.getElementById('activeMode');

function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function addMessage(role, content, intent = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    if (intent && role === 'assistant') {
        const intentSpan = document.createElement('div');
        intentSpan.className = 'message-intent';
        intentSpan.textContent = `Intent: ${intent.type} (${(intent.confidence * 100).toFixed(1)}%)`;
        messageContent.appendChild(intentSpan);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    if (!sessionId) {
        sessionId = generateSessionId();
    }
    
    addMessage('user', message);
    messageInput.value = '';
    sendButton.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                context: {
                    active_mode: activeMode
                }
            }),
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        addMessage('assistant', data.response, data.intent);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('assistant', 'Sorry, I encountered an error processing your request.');
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

capabilitiesList.addEventListener('click', (e) => {
    if (e.target.tagName === 'LI') {
        const mode = e.target.dataset.mode;
        setActiveMode(mode, e.target.textContent);
        
        document.querySelectorAll('#capabilitiesList li').forEach(li => {
            li.classList.remove('active');
        });
        e.target.classList.add('active');
    }
});

function setActiveMode(mode, modeName) {
    activeMode = mode;
    const modeValue = activeModeDisplay.querySelector('.mode-value');
    modeValue.textContent = modeName;
    
    const modeMessages = {
        'file_operation': "File Operations mode activated. I'll focus on creating, reading, deleting, and managing files.",
        'schedule_reminder': "Reminder mode activated. I'll help you schedule and manage reminders.",
        'run_script': "Script Runner mode activated. I'll execute scripts and programs for you.",
        'search': "Search mode activated. I'll help you find files and information.",
        'system_info': "System Info mode activated. I'll provide system information and status.",
        'chat': "General Chat mode activated. I can help with anything!"
    };
    
    if (modeMessages[mode]) {
        addMessage('assistant', modeMessages[mode]);
    }
}

document.querySelector('[data-mode="chat"]').classList.add('active');

addMessage('assistant', "Hello! I'm your AI assistant. Click a capability above to activate focused mode, or chat with me normally. How can I assist you today?");

messageInput.focus();

