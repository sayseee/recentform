// app.js

// Team IDs for comparison
const team1Id = 1963; // Example ID for team 1 (Palmeiras)
const team2Id = 1979; // Example ID for team 2 (Botafogo-SP)

// API URLs
const team1EventsUrl = `https://api.sofascore.com/api/v1/team/${team1Id}/events/last/0`;
const team2EventsUrl = `https://api.sofascore.com/api/v1/team/${team2Id}/events/last/0`;

// Helper function to convert fractional odds to decimal
function fractionalToDecimal(fractionalOdds) {
    const [numerator, denominator] = fractionalOdds.split('/');
    return (parseInt(numerator) / parseInt(denominator) + 1).toFixed(2);
}

// Fetch and display team events
function fetchTeamEvents() {
    Promise.all([
        fetch(team1EventsUrl).then(response => response.json()),
        fetch(team2EventsUrl).then(response => response.json())
    ])
    .then(([team1Data, team2Data]) => {
        const events1 = team1Data.events || [];
        const events2 = team2Data.events || [];
        const eventsContainer = document.getElementById('events-container');

        // Ensure both teams have the same number of events
        const maxEvents = Math.min(events1.length, events2.length);

        for (let i = 0; i < maxEvents; i++) {
            const event1 = events1[i];
            const event2 = events2[i];

            const eventElement = document.createElement('div');
            eventElement.className = 'event-container';

            const homeTeamEvent = createEventElement(event1, team1Id);
            const awayTeamEvent = createEventElement(event2, team2Id);

            eventElement.innerHTML = `
                <div class="team-event">${homeTeamEvent}</div>
                <div class="team-event">${awayTeamEvent}</div>
            `;

            eventsContainer.appendChild(eventElement);
        }
    })
    .catch(error => {
        console.error('Error fetching events:', error);
        document.getElementById('events-container').innerHTML = '<p>Error loading events.</p>';
    });
}

// Create event HTML structure
function createEventElement(event, teamId) {
    const eventId = event.id; // Save event ID for fetching odds

    return `
        <h2>${event.tournament.name} - ${event.season.name} (${event.roundInfo.name})</h2>
        <div class="teams">
            <strong>${event.homeTeam.name}</strong> vs <strong>${event.awayTeam.name}</strong>
        </div>
        <div class="score">
            ${event.homeScore.current} - ${event.awayScore.current}
        </div>
        <div class="status">
            Status: ${event.status.description}
        </div>
        <div class="odds" id="odds-${eventId}">
            <!-- Odds will be inserted here -->
        </div>
        <script>
            fetchOdds(${eventId});
        </script>
    `;
}

// Fetch and display odds
function fetchOdds(eventId) {
    fetch(`https://www.sofascore.com/api/v1/event/${eventId}/odds/1/all`)
        .then(response => response.json())
        .then(data => {
            const oddsContainer = document.getElementById(`odds-${eventId}`);
            const markets = data.markets || [];

            markets.forEach(market => {
                if (market.marketName === "Full time") {
                    const marketElement = document.createElement('div');
                    marketElement.className = 'market';
                    marketElement.innerHTML = `<strong>${market.marketName}</strong>`;

                    market.choices.forEach(choice => {
                        marketElement.innerHTML += `<div>${choice.name}: ${fractionalToDecimal(choice.fractionalValue)} ${choice.winning ? '(Winning)' : ''}</div>`;
                    });

                    oddsContainer.appendChild(marketElement);
                }
            });
        })
        .catch(error => {
            console.error('Error fetching odds:', error);
            const oddsContainer = document.getElementById(`odds-${eventId}`);
            oddsContainer.innerHTML = '<p>Error loading odds.</p>';
        });
}

// Initialize data fetching
fetchTeamEvents();
