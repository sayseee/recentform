const baseURL = 'https://api.sofascore.com/api/v1';

// Utility Functions
const fractionalToDecimal = (fractional) => {
    const [numerator, denominator] = fractional.split('/').map(Number);
    return ((numerator / denominator) + 1).toFixed(2);
};

// Filter events by time and status
const filterEventsByTimeAndStatus = (events, hours, status) => {
    const now = new Date().getTime();
    const timeRange = hours * 60 * 60 * 1000; // Convert hours to milliseconds

    // Filter events by time
    let filteredEvents = events.filter(event => {
        const eventTime = new Date(event.startTimestamp * 1000).getTime();
        return eventTime >= now && eventTime <= now + timeRange;
    });

    // Filter events by status
    if (status) {
        filteredEvents = filteredEvents.filter(event => {
            switch (status) {
                case 'live':
                    return event.status.type === 'inprogress';
                case 'finished':
                    return event.status.type === 'finished';
                case 'scheduled':
                    return event.status.type === 'notstarted';
                default:
                    return true;
            }
        });
    }

    return filteredEvents;
};

// Fetch JSON data from the provided URL
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

// Main function to fetch and display data
const init = async () => {
    const topTournamentsUrl = `${baseURL}/config/top-unique-tournaments/UG/football`;
    const scheduledEventsUrl = `${baseURL}/sport/football/scheduled-events/2024-08-05`;

    // Fetch data from the APIs
    const topTournamentsData = await fetchJson(topTournamentsUrl);
    const scheduledEventsData = await fetchJson(scheduledEventsUrl);

    if (topTournamentsData && scheduledEventsData) {
        // Extract unique tournaments and events
        const uniqueTournaments = topTournamentsData.uniqueTournaments;
        const events = scheduledEventsData.events;

        // Optionally filter events (e.g., within next 24 hours and based on status)
        const status = 'live'; // Example status, can be 'live', 'finished', 'scheduled', or null
        const filteredEvents = filterEventsByTimeAndStatus(events, 24, status);

        // Display data
        displayData(uniqueTournaments, filteredEvents);
    }
};

// Function to display tournaments and events
const displayData = (tournaments, events) => {
    const container = document.getElementById('events-container');
    container.innerHTML = '';

    // Create top tournaments section
    const tournamentsSection = document.createElement('div');
    tournamentsSection.classList.add('category');
    const tournamentsHeader = document.createElement('h2');
    tournamentsHeader.textContent = 'Top Tournaments';
    tournamentsSection.appendChild(tournamentsHeader);

    const tournamentsList = document.createElement('ul');
    tournaments.forEach(tournament => {
        const listItem = document.createElement('li');
        listItem.textContent = tournament.name;
        tournamentsList.appendChild(listItem);
    });
    tournamentsSection.appendChild(tournamentsList);
    container.appendChild(tournamentsSection);

    // Create scheduled events section
    const eventsSection = document.createElement('div');
    eventsSection.classList.add('category');
    const eventsHeader = document.createElement('h2');
    eventsHeader.textContent = 'Scheduled Events';
    eventsSection.appendChild(eventsHeader);

    const eventsList = document.createElement('ul');
    events.forEach(event => {
        const listItem = document.createElement('li');
        listItem.textContent = `${event.homeTeam.name} vs ${event.awayTeam.name} - ${event.homeScore.current} : ${event.awayScore.current}`;
        eventsList.appendChild(listItem);
    });
    eventsSection.appendChild(eventsList);
    container.appendChild(eventsSection);
};

// Run the initialization function
init();
