// Kanban Board Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sortable for each column
    const columns = ['atendimento_inicial', 'proposta_enviada', 'venda_andamento', 'venda_concluida', 'pos_venda'];
    
    columns.forEach(columnId => {
        const columnElement = document.getElementById(columnId);
        if (columnElement) {
            new Sortable(columnElement, {
                group: 'kanban',
                animation: 150,
                ghostClass: 'sortable-ghost',
                dragClass: 'sortable-drag',
                onEnd: function(evt) {
                    const cardId = evt.item.dataset.cardId;
                    const newColumn = evt.to.dataset.column;
                    
                    // Send AJAX request to update card position
                    moveCard(cardId, newColumn);
                }
            });
        }
    });
});

function moveCard(cardId, newColumn) {
    fetch(`/kanban/card/${cardId}/move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            column: newColumn
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Cartão movido com sucesso!', 'success');
            // Update column counters
            updateColumnCounters();
        } else {
            showNotification('Erro ao mover cartão!', 'error');
            // Reload page to reset positions
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erro de conexão!', 'error');
        window.location.reload();
    });
}

function updateColumnCounters() {
    const columns = ['atendimento_inicial', 'proposta_enviada', 'venda_andamento', 'venda_concluida', 'pos_venda'];
    
    columns.forEach(columnId => {
        const columnElement = document.getElementById(columnId);
        const cards = columnElement.querySelectorAll('.kanban-card');
        const header = columnElement.closest('.card').querySelector('.card-header h6');
        
        // Update counter in header
        const headerText = header.textContent;
        const newText = headerText.replace(/\(\d+\)/, `(${cards.length})`);
        header.textContent = newText;
    });
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Card interaction handlers
document.addEventListener('click', function(e) {
    // Handle card menu clicks
    if (e.target.closest('.dropdown-toggle')) {
        e.stopPropagation();
    }
    
    // Handle card click for details (optional)
    if (e.target.closest('.kanban-card') && !e.target.closest('.dropdown')) {
        const card = e.target.closest('.kanban-card');
        // You can add card detail modal here
        console.log('Card clicked:', card.dataset.cardId);
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N to create new card
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const newCardButton = document.querySelector('[data-bs-target="#cardModal"]');
        if (newCardButton) {
            newCardButton.click();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Auto-refresh functionality (optional)
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        // Check for updates without full page reload
        console.log('Auto-refresh check...');
        // You can implement WebSocket or polling here
    }, 30000); // Check every 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Start auto-refresh when page loads
// startAutoRefresh();

// Stop auto-refresh when page unloads
window.addEventListener('beforeunload', stopAutoRefresh);

// Handle visibility change (pause when tab is hidden)
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        // startAutoRefresh();
    }
});
