document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createAgentForm');
    const agentNameInput = document.getElementById('agentName');
    const systemPromptInput = document.getElementById('systemPrompt');
    const statusMessage = document.getElementById('statusMessage');
    const saveButton = form.querySelector('button[type="submit"]');

    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileListContainer = document.getElementById('fileList');
    let filesToUpload = [];

    // --- File Drag and Drop Logic ---
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        filesToUpload = [...filesToUpload, ...files];
        renderFileList();
    }

    function renderFileList() {
        fileListContainer.innerHTML = '';
        if (filesToUpload.length > 0) {
            const list = document.createElement('ul');
            list.className = 'w-full';
            filesToUpload.forEach((file, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'file-item';
                listItem.innerHTML = `
                    <span>${file.name}</span>
                    <button type="button" class="text-red-500 hover:text-red-700" data-index="${index}">&times;</button>
                `;
                list.appendChild(listItem);
            });
            fileListContainer.appendChild(list);
        }
    }
    
    fileListContainer.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON') {
            const index = parseInt(e.target.dataset.index, 10);
            filesToUpload.splice(index, 1);
            renderFileList();
        }
    });


    // --- Form Submission Logic ---
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        saveButton.disabled = true;
        statusMessage.textContent = 'Creating agent...';

        // Step 1: Create the agent
        const agentData = {
            agent_name: agentNameInput.value,
            system_prompt: systemPromptInput.value
        };

        try {
            const agentResponse = await fetch('/api/agents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(agentData)
            });

            if (!agentResponse.ok) {
                throw new Error('Failed to create agent.');
            }
            
            const agentResult = await agentResponse.json();
            const newAgentId = agentResult.agent_id; // IMPORTANT: We need the new agent's ID

            // Step 2: If there are files, upload them
            if (filesToUpload.length > 0) {
                statusMessage.textContent = `Agent created. Uploading ${filesToUpload.length} documents...`;
                
                const formData = new FormData();
                filesToUpload.forEach(file => {
                    formData.append('files[]', file);
                });

                const uploadResponse = await fetch(`/api/agents/${newAgentId}/documents`, {
                    method: 'POST',
                    body: formData
                });

                if (!uploadResponse.ok) {
                    throw new Error('Failed to upload documents.');
                }
            }

            statusMessage.textContent = 'Agent and documents processed successfully! Redirecting...';
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);

        } catch (error) {
            statusMessage.textContent = error.message;
            saveButton.disabled = false;
        }
    });
});