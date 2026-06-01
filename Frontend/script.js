let threadId = null;
let isWidgetOpen = false;
let chatbotButton, chatbotWidget, chatMessages, chatForm, userInput, charCounter;
 
const API_BASE_URL = "https://water-warehouse-chatbot.onrender.com";
const MAX_MESSAGE_LENGTH = 500;   // must match server-side constant
const CLIENT_RATE_LIMIT = 15;     // max messages per minute (mirrors server)
const CLIENT_RATE_WINDOW_MS = 60 * 1000;
let messageTimestamps = [];       // rolling log of send times
 
// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements after DOM is loaded
    chatbotButton = document.getElementById('chatbot-toggle');
    chatbotWidget = document.getElementById('chatbot-widget');
    chatMessages = document.getElementById('chatbot-messages');
    chatForm = document.getElementById('chat-form');
    userInput = document.getElementById('userInput');
    charCounter = document.getElementById('char-counter');
    
    // Check if elements exist
    if (!chatbotButton || !chatbotWidget || !chatMessages || !chatForm || !userInput) {
        console.error('Required elements not found. Check your HTML element IDs.');
        return;
    }
    
    // Initialize event listeners
    initializeEventListeners();
});
 
async function startConversation() {
    try {
        const res = await fetch(`${API_BASE_URL}/start`);
        const data = await res.json();
        threadId = data.thread_id;
        console.log("Thread ID:", threadId);
    } catch (error) {
        console.error("Failed to start conversation: ", error);
    }
}
 
function toggleWidget() {
    isWidgetOpen = !isWidgetOpen;
    chatbotWidget.classList.toggle('active', isWidgetOpen);
    chatbotButton.classList.toggle('active', isWidgetOpen);
    
    if (isWidgetOpen) {
        userInput.focus();
        if (!threadId) {
            startConversation();
        }
    }
}
 
function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = message;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
 
function initializeEventListeners() {
    // Live character counter
    userInput.addEventListener('input', () => {
        const len = userInput.value.length;
        if (charCounter) {
            charCounter.textContent = `${len}/${MAX_MESSAGE_LENGTH}`;
            charCounter.classList.toggle('over-limit', len > MAX_MESSAGE_LENGTH);
        }
    });
 
    // Form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const userMessage = userInput.value.trim();
        if (!userMessage) return;
 
        // Client-side length guard
        if (userMessage.length > MAX_MESSAGE_LENGTH) {
            appendMessage("bot", `Please shorten your message to ${MAX_MESSAGE_LENGTH} characters or less.`);
            return;
        }
 
        // Client-side rate guard (mirrors server)
        const now = Date.now();
        messageTimestamps = messageTimestamps.filter(t => now - t < CLIENT_RATE_WINDOW_MS);
        if (messageTimestamps.length >= CLIENT_RATE_LIMIT) {
            appendMessage("bot", "You're sending messages too quickly. Please wait a moment and try again.");
            return;
        }
        messageTimestamps.push(now);
 
        appendMessage("user", userMessage);
        userInput.value = "";
        if (charCounter) charCounter.textContent = `0/${MAX_MESSAGE_LENGTH}`;
 
        userInput.value = "";
        
        // Show typing indicator
        const typingDiv = document.createElement("div");
        typingDiv.className = "message bot";
        typingDiv.textContent = "Typing...";
        typingDiv.id = "typing-indicator";
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Ensure we have a thread ID
        if (!threadId) {
            await startConversation();
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: userMessage,
                    thread_id: threadId,
                }),
            });
 
            const data = await response.json();
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
 
            if (!response.ok) {
                // Surface server-side rate limit / length errors to the user
                appendMessage("bot", data.error || "Something went wrong. Please try again.");
            } else {
                appendMessage("bot", data.response || "No response from assistant.");
            }
 
            
        } catch (error) {
            console.error(error);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", "Sorry, I'm having trouble connecting. Please try again.");
        }
    });
 
    // Toggle button
    chatbotButton.addEventListener('click', toggleWidget);
 
    // Click outside to close
    document.addEventListener('click', (e) => {
        if (isWidgetOpen && !chatbotWidget.contains(e.target) && !chatbotButton.contains(e.target)) {
            toggleWidget();
        }
    });
 
    // Enter key support
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}



/*
let threadId = null;
let isWidgetOpen = false;
let chatbotButton, chatbotWidget, chatMessages, chatForm, userInput;


const API_BASE_URL = "https://water-warehouse-chatbot.onrender.com"

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements after DOM is loaded
    chatbotButton = document.getElementById('chatbot-toggle');
    chatbotWidget = document.getElementById('chatbot-widget');
    chatMessages = document.getElementById('chatbot-messages');
    chatForm = document.getElementById('chat-form');
    userInput = document.getElementById('userInput');
    
    // Check if elements exist
    if (!chatbotButton || !chatbotWidget || !chatMessages || !chatForm || !userInput) {
        console.error('Required elements not found. Check your HTML element IDs.');
        return;
    }
    
    // Initialize event listeners
    initializeEventListeners();
});

async function startConversation() {
    try {
        const res = await fetch(`${API_BASE_URL}/start`);
        const data = await res.json();
        threadId = data.thread_id;
        console.log("Thread ID:", threadId);
    } catch (error) {
        console.error("Failed to start conversation: ", error);
    }
}

function toggleWidget() {
    isWidgetOpen = !isWidgetOpen;
    chatbotWidget.classList.toggle('active', isWidgetOpen);
    chatbotButton.classList.toggle('active', isWidgetOpen);
    
    if (isWidgetOpen) {
        userInput.focus();
        if (!threadId) {
            startConversation();
        }
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = message;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function initializeEventListeners() {
    // Form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const userMessage = userInput.value.trim();
        if (!userMessage) return;
        
        appendMessage("user", userMessage);
        userInput.value = "";
        
        // Show typing indicator
        const typingDiv = document.createElement("div");
        typingDiv.className = "message bot";
        typingDiv.textContent = "Typing...";
        typingDiv.id = "typing-indicator";
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Ensure we have a thread ID
        if (!threadId) {
            await startConversation();
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: userMessage,
                    thread_id: threadId,
                }),
            });

            const data = await response.json();
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", data.response || "No response from assistant.");
            
        } catch (error) {
            console.error(error);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", "Sorry, I'm having trouble connecting. Please try again.");
        }
    });

    // Toggle button
    chatbotButton.addEventListener('click', toggleWidget);

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (isWidgetOpen && !chatbotWidget.contains(e.target) && !chatbotButton.contains(e.target)) {
            toggleWidget();
        }
    });

    // Enter key support
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}
    */






/*let threadId = null;
let isWidgetOpen = false;
let chatbotButton, chatbotWidget, chatMessages, chatForm, userInput;

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements after DOM is loaded
    chatbotButton = document.getElementById('chatbot-toggle');
    chatbotWidget = document.getElementById('chatbot-widget');
    chatMessages = document.getElementById('chatbot-messages');
    chatForm = document.getElementById('chat-form');
    userInput = document.getElementById('userInput');
    
    // Check if elements exist
    if (!chatbotButton || !chatbotWidget || !chatMessages || !chatForm || !userInput) {
        console.error('Required elements not found. Check your HTML element IDs.');
        return;
    }
    
    // Initialize event listeners
    initializeEventListeners();
});

async function startConversation() {
    try {
        const res = await fetch("http://localhost:8080/start");
        const data = await res.json();
        threadId = data.thread_id;
        console.log("Thread ID:", threadId);
    } catch (error) {
        console.error("Failed to start conversation: ", error);
    }
}

function toggleWidget() {
    isWidgetOpen = !isWidgetOpen;
    chatbotWidget.classList.toggle('active', isWidgetOpen);
    chatbotButton.classList.toggle('active', isWidgetOpen);
    
    if (isWidgetOpen) {
        userInput.focus();
        if (!threadId) {
            startConversation();
        }
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = message;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function initializeEventListeners() {
    // Form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const userMessage = userInput.value.trim();
        if (!userMessage) return;
        
        appendMessage("user", userMessage);
        userInput.value = "";
        
        // Show typing indicator
        const typingDiv = document.createElement("div");
        typingDiv.className = "message bot";
        typingDiv.textContent = "Typing...";
        typingDiv.id = "typing-indicator";
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Ensure we have a thread ID
        if (!threadId) {
            await startConversation();
        }
        
        try {
            const response = await fetch("http://localhost:8080/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: userMessage,
                    thread_id: threadId,
                }),
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", data.response || "No response from assistant.");
            
        } catch (error) {
            console.error(error);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", "Sorry, I'm having trouble connecting. Please try again.");
        }
    });

    // Toggle button
    chatbotButton.addEventListener('click', toggleWidget);

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (isWidgetOpen && !chatbotWidget.contains(e.target) && !chatbotButton.contains(e.target)) {
            toggleWidget();
        }
    });

    // Enter key support
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}
    */








/*
const API_BASE_URL = "https://water-warehouse-chatbot.onrender.com"
// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements after DOM is loaded
    chatbotButton = document.getElementById('chatbot-toggle');
    chatbotWidget = document.getElementById('chatbot-widget');
    chatMessages = document.getElementById('chatbot-messages');
    chatForm = document.getElementById('chat-form');
    userInput = document.getElementById('userInput');
    
    // Check if elements exist
    if (!chatbotButton || !chatbotWidget || !chatMessages || !chatForm || !userInput) {
        console.error('Required elements not found. Check your HTML element IDs.');
        return;
    }
    
    // Initialize event listeners
    initializeEventListeners();
});

async function startConversation() {
    try {
        const res = await fetch("http://localhost:8080/start");
        const data = await res.json();
        threadId = data.thread_id;
        console.log("Thread ID:", threadId);
    } catch (error) {
        console.error("Failed to start conversation: ", error);
    }
}

function toggleWidget() {
    isWidgetOpen = !isWidgetOpen;
    chatbotWidget.classList.toggle('active', isWidgetOpen);
    chatbotButton.classList.toggle('active', isWidgetOpen);
    
    if (isWidgetOpen) {
        userInput.focus();
        if (!threadId) {
            startConversation();
        }
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = message;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function initializeEventListeners() {
    // Form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const userMessage = userInput.value.trim();
        if (!userMessage) return;
        
        appendMessage("user", userMessage);
        userInput.value = "";
        
        // Show typing indicator
        const typingDiv = document.createElement("div");
        typingDiv.className = "message bot";
        typingDiv.textContent = "Typing...";
        typingDiv.id = "typing-indicator";
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Ensure we have a thread ID
        if (!threadId) {
            await startConversation();
        }
        
        try {
            const response = await fetch("http://localhost:8080/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: userMessage,
                    thread_id: threadId,
                }),
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", data.response || "No response from assistant.");
            
        } catch (error) {
            console.error(error);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById("typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            appendMessage("bot", "Sorry, I'm having trouble connecting. Please try again.");
        }
    });

    // Toggle button
    chatbotButton.addEventListener('click', toggleWidget);

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (isWidgetOpen && !chatbotWidget.contains(e.target) && !chatbotButton.contains(e.target)) {
            toggleWidget();
        }
    });

    // Enter key support
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}
*/