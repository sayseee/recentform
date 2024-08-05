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

const displayEventDetails = async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const eventId = urlParams.get('eventId');
    const eventDetailsUrl = `https://api.sofascore.com/api/v1/event/${eventId}`;

    const eventDetailsData = await fetchJson(eventDetailsUrl);

    if (eventDetailsData) {
        const container = document.getElementById('event-details-container');
        container.innerHTML = '';

        const eventTitle = document.createElement('h1');
        eventTitle.textContent = `${eventDetailsData.homeTeam.name} vs ${eventDetailsData.awayTeam.name}`;
        container.appendChild(eventTitle);

        const eventInfo = document.createElement('p');
        eventInfo.textContent = `Start Time: ${new Date(eventDetailsData.startTimestamp * 1000).toLocaleString()}`;
        container.appendChild(eventInfo);

        const score = document.createElement('p');
        score.textContent = `Score: ${eventDetailsData.homeScore.current} - ${eventDetailsData.awayScore.current}`;
        container.appendChild(score);
        
        // Add more details as needed
    }
};

// Run the initialization function
displayEventDetails();
