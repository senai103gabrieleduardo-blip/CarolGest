// Main JavaScript functionality for Monteiro Corretora
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\d{2})(\d{0,5})(\d{0,4})/, function(match, p1, p2, p3) {
                    if (p3) return `(${p1}) ${p2}-${p3}`;
                    if (p2) return `(${p1}) ${p2}`;
                    if (p1) return `(${p1}`;
                    return '';
                });
            }
            e.target.value = value;
        });
    });

    // CPF/CNPJ formatting
    const documentInputs = document.querySelectorAll('input[name*="cpf"], input[name*="cnpj"], input[name*="cpf_cnpj"]');
    documentInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                // CPF formatting
                value = value.replace(/(\d{3})(\d{0,3})(\d{0,3})(\d{0,2})/, function(match, p1, p2, p3, p4) {
                    if (p4) return `${p1}.${p2}.${p3}-${p4}`;
                    if (p3) return `${p1}.${p2}.${p3}`;
                    if (p2) return `${p1}.${p2}`;
                    return p1;
                });
            } else {
                // CNPJ formatting
                value = value.substring(0, 14);
                value = value.replace(/(\d{2})(\d{0,3})(\d{0,3})(\d{0,4})(\d{0,2})/, function(match, p1, p2, p3, p4, p5) {
                    if (p5) return `${p1}.${p2}.${p3}/${p4}-${p5}`;
                    if (p4) return `${p1}.${p2}.${p3}/${p4}`;
                    if (p3) return `${p1}.${p2}.${p3}`;
                    if (p2) return `${p1}.${p2}`;
                    return p1;
                });
            }
            e.target.value = value;
        });
    });

    // Search functionality enhancement
    const searchInputs = document.querySelectorAll('input[type="search"], input[name*="search"]');
    searchInputs.forEach(input => {
        let timeout;
        input.addEventListener('input', function(e) {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Add loading state
                input.classList.add('loading');
                // Remove loading state after 500ms (simulate search)
                setTimeout(() => {
                    input.classList.remove('loading');
                }, 500);
            }, 300);
        });
    });

    // Table row click handlers
    const tableRows = document.querySelectorAll('tbody tr[data-href]');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            if (!e.target.closest('button') && !e.target.closest('form')) {
                window.location.href = this.dataset.href;
            }
        });
    });

    // Confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Tem certeza?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                // Save to localStorage
                const formData = new FormData(form);
                const data = Object.fromEntries(formData);
                localStorage.setItem(`form_${form.id}`, JSON.stringify(data));
                
                // Show save indicator
                showSaveIndicator();
            });
        });

        // Restore form data on load
        const savedData = localStorage.getItem(`form_${form.id}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name*="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Ctrl/Cmd + S for save (prevent default browser save)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const submitButton = document.querySelector('button[type="submit"]:not([disabled])');
            if (submitButton) {
                submitButton.click();
            }
        }

        // Alt + N for new item
        if (e.altKey && e.key === 'n') {
            e.preventDefault();
            const newButton = document.querySelector('[data-bs-toggle="modal"], .btn-primary[href*="new"]');
            if (newButton) {
                newButton.click();
            }
        }
    });

    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6c757d';
    }

    // WebSocket connection for real-time updates (if implemented)
    if (typeof io !== 'undefined') {
        const socket = io();
        
        socket.on('notification', function(data) {
            showNotification(data.message, data.type);
        });

        socket.on('kanban_update', function(data) {
            // Update kanban board without full refresh
            updateKanbanCard(data);
        });
    }

    // Service Worker registration for PWA capabilities
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered:', registration);
            })
            .catch(error => {
                console.log('SW registration failed:', error);
            });
    }
});

// Utility functions
function showSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'alert alert-success position-fixed';
    indicator.style.cssText = 'top: 20px; right: 20px; z-index: 9999; padding: 0.5rem 1rem;';
    indicator.innerHTML = '<i class="fas fa-check"></i> Salvo automaticamente';
    
    document.body.appendChild(indicator);
    
    setTimeout(() => {
        indicator.remove();
    }, 2000);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function updateKanbanCard(data) {
    // Implementation for real-time kanban updates
    const card = document.querySelector(`[data-card-id="${data.card_id}"]`);
    if (card) {
        const targetColumn = document.getElementById(data.new_column);
        if (targetColumn) {
            targetColumn.appendChild(card);
        }
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other scripts
window.MonteiroApp = {
    showNotification,
    showSaveIndicator,
    updateKanbanCard,
    formatCurrency,
    formatDate,
    debounce
};
