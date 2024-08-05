const baseURL = 'https://api.sofascore.com/api/v1';

const loadCategoryTournaments = async () => {
    const categoryName = decodeURIComponent(getUrlParameter('categoryName'));
    const categoryId = getUrlParameter('categoryId');

    const uniqueTournamentsUrl = `${baseURL}/category/${categoryId}/unique-tournaments`;
    const scheduledEventsUrl = `${baseURL}/sport/football/scheduled-events/2024-08-05`;

    const uniqueTournamentsData = await fetchJson(uniqueTournamentsUrl);
    const scheduledEventsData = await fetchJson(scheduledEventsUrl);

    if (uniqueTournamentsData && scheduledEventsData) {
        const uniqueTournaments = uniqueTournamentsData.groups[0].uniqueTournaments;
        const events = scheduledEventsData.events;
        const filteredEvents = filterEventsByTime(events, 24);

        const container = document.getElementById('tournaments-container');

        uniqueTournaments.forEach(tournament => {
            const tournamentItem = document.createElement('div');
            tournamentItem.classList.add('tournament');

            const tournamentLink = document.createElement('a');
            tournamentLink.href = `tournament.html?tournamentId=${tournament.id}&tournamentName=${encodeURIComponent(tournament.name)}`;
            tournamentLink.textContent = tournament.name;
            tournamentItem.appendChild(tournamentLink);

            const categoryEvents = filteredEvents.filter(event => event.tournament.id === tournament.id);

            if (categoryEvents.length > 0) {
                // Group events by unique tournament ID
                const tournamentEvents = categoryEvents.reduce((acc, event) => {
                    if (!acc[event.tournament.name]) {
                        acc[event.tournament.name] = [];
                    }
                    acc[event.tournament.name].push(event);
                    return acc;
                }, {});

                // Display tournament events
                Object.keys(tournamentEvents).forEach(tournamentName => {
                    const tournamentEventsList = document.createElement('ul');
                    tournamentEventsList.classList.add('tournament-events');

                    tournamentEvents[tournamentName].forEach(event => {
                        const eventItem = document.createElement('li');
                        const eventLink = document.createElement('a');
                        eventLink.href = `event.html?eventId=${event.id}`;
                        eventLink.textContent = `${event.homeTeam.name} vs ${event.awayTeam.name}`;
                        eventItem.appendChild(eventLink);
                        tournamentEventsList.appendChild(eventItem);
                    });

                    tournamentItem.appendChild(tournamentEventsList);
                });
            }

            container.appendChild(tournamentItem);
        });
    }
};

const getUrlParameter = (name) => {
    const url = window.location.href;
    const paramRegex = new RegExp(`[?&]${name}=([^&#]*)`);
    const match = url.match(paramRegex);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
};

loadCategoryTournaments();