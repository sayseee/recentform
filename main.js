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
        const topTournaments = topTournamentsData.uniqueTournaments;
        const events = scheduledEventsData.events;
        const filteredEvents = filterEventsByTime(events, 24);

        // Create a list of categories with scheduled events
        const container = document.getElementById('categories-container');
        container.innerHTML = '';

        // Display top tournament categories first
        topTournaments.forEach(tournament => {
            const categoryName = tournament.category.name;
            const categoryEvents = filteredEvents.filter(event => event.tournament.id === tournament.id);

            if (categoryEvents.length > 0) {
                const categoryItem = document.createElement('div');
                categoryItem.classList.add('category');
                
                const categoryLink = document.createElement('a');
                categoryLink.href = `category.html?categoryName=${encodeURIComponent(categoryName)}`;
                categoryLink.textContent = categoryName; // Use category name for the link text
                categoryItem.appendChild(categoryLink);
                
                container.appendChild(categoryItem);
            }
        });

        // Then, display other categories
        const otherCategories = new Map();
        filteredEvents.forEach(event => {
            const categoryName = event.tournament.category.name;
            if (!topTournaments.some(tournament => tournament.id === event.tournament.id)) {
                if (!otherCategories.has(categoryName)) {
                    otherCategories.set(categoryName, []);
                }
                otherCategories.get(categoryName).push(event);
            }
        });

        otherCategories.forEach((events, categoryName) => {
            const categoryItem = document.createElement('div');
            categoryItem.classList.add('category');
            
            const categoryLink = document.createElement('a');
            categoryLink.href = `category.html?categoryName=${encodeURIComponent(categoryName)}`;
            categoryLink.textContent = categoryName; // Use category name for the link text
            categoryItem.appendChild(categoryLink);
            
            container.appendChild(categoryItem);
        });
    }
};