(function() {
    // CSRF Token utility for AJAX POSTs
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Get CSRF Token from cookie or from DOM middleware token input
    const csrftoken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    let pollIntervalId = null;
    let isTransitional = false;

    // Fetch current VM status from the API
    async function fetchVMStatus() {
        try {
            const response = await fetch('/api/vm/status');
            const data = await response.json();
            
            if (data.success) {
                updateVMUI(data.status, data.vm_name, data.resource_group);
                hideError();
                
                // Adjust polling speed dynamically based on state
                const transitionalStates = ['Starting', 'Stopping', 'Restarting'];
                if (transitionalStates.includes(data.status)) {
                    if (!isTransitional) {
                        isTransitional = true;
                        startPolling(3000); // Poll fast (every 3 seconds) during transitions
                    }
                } else {
                    if (isTransitional) {
                        isTransitional = false;
                        startPolling(15000); // Fallback to slow (15 seconds) for stable states
                    }
                }
            } else {
                showError(data.error || 'Failed to retrieve VM status.');
                updateVMUI('Unknown');
            }
        } catch (err) {
            showError('Network error while fetching VM status.');
            updateVMUI('Unknown');
        }
    }

    // Synchronize unreachable connection warning alert with VM state
    function syncConnectionAlert(vmStatus) {
        const alertCards = document.querySelectorAll('.alert-card');
        alertCards.forEach(card => {
            if (card.textContent.includes('Connection warning') || card.textContent.includes('telemetry')) {
                // If VM is not running, server unreachable is normal and expected
                if (vmStatus !== 'Running') {
                    card.style.display = 'none';
                } else {
                    card.style.display = 'flex';
                }
            }
        });
    }

    // Update the VM UI display elements and enable/disable control buttons
    function updateVMUI(status, vmName = null, resourceGroup = null) {
        const badge = document.getElementById('vm-status-badge');
        const text = document.getElementById('vm-status-text');
        const btnStart = document.getElementById('btn-start');
        const btnRestart = document.getElementById('btn-restart');
        const btnStop = document.getElementById('btn-stop');
        // const btnDeallocate = document.getElementById('btn-deallocate');
        const resourceInfo = document.getElementById('vm-resource-info');

        if (vmName && resourceGroup && resourceInfo) {
            resourceInfo.textContent = `${vmName} (${resourceGroup})`;
        }

        if (!badge || !text) return;

        // Reset class list
        badge.className = 'vm-badge';
        
        switch (status) {
            case 'Running':
                badge.classList.add('vm-badge-running');
                text.innerHTML = '🟢 Running';
                if (btnStart) btnStart.disabled = true;
                if (btnRestart) btnRestart.disabled = false;
                if (btnStop) btnStop.disabled = false;
                break;
            case 'Starting':
                badge.classList.add('vm-badge-starting');
                text.innerHTML = '<span class="badge-spinner"></span> 🟡 Starting';
                if (btnStart) btnStart.disabled = true;
                if (btnRestart) btnRestart.disabled = true;
                if (btnStop) btnStop.disabled = true;
                break;
            case 'Stopping':
                badge.classList.add('vm-badge-stopping');
                text.innerHTML = '<span class="badge-spinner"></span> 🟠 Stopping';
                if (btnStart) btnStart.disabled = true;
                if (btnRestart) btnRestart.disabled = true;
                if (btnStop) btnStop.disabled = true;
                break;
            case 'Stopped':
                badge.classList.add('vm-badge-stopped');
                text.innerHTML = '🔴 Stopped (deallocated)';
                if (btnStart) btnStart.disabled = false;
                if (btnRestart) btnRestart.disabled = true;
                if (btnStop) btnStop.disabled = true;
                break;
            case 'Deallocated':
                badge.classList.add('vm-badge-stopped');
                text.innerHTML = '🔴 Stopped (deallocated)';
                if (btnStart) btnStart.disabled = false;
                if (btnRestart) btnRestart.disabled = true;
                if (btnStop) btnStop.disabled = true;
                break;
            case 'Restarting':
                badge.classList.add('vm-badge-restarting');
                text.innerHTML = '<span class="badge-spinner"></span> 🔵 Restarting';
                if (btnStart) btnStart.disabled = true;
                if (btnRestart) btnRestart.disabled = true;
                if (btnStop) btnStop.disabled = true;
                break;
            default:
                badge.classList.add('vm-badge-deallocated');
                text.innerHTML = '⚪ Unknown';
                if (btnStart) btnStart.disabled = true;
                if (btnRestart) btnRestart.disabled = true;
                if (btnStop) btnStop.disabled = true;
                break;
        }

        // Run alert synchronization
        syncConnectionAlert(status);
    }

    // Perform Azure VM Action
    async function handleVMAction(action) {
        const loader = document.getElementById('vm-loader');
        const loaderText = document.getElementById('vm-loader-text');
        
        if (!loader || !loaderText) return;

        const actionLabel = action.charAt(0).toUpperCase() + action.slice(1);
        loaderText.textContent = `${actionLabel === 'Deallocate' ? 'Deallocating' : actionLabel === 'Stop' ? 'Stopping' : actionLabel === 'Start' ? 'Starting' : 'Restarting'} VM...`;
        
        // Show loader overlay briefly during API call initiation
        loader.style.display = 'flex';
        hideError();
        
        // Proactively update UI state and trigger fast polling
        if (action === 'restart') {
            updateVMUI('Restarting');
        } else if (action === 'start') {
            updateVMUI('Starting');
        } else if (action === 'stop') {
            updateVMUI('Stopping');
        } else if (action === 'deallocate') {
            updateVMUI('Stopping');
        }

        try {
            const response = await fetch(`/api/vm/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            });
            const data = await response.json();
            
            if (data.success) {
                // Instantly query status and shift to 3-second rapid polling
                isTransitional = true;
                startPolling(3000);
                await fetchVMStatus();
            } else {
                showError(data.error || `Failed to ${action} VM.`);
                await fetchVMStatus();
            }
        } catch (err) {
            showError(`Network error while trying to ${action} VM.`);
            await fetchVMStatus();
        } finally {
            loader.style.display = 'none';
        }
    }

    function startPolling(ms) {
        if (pollIntervalId) {
            clearInterval(pollIntervalId);
        }
        pollIntervalId = setInterval(fetchVMStatus, ms);
    }

    function showError(message) {
        const banner = document.getElementById('vm-error-banner');
        if (banner) {
            banner.textContent = message;
            banner.style.display = 'block';
        }
    }

    function hideError() {
        const banner = document.getElementById('vm-error-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }

    // Expose handleVMAction globally since it is used in HTML onclick attributes
    window.handleVMAction = handleVMAction;

    // Initialize and poll status
    document.addEventListener('DOMContentLoaded', () => {
        fetchVMStatus();
        startPolling(15000); // Start standard 15s status poll
        
        // Set dynamic widths for metric card bars (avoids template syntax inline style validation warnings)
        document.querySelectorAll('.card-bar[data-width]').forEach(bar => {
            const width = bar.getAttribute('data-width');
            if (width && !isNaN(width)) {
                bar.style.width = width + '%';
            }
        });
    });
})();
