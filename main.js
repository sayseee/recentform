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

const filterEventsByTime = (events, hours) => {
    const now = new Date().getTime();
    const timeRange = hours * 60 * 60 * 1000; // Convert hours to milliseconds

    return events.filter(event => {
        const eventTime = new Date(event.startTimestamp * 1000).getTime();
        return eventTime >= now && eventTime <= now + timeRange;
    });
};

const displayCategories = async () => {
    const topTournamentsUrl = `${baseURL}/config/top-unique-tournaments/UG/football`;
    const scheduledEventsUrl = `${baseURL}/sport/football/scheduled-events/2024-08-05`;

    const topTournamentsData = await fetchJson(topTournamentsUrl);
    const scheduledEventsData = await fetchJson(scheduledEventsUrl);

    if (topTournamentsData && scheduledEventsData) {
        const uniqueTournaments = topTournamentsData.uniqueTournaments;
        const events = scheduledEventsData.events;

        const status = 'live'; // Example status, can be 'live', 'finished', 'scheduled', or null
        const filteredEvents = filterEventsByTime(events, 24);

        // Create a list of categories with scheduled events
        const container = document.getElementById('categories-container');
        container.innerHTML = '';

        uniqueTournaments.forEach(tournament => {
            const tournamentEvents = filteredEvents.filter(event => event.tournament.id === tournament.id);

            if (tournamentEvents.length > 0) {
                const categoryItem = document.createElement('div');
                categoryItem.classList.add('category');
                
                const categoryLink = document.createElement('a');
                categoryLink.href = `category.html?tournamentId=${tournament.id}`;
                categoryLink.textContent = tournament.name;
                categoryItem.appendChild(categoryLink);
                
                container.appendChild(categoryItem);
            }
        });
    }
};

// Run the initialization function
displayCategories();
