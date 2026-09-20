function checkNewLocation() {
    fetch('/api/get_latest_gps')
        .then(response => response.json())
        .then(data => {
            if (data.latitude && data.longitude) {
                marker.setLatLng([data.latitude, data.longitude]);
                map.setView([data.latitude, data.longitude]);
                var latElem = document.getElementById('lat-display');
                var lngElem = document.getElementById('lng-display');
                if (latElem) latElem.innerText = data.latitude;
                if (lngElem) lngElem.innerText = data.longitude;
                var gmapsLink = document.getElementById('gmaps-link');
                if (gmapsLink) {
                    gmapsLink.href = `https://www.google.com/maps?q=${data.latitude},${data.longitude}`;
                }
            }
        })
        .catch(error => console.error('Error fetching GPS data:', error));
}

setInterval(checkNewLocation, 5000);

// SOS Trigger logic for login.html
function sendSOS() {
    var statusText = document.getElementById('sos-status-text');
    var sosBtn = document.getElementById('sos-trigger-btn');

    if (sosBtn) sosBtn.disabled = true;
    if (statusText) {
        statusText.style.color = '#f59e0b';
        statusText.innerText = 'Sending Emergency Alert...';
    }

    fetch('/api/trigger_sos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (statusText) {
            statusText.style.color = '#22c55e';
            statusText.innerText = '🚨 SOS DISPATCHED SUCCESSFULLY!';
        }
    })
    .catch(error => {
        if (statusText) {
            statusText.style.color = '#ef4444';
            statusText.innerText = 'Failed to dispatch SOS alert.';
        }
    })
    .finally(() => {
        setTimeout(() => {
            if (sosBtn) sosBtn.disabled = false;
        }, 5000);
    });
}