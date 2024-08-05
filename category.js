const baseURL = 'https://api.sofascore.com/api/v1';

const fetchJson = async (url) => {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Error ${response.status}: ${errorData.message}`);
        }
        return response.json();
    } catch (error) {
        console.error('Fetch error:', error.message);
        return null;
    }
};

const displayCategoryEvents = async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tournamentId = urlParams.get('tournamentId');
    const scheduledEventsUrl = `https://api.sofascore.com/api/v1/sport/football/scheduled-events/2024-08-05`;

    const scheduledEventsData = await fetchJson(scheduledEventsUrl);

    if (scheduledEventsData) {
        const events = scheduledEventsData.events;
        const filteredEvents = events.filter(event => event.tournament.id === parseInt(tournamentId));
        
        const container = document.getElementById('events-container');
        container.innerHTML = '';

        // Group events by tournament
        if (filteredEvents.length > 0) {
            const tournamentSection = document.createElement('div');
            tournamentSection.classList.add('event');
            const tournamentHeader = document.createElement('h2');
            tournamentHeader.textContent = `Tournament Events`;
            tournamentSection.appendChild(tournamentHeader);

            const eventsList = document.createElement('ul');
            filteredEvents.forEach(event => {
                const listItem = document.createElement('li');
                const eventLink = document.createElement('a');
                eventLink.href = `event.html?eventId=${event.id}`;
                eventLink.textContent = `${event.homeTeam.name} vs ${event.awayTeam.name}`;
                listItem.appendChild(eventLink);
                eventsList.appendChild(listItem);
            });
            tournamentSection.appendChild(eventsList);
            container.appendChild(tournamentSection);
        }
    }
};

// Run the initialization function
displayCategoryEvents();
