document.addEventListener('DOMContentLoaded', () => {
    const agentId = document.querySelector('.main-layout').dataset.agentId;
    const agentName = document.querySelector('.main-layout').dataset.agentName; 
    const conversationList = document.getElementById('conversationList');
    const newChatBtn = document.getElementById('newChatBtn');
    const messageArea = document.getElementById('messageArea');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    const documentUploadInput = document.getElementById('documentUploadInput');
    const uploadImageBtn = document.getElementById('uploadImageBtn');
    const imageUploadInput = document.getElementById('imageUploadInput');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const uploadNotification = document.getElementById('uploadNotification');

    let currentConversationId = null;
    let selectedImageFile = null; // To hold the currently selected image file
    const converter = new showdown.Converter(); // Markdown converter

    // --- Utility Functions ---

    function showNotification(message, type = 'info', duration = 3000) {
        uploadNotification.textContent = message;
        uploadNotification.className = `upload-notification show ${type}`; // Add type for styling
        setTimeout(() => {
            uploadNotification.classList.remove('show');
        }, duration);
    }

    function displayMessage(sender, content, timestamp, image_src = null, isNew = true) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'sent' : 'received');

        const header = document.createElement('div');
        header.classList.add('message-header');
        const senderName = document.createElement('strong');
        senderName.textContent = sender === 'user' ? 'You' : 'Agent';
        const timeSpan = document.createElement('span');
        timeSpan.classList.add('message-timestamp');
        timeSpan.textContent = new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        header.appendChild(senderName);
        header.appendChild(document.createTextNode(' ')); // Space between name and time
        header.appendChild(timeSpan);
        messageDiv.appendChild(header);

        if (image_src) {
            const img = document.createElement('img');
            img.src = image_src;
            img.alt = "Uploaded image";
            img.classList.add('message-image');
            messageDiv.appendChild(img);
        }

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        // Convert markdown to HTML for agent responses
        contentDiv.innerHTML = sender === 'agent' ? converter.makeHtml(content) : content;
        messageDiv.appendChild(contentDiv);

        messageArea.appendChild(messageDiv);

        if (isNew) {
            messageArea.scrollTop = messageArea.scrollHeight; // Scroll to bottom for new messages
        }
    }

    async function fetchConversations() {
        try {
            // CHANGED: Added '/api' prefix
            const response = await fetch(`/api/agents/${agentId}/conversations`); 
            const conversations = await response.json();
            conversationList.innerHTML = ''; // Clear existing list
            
            if (conversations.length === 0) {
                conversationList.innerHTML = '<li class="text-gray-400 p-2">No chats yet. Start a new one!</li>';
            } else {
                conversations.forEach(conv => addConversationToSidebar(conv));
                console.log("DEBUG: currentConversationId before fetchConversations logic:", currentConversationId);
                if (!currentConversationId) {
                    loadConversation(conversations[0].id, conversations[0].title);
                } else {
                    const activeItem = document.querySelector(`.conversation-item[data-conv-id="${currentConversationId}"]`);
                    if (activeItem) {
                        activeItem.classList.add('active');
                    } else {
                        loadConversation(conversations[0].id, conversations[0].title);
                    }
                }
            }
        } catch (error) {
            console.error('Error fetching conversations:', error);
            showNotification('Error loading conversations.', 'error');
        }
    }

    async function loadConversation(convId, convTitle) {
        currentConversationId = convId;
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeItem = document.querySelector(`.conversation-item[data-conv-id="${convId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
        
        messageArea.innerHTML = `
            <div class="message received initial-message">
                <p>Hello! I am the {{ agent.agent_name }}. I am ready to answer questions based on the documents you've provided, or you can upload new documents using the '+' button.</p>
            </div>
        `; // Clear and add initial message

        try {
            
            const response = await fetch(`/api/conversations/${convId}/messages`); 
            const messages = await response.json();
            messages.forEach(msg => displayMessage(msg.sender, msg.content, msg.timestamp, msg.image_src, false));
            messageArea.scrollTop = messageArea.scrollHeight; // Scroll to bottom
        } catch (error) {
            console.error('Error fetching messages:', error);
            showNotification('Error loading messages.', 'error');
        }
    }

    function addConversationToSidebar(conv) {
        const listItem = document.createElement('li');
        listItem.classList.add('conversation-item');
        listItem.dataset.convId = conv.id;

        const titleSpan = document.createElement('span');
        titleSpan.textContent = conv.title;
        titleSpan.title = conv.title; // Show full title on hover

        const renameBtn = document.createElement('button');
        renameBtn.classList.add('rename-conv-btn');
        renameBtn.innerHTML = '<i class="fas fa-edit"></i>'; 
        renameBtn.title = 'Rename conversation';

        listItem.appendChild(titleSpan);
        listItem.appendChild(renameBtn);
        conversationList.prepend(listItem); // Add to top of the list

        listItem.addEventListener('click', () => {
            if (currentConversationId !== conv.id) {
                loadConversation(conv.id, conv.title);
            }
        });

        renameBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent loading conversation when renaming
            const newTitle = prompt('Enter new title for this conversation:', conv.title);
            if (newTitle && newTitle.trim() !== '' && newTitle !== conv.title) {
                renameConversation(conv.id, newTitle.trim(), titleSpan);
            }
        });
    }

    async function renameConversation(convId, newTitle, titleSpanElement) {
        try {
            
            const response = await fetch(`/api/conversations/${convId}/rename`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });
            const data = await response.json();
            if (response.ok) {
                titleSpanElement.textContent = data.new_title;
                titleSpanElement.title = data.new_title;
                showNotification('Conversation renamed successfully!', 'success');
            } else {
                showNotification(`Error renaming conversation: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Network error renaming conversation:', error);
            showNotification('Network error renaming conversation.', 'error');
        }
    }


    

    newChatBtn.addEventListener('click', () => {
        currentConversationId = null; // Reset conversation ID to start a new one
        messageArea.innerHTML = `
            <div class="message received initial-message">
                <p>Hello! I am the ${agentName}. I am ready to answer questions based on the documents you've provided, or you can upload new documents using the '+' button.</p>
            </div>
        `;
        document.querySelectorAll('.conversation-item').forEach(item => item.classList.remove('active'));
        userInput.focus();
        selectedImageFile = null;
        imagePreviewContainer.innerHTML = '';
    });


    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });


    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        let imageData = null;

        if (!message && !selectedImageFile) {
            return; // Don't send empty message
        }

        if (selectedImageFile) {
            imageData = await convertFileToBase64(selectedImageFile);
            if (!imageData) {
                showNotification('Failed to read image file.', 'error');
                return;
            }
        }

        // Display user message immediately
        displayMessage('user', message || "Image uploaded.", new Date().toISOString(), imageData);
        userInput.value = ''; // Clear input
        userInput.style.height = 'auto'; // Reset textarea height
        selectedImageFile = null; // Clear selected image
        imagePreviewContainer.innerHTML = ''; // Clear image preview

        try {
            const payload = { // Creating a payload variable for logging
                agent_id: agentId,
                message: message,
                conversation_id: currentConversationId,
                image: imageData
            };
           
        
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload) // Using the payload variable
            });


            const data = await response.json();

            if (response.ok) {
                displayMessage('agent', data.response, new Date().toISOString());
                if (!currentConversationId) {
                    currentConversationId = data.conversation_id;
                    await fetchConversations(); // Reload sidebar to show new conversation
                } else {
                    const activeConvItem = document.querySelector(`.conversation-item[data-conv-id="${currentConversationId}"]`);
                    if (activeConvItem) {
                        activeConvItem.remove(); 
                        await fetchConversations(); 
                    }
                }
            } else {
                displayMessage('agent', `Error: ${data.error || 'Something went wrong.'}`, new Date().toISOString());
                showNotification(`Chat error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            displayMessage('agent', `Network error: Could not connect to the server.`, new Date().toISOString());
            showNotification('Network error. Check console for details.', 'error');
        }
    });

    uploadFileBtn.addEventListener('click', () => {
        documentUploadInput.click();
    });

    documentUploadInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (files.length === 0) return;

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files[]', files[i]);
        }

        showNotification(`Uploading ${files.length} document(s)...`, 'info');

        try {
            // CHANGED: Added '/api' prefix
            const response = await fetch(`/api/agents/${agentId}/documents`, { 
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                showNotification(data.message, 'success');
                displayMessage('agent', `Started processing ${files.length} document(s). Task IDs: ${data.task_ids.join(', ')}.`, new Date().toISOString());
                data.task_ids.forEach(taskId => pollTaskStatus(taskId));
            } else {
                showNotification(`Upload failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error uploading documents:', error);
            showNotification('Network error during document upload.', 'error');
        } finally {
            documentUploadInput.value = ''; // Clear file input
        }
    });

    async function pollTaskStatus(taskId) {
        const interval = setInterval(async () => {
            try {
                // CHANGED: Added '/api' prefix
                const response = await fetch(`/api/tasks/${taskId}`); 
                const data = await response.json();

                if (data.state === 'SUCCESS') {
                    clearInterval(interval);
                    showNotification(`Document processing task ${taskId} completed successfully!`, 'success');
                    displayMessage('agent', `Document processing completed for task ${taskId}. You can now ask questions about the new documents.`, new Date().toISOString());
                } else if (data.state === 'FAILURE') {
                    clearInterval(interval);
                    showNotification(`Document processing task ${taskId} failed: ${data.status}`, 'error', 10000);
                    displayMessage('agent', `Document processing failed for task ${taskId}. Details: ${data.status}`, new Date().toISOString());
                } else {
                    // console.log(`Task ${taskId} status: ${data.status}`);
                }
            } catch (error) {
                console.error(`Error polling task ${taskId} status:`, error);
                clearInterval(interval);
                showNotification(`Error polling status for task ${taskId}.`, 'error');
            }
        }, 5000); // Poll every 5 seconds
    }

    // --- Image Upload Logic ---
    uploadImageBtn.addEventListener('click', () => {
        imageUploadInput.click();
    });

    imageUploadInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            selectedImageFile = file;
            displayImagePreview(file);
        }
        imageUploadInput.value = ''; // Clear input so same file can be selected again
    });

    function displayImagePreview(file) {
        imagePreviewContainer.innerHTML = ''; // Clear previous previews
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.classList.add('image-preview-item');
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="Image preview">
                <button class="remove-image-btn" aria-label="Remove image">&times;</button>
            `;
            imagePreviewContainer.appendChild(previewItem);

            previewItem.querySelector('.remove-image-btn').addEventListener('click', () => {
                selectedImageFile = null;
                imagePreviewContainer.innerHTML = '';
            });
        };
        reader.readAsDataURL(file); // Read as base64
    }

    function convertFileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    // Initial load
    fetchConversations();
});

