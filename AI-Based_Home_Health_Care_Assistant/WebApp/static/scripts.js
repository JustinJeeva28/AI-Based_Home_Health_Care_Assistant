document.getElementById('sendMessage').addEventListener('click', async () => {
    const message = document.getElementById('userMessage').value;
    const responseDiv = document.getElementById('chatResponse');

    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    });

    const data = await response.json();
    responseDiv.innerText = data.reply;
});

document.getElementById('reminderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const task = document.getElementById('task').value;
    const time = document.getElementById('time').value;
    const duration = document.getElementById('duration').value;
    const mode = document.getElementById('mode').value;
    const statusDiv = document.getElementById('reminderStatus');

    const response = await fetch('/api/reminder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task, time, duration, mode }),
    });

    const data = await response.json();
    statusDiv.innerText = data.status;
});

document.getElementById('loadReports').addEventListener('click', async () => {
    const response = await fetch('/api/reports');
    const reports = await response.json();
    const reportsList = document.getElementById('reportsList');
    
    // reportsList.innerHTML = reports.map(report => `<div>${report[2]}</div>`).join('');
    // reportsList.innerHTML = reports.map(report => `<tr><td>${report}</td></tr>`);
    // reportsList.innerHTML = reports.map(report => `<tr><td>${report[0]}</td><td>${report[1]}</td></tr>`).join('');
    reportsList.innerHTML = reports.map(report => `<div>${JSON.stringify(report)}</div>`).join('');
});

document.getElementById('loadVitals').addEventListener('click', async () => {
    const response = await fetch('/api/vitals');
    const vitals = await response.json();
    const vitalsList = document.getElementById('vitalsList');
    vitalsList.innerHTML = vitals.map(vital => `<div>${JSON.stringify(vital)}</div>`).join('');
});