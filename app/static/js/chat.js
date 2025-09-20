document.addEventListener('DOMContentLoaded', function() {
    // Zaroori elements ko select karna
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messageArea = document.getElementById('messageArea');
    const chatContainer = document.querySelector('.chat-container');
    const converter = new showdown.Converter();

    // Naye elements file upload ke liye
    const uploadBtn = document.getElementById('uploadBtn');
    const documentUploadInput = document.getElementById('documentUploadInput');
    const uploadNotification = document.getElementById('uploadNotification');

    // --- Chat Logic ---
    chatForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const userMessage = userInput.value.trim();
        const agentId = chatContainer.dataset.agentId;
        if (userMessage === '' || !agentId) return;

        addMessage(userMessage, 'sent');
        userInput.value = '';

        const typingIndicator = addMessage('...', 'received', true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage, agent_id: agentId }),
            });
            const result = await response.json();
            
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

    // --- NAYA: File Upload Logic ---
    uploadBtn.addEventListener('click', () => {
        documentUploadInput.click(); // Chhipe hue input ko trigger karna
    });

    documentUploadInput.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (files.length === 0) return;

        const agentId = chatContainer.dataset.agentId;
        const formData = new FormData();
        for (const file of files) {
            formData.append('files[]', file);
        }

        showNotification(`Uploading ${files.length} document(s)...`, 'info');

        try {
            const response = await fetch(`/api/agents/${agentId}/documents`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                showNotification('Upload successful! Your agent is now learning from the new documents.', 'success');
                // Agent ko naye gyaan ke baare mein batana
                addMessage(`I am now processing the ${files.length} new document(s) you've provided.`, 'received');
            } else {
                const errorResult = await response.json();
                showNotification(`Upload failed: ${errorResult.error}`, 'error');
            }
        } catch (error) {
            showNotification('An error occurred during upload.', 'error');
        } finally {
            // File input ko reset karna taaki user wahi file dobara select kar sake
            e.target.value = null;
        }
    });
    
    // --- Helper Functions ---
    function addMessage(text, type, isTyping = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        const p = document.createElement('p');
        
        if (type === 'received' && !isTyping) {
            p.innerHTML = converter.makeHtml(text);
        } else {
            p.textContent = text;
        }
        messageDiv.appendChild(p);
        messageArea.appendChild(messageDiv);
        messageArea.scrollTop = messageArea.scrollHeight;
        return messageDiv;
    }

    function showNotification(message, type = 'info') {
        uploadNotification.textContent = message;
        uploadNotification.className = `upload-notification show ${type}`;
        setTimeout(() => {
            uploadNotification.classList.remove('show');
        }, 5000); // 5 second baad notification gayab ho jaayega
    }
});


// document.addEventListener('DOMContentLoaded', function() {
//     // Zaroori elements ko select karna
//     const chatForm = document.getElementById('chatForm');
//     const userInput = document.getElementById('userInput');
//     const messageArea = document.getElementById('messageArea');
//     const chatContainer = document.querySelector('.chat-container');
//     // Naya: Markdown converter ko initialize karna
//     const converter = new showdown.Converter();

//     chatForm.addEventListener('submit', async function(event) {
//         event.preventDefault();
//         const userMessage = userInput.value.trim();
//         const agentId = chatContainer.dataset.agentId;

//         if (userMessage === '' || !agentId) return;

//         // 1. User ka message turant dikhana
//         addMessage(userMessage, 'sent');
//         userInput.value = '';

//         // 2. "Typing..." indicator dikhana
//         const typingIndicator = addMessage('...', 'received', true);
        
//         try {
//             // 3. Backend API ko data bhejna
//             const response = await fetch('/api/chat', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     message: userMessage,
//                     agent_id: agentId, 
//                 }),
//             });

//             const result = await response.json();
            
//             // 4. Typing indicator hatakar AI ka jawab dikhana
//             typingIndicator.remove();
//             if (response.ok) {
//                 addMessage(result.response, 'received');
//             } else {
//                 addMessage(`Error: ${result.error}`, 'received');
//             }

//         } catch (error) {
//             typingIndicator.remove();
//             addMessage('Sorry, something went wrong. Please try again.', 'received');
//         }
//     });

//     // Helper function to add a message bubble to the chat window
//     function addMessage(text, type, isTyping = false) {
//         const messageDiv = document.createElement('div');
//         messageDiv.className = `message ${type}`;
        
//         const p = document.createElement('p');
        
//         // YEH HAI NAYA LOGIC: Agar AI ka jawab hai, toh Markdown ko HTML mein convert karo
//         if (type === 'received' && !isTyping) {
//             const html = converter.makeHtml(text);
//             p.innerHTML = html;
//         } else {
//             p.textContent = text;
//         }

//         messageDiv.appendChild(p);

//         if (isTyping) {
//             messageDiv.classList.add('typing');
//         }

//         messageArea.appendChild(messageDiv);
//         messageArea.scrollTop = messageArea.scrollHeight;
//         return messageDiv;
//     }
// });