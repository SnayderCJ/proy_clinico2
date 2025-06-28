document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages después de 5 segundos
    setTimeout(function() {
        const messages = document.querySelectorAll('[data-message-id]');
        messages.forEach(function(message) {
            closeMessage(message.dataset.messageId);
        });
    }, 5000);
});

function closeMessage(messageId) {
    const message = document.getElementById('message-' + messageId);
    if (message) {
        message.classList.add('animate-slide-out-up');
        
        // Remover del DOM después de la animación
        setTimeout(function() {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
            
            // Ocultar el contenedor si no hay más mensajes
            const container = document.getElementById('messagesContainer');
            if (container && container.children.length === 0) {
                container.classList.add('hidden');
            }
        }, 400);
    }
}

// Función para mostrar mensaje programáticamente
function showMessage(text, type = 'info') {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    const messageId = Date.now();
    const icons = {
        'success': 'check',
        'error': 'times', 
        'warning': 'exclamation',
        'info': 'info'
    };
    
    const typeClasses = {
        'success': 'bg-gradient-to-r from-green-50 to-emerald-100 border-l-emerald-500 text-emerald-800 dark:bg-gradient-to-r dark:from-emerald-900/30 dark:to-emerald-800/30 dark:text-emerald-300',
        'error': 'bg-gradient-to-r from-red-50 to-red-100 border-l-red-500 text-red-800 animate-shake dark:bg-gradient-to-r dark:from-red-900/30 dark:to-red-800/30 dark:text-red-300',
        'warning': 'bg-gradient-to-r from-yellow-50 to-amber-100 border-l-amber-500 text-amber-800 dark:bg-gradient-to-r dark:from-amber-900/30 dark:to-amber-800/30 dark:text-amber-300',
        'info': 'bg-gradient-to-r from-blue-50 to-blue-100 border-l-blue-500 text-blue-800 dark:bg-gradient-to-r dark:from-blue-900/30 dark:to-blue-800/30 dark:text-blue-300'
    };
    
    const iconColors = {
        'success': 'bg-emerald-500',
        'error': 'bg-red-500',
        'warning': 'bg-amber-500',
        'info': 'bg-blue-500'
    };
    
    const messageHtml = `
        <div id="message-${messageId}" 
             class="relative mb-4 p-4 rounded-xl shadow-2xl border-l-4 backdrop-blur-sm overflow-hidden animate-slide-in-down ${typeClasses[type] || typeClasses.info}"
             data-message-id="${messageId}">
            <div class="flex items-start justify-between">
                <div class="flex items-start gap-3 flex-1">
                    <div class="flex-shrink-0 pt-0.5">
                        <div class="w-6 h-6 ${iconColors[type] || iconColors.info} rounded-full flex items-center justify-center text-white text-xs">
                            <i class="fa-solid fa-${icons[type] || 'info'}"></i>
                        </div>
                    </div>
                    <div class="flex-1">
                        <p class="m-0 font-semibold text-sm leading-relaxed">${text}</p>
                    </div>
                </div>
                <button onclick="closeMessage(${messageId})" 
                        class="flex-shrink-0 ml-4 p-1 border-none bg-transparent rounded-full cursor-pointer opacity-60 hover:opacity-100 hover:bg-black/10 dark:hover:bg-white/10 transition-all duration-200 text-current">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>
            <div class="absolute bottom-0 left-0 h-1 bg-current opacity-20 rounded-bl-xl animate-progress-bar"></div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    container.classList.remove('hidden');
    
    // Auto-hide después de 5 segundos
    setTimeout(() => closeMessage(messageId), 5000);
}