document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messageArea = document.getElementById('messageArea');
    const systemPromptInput = document.getElementById('systemPrompt');

    chatForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;

        // 1. Display user's message immediately
        addMessage(userMessage, 'sent');
        userInput.value = '';

        // 2. Show a "typing" indicator
        const typingIndicator = addMessage('...', 'received', true);
        
        try {
            // 3. Send data to the backend API
            const systemPrompt = systemPromptInput.value;
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    system_prompt: systemPrompt,
                }),
            });

            const result = await response.json();
            
            // 4. Remove typing indicator and display AI response
            typingIndicator.remove();
            if (response.ok) {
                addMessage(result.response, 'received');
            } else {
                addMessage(`Error: ${result.error}`, 'received');
            }

        } catch (error) {
            typingIndicator.remove();
            addMessage('Sorry, something went wrong. Please try again.', 'received');
        }
    });

    // Helper function to add a message bubble to the chat window
    function addMessage(text, type, isTyping = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const p = document.createElement('p');
        p.textContent = text;
        messageDiv.appendChild(p);

        if (isTyping) {
            messageDiv.classList.add('typing');
        }

        messageArea.appendChild(messageDiv);
        // Scroll to the bottom to see the new message
        messageArea.scrollTop = messageArea.scrollHeight;
        return messageDiv;
    }
});
