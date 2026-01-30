// Load activities when page loads
document.addEventListener('DOMContentLoaded', function () {
  loadActivities();
  setupSignupForm();
});

async function loadActivities() {
  try {
    const response = await fetch('/activities');
    const activities = await response.json();

    displayActivities(activities);
    populateActivityDropdown(activities);
  } catch (error) {
    console.error('Error loading activities:', error);
    document.getElementById('activities-list').innerHTML =
      '<p class="error">Failed to load activities. Please try again later.</p>';
  }
}

function displayActivities(activities) {
  const container = document.getElementById('activities-list');
  container.innerHTML = '';

  for (const [name, details] of Object.entries(activities)) {
    const card = document.createElement('div');
    card.className = 'activity-card';

    const participantsList = details.participants.length > 0
      ? `<div class="participants-list">
                ${details.participants.map(email => `
                  <div class="participant-item">
                    <span class="participant-email">${email}</span>
                    <button class="delete-icon" data-activity="${name}" data-email="${email}" title="Unregister">❌</button>
                  </div>
                `).join('')}
               </div>`
      : '<p class="no-participants">No participants yet</p>';

    card.innerHTML = `
            <h4>${name}</h4>
            <p><strong>Description:</strong> ${details.description}</p>
            <p><strong>Schedule:</strong> ${details.schedule}</p>
            <p><strong>Capacity:</strong> ${details.participants.length}/${details.max_participants}</p>
            <div class="participants-section">
                <p><strong>Current Participants:</strong></p>
                ${participantsList}
            </div>
        `;

    container.appendChild(card);
  }

  // Add event listeners to delete buttons
  document.querySelectorAll('.delete-icon').forEach(button => {
    button.addEventListener('click', handleUnregister);
  });
}

function populateActivityDropdown(activities) {
  const select = document.getElementById('activity');

  for (const name of Object.keys(activities)) {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  }
}

async function handleUnregister(event) {
  const button = event.target;
  const activity = button.dataset.activity;
  const email = button.dataset.email;

  if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
    return;
  }

  try {
    const response = await fetch(`/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`, {
      method: 'DELETE'
    });

    if (response.ok) {
      const result = await response.json();
      showMessage(result.message, 'success');
      // Reload activities to show updated participant list
      loadActivities();
    } else {
      const error = await response.json();
      showMessage(error.detail, 'error');
    }
  } catch (error) {
    console.error('Error unregistering:', error);
    showMessage('Failed to unregister. Please try again.', 'error');
  }
}

function setupSignupForm() {
  const form = document.getElementById('signup-form');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const activity = document.getElementById('activity').value;

    if (!email || !activity) {
      showMessage('Please fill in all fields', 'error');
      return;
    }

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        showMessage(result.message, 'success');
        form.reset();
        // Reload activities to show updated participant list
        loadActivities();
      } else {
        const error = await response.json();
        showMessage(error.detail, 'error');
      }
    } catch (error) {
      console.error('Error signing up:', error);
      showMessage('Failed to sign up. Please try again.', 'error');
    }
  });
}

function showMessage(text, type) {
  const messageDiv = document.getElementById('message');
  messageDiv.textContent = text;
  messageDiv.className = `message ${type}`;
  messageDiv.classList.remove('hidden');

  setTimeout(() => {
    messageDiv.classList.add('hidden');
  }, 5000);
}
