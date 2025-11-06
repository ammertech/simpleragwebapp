document.addEventListener('DOMContentLoaded', () => {
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const chatMessages = document.getElementById('chat-messages');
    const sourcesList = document.getElementById('sources-list');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Submit form event
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        
        if (!query) return;
        
        // Add user message to the chat
        addMessage('user', query);
        
        // Clear input
        queryInput.value = '';
        
        // Show loading indicator
        loadingIndicator.style.display = 'flex';
        
        try {
            // Send query to server
            const response = await fetchAnswer(query);
            
            // Add bot response to the chat
            addMessage('bot', response.answer);
            
            // Update sources
            updateSources(response.sources);
            
        } catch (error) {
            console.error('Error:', error);
            addMessage('system', 'Es ist ein Fehler aufgetreten. Bitte versuche es später noch einmal.');
        } finally {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
        }
    });

    // Fetch answer from server
    async function fetchAnswer(query) {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: 3
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        return await response.json();
    }

    // Add a message to the chat
    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Convert any Markdown-style formatting to HTML
        const formattedContent = formatMarkdown(content);
        messageContent.innerHTML = formattedContent;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Simple Markdown formatter
    function formatMarkdown(text) {
        // Replace line breaks with <br>
        let formatted = text.replace(/\n/g, '<br>');
        
        // Bold: **text** -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic: *text* -> <em>text</em>
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert bullet lists
        formatted = formatted.replace(/- (.*?)(?=<br>|$)/g, '• $1');
        
        return formatted;
    }

    // Update the sources list
    function updateSources(sources) {
        sourcesList.innerHTML = '';
        
        if (!sources || sources.length === 0) {
            sourcesList.innerHTML = '<p class="no-sources">Keine Quellen verfügbar.</p>';
            return;
        }
        
        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            
            // Format the source score as percentage
            const scorePercentage = Math.round(source.score * 100);
            
            sourceItem.innerHTML = `
                <h3>${source.title || 'Unbekanntes Dokument'}</h3>
                <div class="source-score">Relevanz: ${scorePercentage}%</div>
            `;
            
            sourcesList.appendChild(sourceItem);
        });
    }
});
