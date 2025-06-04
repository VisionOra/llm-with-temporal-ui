// Application state
const AppState = {
    isLoading: false,
    temporalHealthy: false,
    llmHealthy: false
};

// DOM elements
const elements = {
    inputText: document.getElementById('inputText'),
    charCount: document.getElementById('charCount'),
    reverseBtn: document.getElementById('reverseBtn'),
    summarizeBtn: document.getElementById('summarizeBtn'),
    rephraseBtn: document.getElementById('rephraseBtn'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    
    // Result elements
    originalText: document.getElementById('originalText'),
    reversedText: document.getElementById('reversedText'),
    workflowId: document.getElementById('workflowId'),
    processingTime: document.getElementById('processingTime'),
    llmOperationLabel: document.getElementById('llmOperationLabel'),
    llmOutput: document.getElementById('llmOutput'),
    
    // Status elements
    temporalStatus: document.getElementById('temporalStatus'),
    llmStatus: document.getElementById('llmStatus'),
    statusMessages: document.getElementById('statusMessages'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    
    // Result cards
    temporalResult: document.getElementById('temporalResult'),
    llmResult: document.getElementById('llmResult')
};

// API configuration
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkSystemHealth();
    updateCharCount();
});

// Event listeners setup
function initializeEventListeners() {
    // Input text events
    elements.inputText.addEventListener('input', updateCharCount);
    elements.inputText.addEventListener('keydown', handleKeydown);
    
    // Button events
    elements.reverseBtn.addEventListener('click', handleReverseString);
    elements.summarizeBtn.addEventListener('click', () => handleLLMOperation('summarize'));
    elements.rephraseBtn.addEventListener('click', () => handleLLMOperation('rephrase'));
    elements.analyzeBtn.addEventListener('click', () => handleLLMOperation('analyze'));
}

// Handle keyboard shortcuts
function handleKeydown(event) {
    if (event.ctrlKey || event.metaKey) {
        switch(event.key) {
            case 'Enter':
                event.preventDefault();
                handleReverseString();
                break;
        }
    }
}

// Update character count
function updateCharCount() {
    const count = elements.inputText.value.length;
    elements.charCount.textContent = count;
    
    if (count > 9000) {
        elements.charCount.style.color = '#e53e3e';
    } else if (count > 7000) {
        elements.charCount.style.color = '#d69e2e';
    } else {
        elements.charCount.style.color = '#718096';
    }
}

// Show/hide loading overlay
function setLoading(isLoading, message = 'Processing...') {
    AppState.isLoading = isLoading;
    elements.loadingText.textContent = message;
    
    if (isLoading) {
        elements.loadingOverlay.classList.add('show');
        disableButtons(true);
    } else {
        elements.loadingOverlay.classList.remove('show');
        disableButtons(false);
    }
}

// Enable/disable buttons
function disableButtons(disabled) {
    elements.reverseBtn.disabled = disabled;
    elements.summarizeBtn.disabled = disabled;
    elements.rephraseBtn.disabled = disabled;
    elements.analyzeBtn.disabled = disabled;
}

// Show status message
function showStatusMessage(message, type = 'info', duration = 5000) {
    const messageElement = document.createElement('div');
    messageElement.className = `status-message ${type}`;
    messageElement.textContent = message;
    
    elements.statusMessages.appendChild(messageElement);
    
    // Auto-remove message after duration
    setTimeout(() => {
        if (messageElement.parentElement) {
            messageElement.remove();
        }
    }, duration);
}

// Check system health
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        updateSystemStatus(data);
        
        if (data.status === 'healthy') {
            showStatusMessage('All systems are healthy!', 'success');
        } else {
            showStatusMessage('Some services are unavailable', 'error');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateSystemStatus({ status: 'unhealthy', services: { temporal: 'unhealthy', llm: 'unhealthy' } });
        showStatusMessage('Failed to check system health', 'error');
    }
}

// Update system status indicators
function updateSystemStatus(data) {
    const temporalHealthy = data.services?.temporal === 'healthy';
    const llmHealthy = data.services?.llm === 'healthy';
    
    AppState.temporalHealthy = temporalHealthy;
    AppState.llmHealthy = llmHealthy;
    
    updateStatusIndicator(elements.temporalStatus, temporalHealthy ? 'healthy' : 'unhealthy');
    updateStatusIndicator(elements.llmStatus, llmHealthy ? 'healthy' : 'unhealthy');
}

// Update individual status indicator
function updateStatusIndicator(element, status) {
    element.className = `status-indicator ${status}`;
    
    const statusText = {
        healthy: 'Online',
        unhealthy: 'Offline',
        checking: 'Checking...'
    };
    
    element.innerHTML = `<i class="fas fa-circle"></i> ${statusText[status]}`;
}

// Validate input text
function validateInput() {
    const text = elements.inputText.value.trim();
    
    if (!text) {
        showStatusMessage('Please enter some text', 'error');
        elements.inputText.focus();
        return false;
    }
    
    if (text.length > 10000) {
        showStatusMessage('Text is too long (maximum 10,000 characters)', 'error');
        return false;
    }
    
    return true;
}

// Handle string reversal via Temporal workflow
async function handleReverseString() {
    if (!validateInput()) return;
    
    if (!AppState.temporalHealthy) {
        showStatusMessage('Temporal service is not available', 'error');
        return;
    }
    
    const text = elements.inputText.value.trim();
    
    try {
        setLoading(true, 'Executing Temporal workflow...');
        
        const response = await fetch(`${API_BASE}/reverse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayTemporalResult(data);
            showStatusMessage('String reversed successfully!', 'success');
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
    } catch (error) {
        console.error('Reverse string error:', error);
        showStatusMessage(`Error: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

// Handle LLM operations
async function handleLLMOperation(operation) {
    if (!validateInput()) return;
    
    if (!AppState.llmHealthy) {
        showStatusMessage('LLM service is not available', 'error');
        return;
    }
    
    const text = elements.inputText.value.trim();
    const operationNames = {
        summarize: 'Summarizing',
        rephrase: 'Rephrasing',
        analyze: 'Analyzing'
    };
    
    try {
        setLoading(true, `${operationNames[operation]} text...`);
        
        const response = await fetch(`${API_BASE}/llm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, operation })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayLLMResult(data, operation);
            showStatusMessage(`Text ${operation}d successfully!`, 'success');
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
    } catch (error) {
        console.error(`LLM ${operation} error:`, error);
        showStatusMessage(`Error: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

// Display Temporal workflow result
function displayTemporalResult(data) {
    elements.originalText.textContent = data.result || 'N/A';
    elements.reversedText.textContent = data.result || 'N/A';
    
    if (data.workflow_id) {
        elements.workflowId.textContent = `Workflow ID: ${data.workflow_id}`;
        elements.workflowId.style.display = 'inline-block';
    }
    
    if (data.processing_time_ms) {
        elements.processingTime.textContent = `Processing Time: ${data.processing_time_ms}ms`;
        elements.processingTime.style.display = 'inline-block';
    }
    
    // Show the result card with animation
    elements.temporalResult.classList.add('show');
    elements.temporalResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display LLM result
function displayLLMResult(data, operation) {
    const operationLabels = {
        summarize: 'Summary',
        rephrase: 'Rephrased Text',
        analyze: 'Analysis'
    };
    
    elements.llmOperationLabel.textContent = `${operationLabels[operation]}:`;
    elements.llmOutput.textContent = data.result || 'N/A';
    
    // Show the result card with animation
    elements.llmResult.classList.add('show');
    elements.llmResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Utility function to make API calls
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
}

// Periodic health check
setInterval(checkSystemHealth, 30000); // Check every 30 seconds

// Handle visibility change to refresh health when tab becomes active
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        checkSystemHealth();
    }
});

// Handle network connectivity
window.addEventListener('online', function() {
    showStatusMessage('Connection restored', 'success');
    checkSystemHealth();
});

window.addEventListener('offline', function() {
    showStatusMessage('Connection lost', 'error');
    updateSystemStatus({ status: 'unhealthy', services: { temporal: 'unhealthy', llm: 'unhealthy' } });
});

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AppState,
        handleReverseString,
        handleLLMOperation,
        validateInput,
        checkSystemHealth
    };
} 