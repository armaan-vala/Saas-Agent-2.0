document.addEventListener('DOMContentLoaded', function() {
    const agentGrid = document.getElementById('agentGrid');
    const createAgentBtn = document.getElementById('createAgentBtn');

    // Event listener for the "Create New Agent" button
    createAgentBtn.addEventListener('click', () => {
        window.location.href = '/create';
    });

    // Function to fetch agents and display them
    async function loadAgents() {
        try {
            const response = await fetch('/api/agents');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const agents = await response.json();

            agentGrid.innerHTML = ''; // Clear existing content

            // Create a card for each agent
            agents.forEach(agent => {
                const card = document.createElement('div');
                card.className = 'agent-card';
                card.dataset.agentId = agent.id; // Store the agent's ID

                card.innerHTML = `
                    <div class="status-indicator ready"><span></span>Ready</div>
                    <div class="content">
                        <h2 class="agent-title">${agent.agent_name}</h2>
                        <p class="agent-description">${agent.system_prompt}</p>
                    </div>
                    <div class="icon-container">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7 text-gray-400">
                           <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m2.25 2.25H15M3.75 21.75c0-2.485 2.015-4.5 4.5-4.5H16.5c2.485 0 4.5 2.015 4.5 4.5v.75H3.75v-.75zM16.5 9.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0z" />
                        </svg>
                    </div>
                `;

                // Add click event listener to the card to navigate to the chat page
                card.addEventListener('click', () => {
                    window.location.href = `/chat/${agent.id}`;
                });

                agentGrid.appendChild(card);
            });

        } catch (error) {
            agentGrid.innerHTML = '<p class="text-red-500">Failed to load agents.</p>';
            console.error('There was a problem with the fetch operation:', error);
        }
    }

    // Load agents when the page is ready
    loadAgents();
});

