document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createAgentForm');
    const messageDiv = document.getElementById('form-message');

    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent the default form submission

        const agentName = document.getElementById('agent_name').value;
        const systemPrompt = document.getElementById('system_prompt').value;

        messageDiv.textContent = 'Saving agent...';
        messageDiv.className = 'text-center mt-4 text-blue-600';

        try {
            const response = await fetch('/api/agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_name: agentName,
                    system_prompt: systemPrompt,
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to create agent');
            }
            
            messageDiv.textContent = result.message;
            messageDiv.className = 'text-center mt-4 text-green-600';

            // Redirect back to the dashboard after 2 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);

        } catch (error) {
            messageDiv.textContent = `Error: ${error.message}`;
            messageDiv.className = 'text-center mt-4 text-red-600';
        }
    });
});
