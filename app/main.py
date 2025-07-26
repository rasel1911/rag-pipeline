from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from datetime import datetime
import json
import requests
from google import genai
from dotenv import load_dotenv
import bn
load_dotenv()

client = genai.Client()



# Get all chunk texts
response = requests.get("http://localhost:8001/chunks/texts")
chunk_texts = response.json()
list_chunk= []
for chunk in chunk_texts:
    list_chunk.append(chunk['chunk_text'])
#print(list_chunk)



app = FastAPI(title="Chatbot API", description="A modern chatbot interface")

# Pydantic models
class Message(BaseModel):
    content: str
    timestamp: datetime = None
    sender: str = "user"

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime
    sender: str = "bot"

class ChatHistory(BaseModel):
    messages: List[Dict]

# In-memory storage for chat sessions
chat_sessions: Dict[str, List[Dict]] = {}

def search_chunks_multiple_keywords(chunks, keywords):
    print("search start")
    # Normalize keywords to lowercase
    keywords = [k.lower() for k in keywords]
    
    # Search for any of the keywords in each chunk
    result = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        if any(k in chunk_lower for k in keywords):
            result.append(chunk)

    return result

def output_get(content,question):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f'{content} read this content and give {question} this question answer. only give answer',
    )
    return response.text

# Simple bot responses (you can replace this with your AI model)
def generate_bot_response(user_message: str) -> str:
    user_message = user_message.lower().strip()
    print(user_message)
    st=bn.remove_stopwords(user_message)
    words = bn.tokenizer(st) # or bn.tokenizer(text, 'word')
    found_chunks = search_chunks_multiple_keywords(list_chunk, words)
    result_al = []
    for i, chunk in enumerate(found_chunks):
        result_al.append(chunk)
    result = output_get(result_al,user_message)
    print(result)
    return result
    

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Modern Chatbot</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }

                .chat-container {
                    width: 90%;
                    max-width: 800px;
                    height: 80vh;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    backdrop-filter: blur(10px);
                }

                .chat-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    position: relative;
                }

                .chat-header h1 {
                    font-size: 24px;
                    font-weight: 600;
                }

                .status-indicator {
                    position: absolute;
                    right: 20px;
                    top: 50%;
                    transform: translateY(-50%);
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: #4ade80;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }

                .chat-messages {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }

                .message {
                    max-width: 70%;
                    padding: 12px 16px;
                    border-radius: 18px;
                    position: relative;
                    animation: slideIn 0.3s ease-out;
                }

                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .user-message {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    align-self: flex-end;
                    margin-left: auto;
                }

                .bot-message {
                    background: #f1f5f9;
                    color: #334155;
                    align-self: flex-start;
                    border: 1px solid #e2e8f0;
                }

                .message-time {
                    font-size: 11px;
                    opacity: 0.7;
                    margin-top: 4px;
                }

                .chat-input-container {
                    padding: 20px;
                    background: #f8fafc;
                    border-top: 1px solid #e2e8f0;
                }

                .input-wrapper {
                    display: flex;
                    gap: 12px;
                    align-items: flex-end;
                }

                .chat-input {
                    flex: 1;
                    padding: 12px 16px;
                    border: 2px solid #e2e8f0;
                    border-radius: 25px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.3s ease;
                    resize: none;
                    min-height: 44px;
                    max-height: 120px;
                }

                .chat-input:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }

                .send-button {
                    width: 44px;
                    height: 44px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s ease;
                    flex-shrink: 0;
                }

                .send-button:hover {
                    transform: scale(1.05);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }

                .send-button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }

                .typing-indicator {
                    display: none;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 16px;
                    background: #f1f5f9;
                    border-radius: 18px;
                    max-width: 70px;
                    animation: slideIn 0.3s ease-out;
                }

                .typing-dots {
                    display: flex;
                    gap: 4px;
                }

                .typing-dot {
                    width: 6px;
                    height: 6px;
                    background: #94a3b8;
                    border-radius: 50%;
                    animation: typingAnimation 1.4s infinite ease-in-out;
                }

                .typing-dot:nth-child(1) { animation-delay: -0.32s; }
                .typing-dot:nth-child(2) { animation-delay: -0.16s; }

                @keyframes typingAnimation {
                    0%, 80%, 100% {
                        transform: scale(0.8);
                        opacity: 0.5;
                    }
                    40% {
                        transform: scale(1);
                        opacity: 1;
                    }
                }

                .clear-button {
                    background: none;
                    border: none;
                    color: #64748b;
                    cursor: pointer;
                    padding: 8px;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                }

                .clear-button:hover {
                    background: #f1f5f9;
                    color: #334155;
                }

                /* Scrollbar styling */
                .chat-messages::-webkit-scrollbar {
                    width: 6px;
                }

                .chat-messages::-webkit-scrollbar-track {
                    background: #f1f5f9;
                }

                .chat-messages::-webkit-scrollbar-thumb {
                    background: #cbd5e1;
                    border-radius: 3px;
                }

                .chat-messages::-webkit-scrollbar-thumb:hover {
                    background: #94a3b8;
                }

                /* Mobile responsiveness */
                @media (max-width: 768px) {
                    .chat-container {
                        width: 95%;
                        height: 90vh;
                        border-radius: 15px;
                    }
                    
                    .message {
                        max-width: 85%;
                    }
                    
                    .chat-header h1 {
                        font-size: 20px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <h1>🤖 AI Assistant</h1>
                    <div class="status-indicator">
                        <div class="status-dot"></div>
                        <span style="font-size: 12px;">Online</span>
                    </div>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        <div><h2>Hello! I'm your AI assistant</h2></div>
                        <div class="message-time" id="welcomeTime"></div>
                    </div>
                </div>
                
                <div class="typing-indicator" id="typingIndicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <div class="input-wrapper">
                        <button class="clear-button" onclick="clearChat()" title="Clear chat">
                            🗑️
                        </button>
                        <textarea 
                            class="chat-input" 
                            id="messageInput" 
                            placeholder="Type your message here..."
                            rows="1"
                        ></textarea>
                        <button class="send-button" id="sendButton" onclick="sendMessage()">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22,2 15,22 11,13 2,9"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <script>
                const chatMessages = document.getElementById('chatMessages');
                const messageInput = document.getElementById('messageInput');
                const sendButton = document.getElementById('sendButton');
                const typingIndicator = document.getElementById('typingIndicator');
                
                // Set welcome message time
                document.getElementById('welcomeTime').textContent = formatTime(new Date());
                
                // Auto-resize textarea
                messageInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
                });
                
                // Send message on Enter (but allow Shift+Enter for new lines)
                messageInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                function formatTime(date) {
                    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                }
                
                function addMessage(content, isUser = false) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                    
                    const now = new Date();
                    messageDiv.innerHTML = `
                        <div>${content}</div>
                        <div class="message-time">${formatTime(now)}</div>
                    `;
                    
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                function showTypingIndicator() {
                    typingIndicator.style.display = 'flex';
                    chatMessages.appendChild(typingIndicator);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                function hideTypingIndicator() {
                    typingIndicator.style.display = 'none';
                    if (typingIndicator.parentNode) {
                        typingIndicator.parentNode.removeChild(typingIndicator);
                    }
                }
                
                async function sendMessage() {
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    // Add user message
                    addMessage(message, true);
                    messageInput.value = '';
                    messageInput.style.height = 'auto';
                    
                    // Disable send button
                    sendButton.disabled = true;
                    
                    // Show typing indicator
                    showTypingIndicator();
                    
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                content: message,
                                sender: 'user'
                            }),
                        });
                        
                        if (!response.ok) {
                            throw new Error('Failed to send message');
                        }
                        
                        const data = await response.json();
                        
                        // Hide typing indicator and add bot response
                        setTimeout(() => {
                            hideTypingIndicator();
                            addMessage(data.message);
                            sendButton.disabled = false;
                        }, 1000); // Simulate thinking time
                        
                    } catch (error) {
                        hideTypingIndicator();
                        addMessage('Sorry, I encountered an error. Please try again.');
                        sendButton.disabled = false;
                    }
                }
                
                function clearChat() {
                    chatMessages.innerHTML = `
                        <div class="message bot-message">
                            <div>Hello! I'm your AI assistant. How can I help you today?</div>
                            <div class="message-time">${formatTime(new Date())}</div>
                        </div>
                    `;
                }
                
                // Focus input on page load
                messageInput.focus();
            </script>
        </body>
        </html>
    """

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: Message):
    try:
        # Generate bot response
        bot_response = generate_bot_response(message.content)
        
        # Create response
        response = ChatResponse(
            message=bot_response,
            timestamp=datetime.now(),
            sender="bot"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)