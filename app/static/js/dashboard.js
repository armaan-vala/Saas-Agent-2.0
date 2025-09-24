document.addEventListener('DOMContentLoaded', function() {
    const agentGrid = document.getElementById('agentGrid');
    const createAgentBtn = document.getElementById('createAgentBtn');

    // Event listener for the "Create New Agent" button
    createAgentBtn.addEventListener('click', () => {
        window.location.href = '/create';
    });

    
    async function loadAgents() {
        try {
            const response = await fetch('/api/agents');
            if (!response.ok) throw new Error('Failed to load agents');
            const agents = await response.json();
            agentGrid.innerHTML = '';

            agents.forEach(agent => {
                const card = document.createElement('div');
                card.className = 'agent-card';
                card.dataset.agentId = agent.id;

                
                card.innerHTML = `
                    <div class="card-header">
                        <div class="status-indicator ready"><span></span>Ready</div>
                        <button class="delete-btn" data-agent-id="${agent.id}" title="Delete Agent">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-1.157.046-2.14.349-2.868.786A2.983 2.983 0 00.5 7.5v6.059a3 3 0 00.51 1.658l.144.248c.18.31.42.583.694.811A2.982 2.982 0 004.5 17.5h11a2.982 2.982 0 002.652-1.233c.273-.228.514-.5.694-.811l.144-.248A3 3 0 0019.5 13.56V7.5a2.983 2.983 0 00-2.632-2.521c-.728-.437-1.711-.74-2.868-.786v-.443A2.75 2.75 0 0011.25 1h-2.5zM10 5.5a.75.75 0 00-1.5 0v6a.75.75 0 001.5 0v-6zM13.25 5.5a.75.75 0 01.75.75v6a.75.75 0 01-1.5 0v-6a.75.75 0 01.75-.75zM6.75 5.5a.75.75 0 01.75.75v6a.75.75 0 01-1.5 0v-6a.75.75 0 01.75-.75z" clip-rule="evenodd" /></svg>
                        </button>
                    </div>
                    <div class="content">
                        <h2 class="agent-title">${agent.agent_name}</h2>
                        <p class="agent-description">${agent.system_prompt}</p>
                    </div>
                    <div class="icon-container">
                        <!-- Icon can go here -->
                    </div>
                `;

                // Click event for the whole card to go to chat
                card.addEventListener('click', (e) => {
                    // Prevent navigation if the delete button was clicked
                    if (!e.target.closest('.delete-btn')) {
                        window.location.href = `/chat/${agent.id}`;
                    }
                });

                agentGrid.appendChild(card);
            });

        } catch (error) {
            agentGrid.innerHTML = `<p class="text-red-500">${error.message}</p>`;
        }
    }
    
    // Load agents when the page is ready
    loadAgents();

    // DELETE AGENT LOGIC 
    agentGrid.addEventListener('click', async function(e) {
        const deleteButton = e.target.closest('.delete-btn');
        if (deleteButton) {
            const agentId = deleteButton.dataset.agentId;
            const agentCard = deleteButton.closest('.agent-card');
            const agentName = agentCard.querySelector('.agent-title').textContent;

            //  confirmation
            if (confirm(`Are you sure you want to delete the agent "${agentName}"? This action cannot be undone.`)) {
                try {
                    const response = await fetch(`/api/agents/${agentId}`, {
                        method: 'DELETE',
                    });

                    if (response.ok) {
                        // Remove the card from the UI on success
                        agentCard.remove();
                    } else {
                        alert('Failed to delete the agent.');
                    }
                } catch (error) {
                    alert('An error occurred while deleting the agent.');
                }
            }
        }
    });
    
});

