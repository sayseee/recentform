<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soccer Analysis System</title>
    <script src="https://cdn.jsdelivr.net/npm/luxon@2.0.2/build/global/luxon.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script> <!-- Add this line -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
      <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }

        .container {  
            padding: 20px;  
        }

        h1 {
            text-align: center;
        }

        #odds-container {
            margin-bottom: 20px;
        }

        canvas {
            width: 100%;
            height: 400px;
        }
        /* Categories container */
main {
    height: calc(100vh - 76px); /* Fill the viewport height minus 76px */  
    display: flex;
    position: relative;
}
/* Categories container */
.categories {
    width: 22%; /* Fill the viewport height minus 76px */
    overflow-y: auto; /* Enable vertical scrolling */
    padding: 5px; /* Optional padding */ 
    border-right: var(--color-support-3) 1px solid;
    padding-top: 20px; 
}
    </style>
</head>
<body>
    <header id="superheader">
    <div class="logo">Football Analyzer</div>
    <div class="filter-bar">
        <div>
            From:                     
            <input type="date" id="start-date" name="start-date">
             To:<input type="date" id="end-date" name="end-date"> 
        </div>
        <div>
            <select id="time-range">
                <option value="">Select Time</option>
                <option value="3">3 Hours</option>
                <option value="6">6 Hours</option>
                <option value="12">12 Hours</option>
            </select>
            <button id="filter-btn">Filter</button>
        </div> 
    </div>
</header>
<main>
    <div id="categories-container" class="categories"></div>
    <div class="container">
        <h1>Soccer Odds Analysis</h1>
        <div id="odds-container"></div>
        <div id="oddsChart"></div> 
        <div id="loader" style="display: none;">Loading...</div>
<div id="event-details-div"></div> 
    <div id="stats"></div>
    </div>
</main>
    <script>
        const baseURL = 'https://api.sofascore.com/api/v1';
        
        document.addEventListener('DOMContentLoaded', () => {
                const today = new Date().toISOString().split('T')[0];
                document.getElementById('start-date').value = today;
                document.getElementById('end-date').value = today;

                // Initial data load
                displayCategories(today, today, '');

                document.getElementById('filter-btn').addEventListener('click', () => {
                    const startDate = document.getElementById('start-date').value;
                    const endDate = document.getElementById('end-date').value;
                    const hours = document.getElementById('time-range').value;
                    displayCategories(startDate, endDate, hours);
                });

                document.querySelectorAll('.main-nav a').forEach(link => {
                    link.addEventListener('click', async event => {
                        event.preventDefault();
                        const filterType = link.getAttribute('href').replace('#', '');

                        let startDate = today;
                        let endDate = today;
                        let hours = '';

                        switch (filterType) {
                            case 'all-games':
                                displayCategories(startDate, endDate, hours);
                                break;
                            case 'live-games':
                                displayCategories(startDate, endDate, hours, 'live');
                                break;
                            case 'finished-games':
                                displayCategories(startDate, endDate, hours, 'finished');
                                break;
                            case 'scheduled-games':
                                displayCategories(startDate, endDate, hours, 'scheduled');
                                break;
                            default:
                                displayCategories(startDate, endDate, hours);
                                break;
                        }

                        // Remove 'active' class from all links
                        document.querySelectorAll('.main-nav a').forEach(link => {
                            link.classList.remove('active');
                        });

                        // Add 'active' class to the clicked link
                        event.target.classList.add('active');
                    });
                });

                

            });


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
        

    async function fetchAndCheck(endpoint) {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`Failed to fetch: ${response.status}`);
        return response.json();
    }

    async function fetchTeamIdsByEvent(eventId) {
        const response = await fetch(`https://api.sofascore.com/api/v1/event/${eventId}`);
        if (!response.ok) throw new Error(`Failed to fetch team IDs for event ${eventId}`);
        const data = await response.json(); 
        
        return {
            homeTeamId: data.event.homeTeam.id,
            awayTeamId: data.event.awayTeam.id
        };
    }


    async function fetchTeamNames(teamIds) {
        const teamNames = {};
        
        const nameFetchPromises = Object.keys(teamIds).map(async (teamType) => {
            const response = await fetch(`https://api.sofascore.com/api/v1/team/${teamIds[teamType]}`);
            if (!response.ok) throw new Error(`Failed to fetch team name for ID ${teamIds[teamType]}`);
            const data = await response.json();
            teamNames[teamType] = data.team.name; // Assuming the team name is in this path
        });

        await Promise.all(nameFetchPromises);
        return teamNames;
    }


    /**
 * Fetches and displays team details.
 * 
 * @param {Object} teamIds - Object containing home and away team IDs.
 * @param {HTMLElement} container - Container element to display team details.
 */
 const fetchAndDisplayDetails = async (teamIds, container) => {
    if (!teamIds || !teamIds.home || !teamIds.away) {
        console.error('Invalid team IDs:', teamIds);
        return; // Exit function if team IDs are invalid
    }

    try {
        // Fetch team events
        const eventsResponse = await fetchJson(`https://api.sofascore.com/api/v1/events/${teamIds.home}`);
        if (!eventsResponse) {
            container.innerHTML = '<p>No event data available.</p>';
            return;
        }

        // Process team stats
        const teamStats = processTeamStats(eventsResponse);
        const last3GamesStatsHome = processLast3GamesStats(eventsResponse, true);
        const last3GamesStatsAway = processLast3GamesStats(eventsResponse, false);
        const correctScoresHome = calculateCorrectScores(eventsResponse, true);
        const correctScoresAway = calculateCorrectScores(eventsResponse, false);

        // Display stats for home team
        await displayStats(teamStats, last3GamesStatsHome, correctScoresHome, 'Home Team Name', container, true);

        // Display stats for away team
        await displayStats(teamStats, last3GamesStatsAway, correctScoresAway, 'Away Team Name', container, false);
    } catch (error) {
        console.error('Error fetching team details:', error);
        container.innerHTML = '<p>Error loading team details. Please try again later.</p>';
    }
}

async function displayEventDetails(selectedEvent) {
    const eventId = selectedEvent.event.id;
    console.log(eventId);
    const eventDetailsDiv = document.getElementById('event-details-div');
    if (!eventDetailsDiv) {
        console.error('Event details div not found!');
        return;
    }
    
    eventDetailsDiv.innerHTML = ''; // Clear previous details

    try {
        const teamIds = { home: selectedEvent.homeTeam.id, away: selectedEvent.awayTeam.id }; 
        await init(eventId);
    } catch (error) {
        console.error('Error loading event details:', error);
        eventDetailsDiv.innerHTML = '<p>Error loading event details. Please try again later.</p>';
    }
}
 


function displayStats(teamStats, last3GamesStats, correctScores, teamName, container, isHomeTeam) {
    const {
        gamesPlayed, totalGoalsScored, totalGoalsConceded, wins, draws, losses, 
        over1_5, over2_5, over3_5, under2_5, btts, drawsHalfTime, cleanSheets, 
        scoredBothHalves, bttsWin, bttsOver2_5, totalFirstHalfGoals, totalSecondHalfGoals,
        totalFirstHalfConceded, totalSecondHalfConceded, winAndOver2_5
    } = teamStats;

    const { gamesScoredIn, goalsScored, over2_5: last3GamesOver2_5, lastMatchTotalGoals,
            firstHalfGoals, secondHalfGoals } = last3GamesStats; 

    const averageScored = totalGoalsScored / gamesPlayed;
    const averageConceded = totalGoalsConceded / gamesPlayed;
    const points = (wins * 3 + draws);
    const pointsPerGame = points / gamesPlayed;
    const averageScoredFirstHalf = totalFirstHalfGoals / gamesPlayed;
    const averageScoredSecondHalf = totalSecondHalfGoals / gamesPlayed;
    const averageScoredFirstHalfConceded = totalFirstHalfConceded / gamesPlayed;
    const averageScoredSecondHalfConceded = totalSecondHalfConceded / gamesPlayed;
    const safeTeamName = teamName.replace(/\s+/g, '-').toLowerCase(); // Replaces spaces with dashes and converts to lowercase

    const teamStatsDiv = document.createElement('div');
    teamStatsDiv.classList.add('team-stats');
    teamStatsDiv.innerHTML = `
        <h2>${teamName}</h2>
        <p>Games Played: ${gamesPlayed}</p>
        <p>Points: ${points}</p>
        <p>Points per Game: ${pointsPerGame.toFixed(2)}</p>
        <p>Average Goals Scored: ${averageScored.toFixed(2)}</p>
        <p>Average Goals Conceded: ${averageConceded.toFixed(2)}</p>
        <p>Wins: ${wins}</p>
        <p>Draws: ${draws}</p>
        <p>Losses: ${losses}</p>
        <p>Over 1.5 Goals: ${over1_5}</p>
        <p>Over 2.5 Goals: ${over2_5}</p>
        <p>Over 3.5 Goals: ${over3_5}</p>
        <p>Under 2.5 Goals: ${under2_5}</p>
        <p>Clean Sheets: ${cleanSheets}</p>
        <p>Win & Over 2.5 Goals: ${winAndOver2_5}</p> <!-- New stat displayed -->
        <p>BTTS: ${btts}</p>
        <p>BTTS & Win: ${bttsWin}</p>
        <p>BTTS & Over 2.5 Goals: ${bttsOver2_5}</p>
        <p>Draws Half-Time: ${drawsHalfTime}</p>
        <p>Scored Both Halves: ${scoredBothHalves}</p>
        <p>First Half Goals Scored: ${averageScoredFirstHalf.toFixed(2)}</p>
        <p>First Half Goals Conceded: ${averageScoredFirstHalfConceded.toFixed(2)}</p>
        <p>Second Half Goals: ${averageScoredSecondHalf.toFixed(2)}</p>
        <p>Second Half Goals Conceded: ${averageScoredSecondHalfConceded.toFixed(2)}</p>

        <h3>Last 3 ${isHomeTeam ? 'Home' : 'Away'} Games</h3>
        <p>Games Scored In: ${gamesScoredIn}</p>
        <p>Goals Scored: ${goalsScored}</p>
        <p>First Half Goals Scored: ${firstHalfGoals}</p>
        <p>Second Half Goals Scored: ${secondHalfGoals}</p>
        <p>Over 2.5 Goals in Last 3 Games: ${last3GamesOver2_5}</p>
        <p>Total Goals in Last Match: ${lastMatchTotalGoals}</p>
        <h3>Correct Scores</h3>
        <ul id="${safeTeamName}-correct-scores"></ul>
 <!-- Placeholder for correct scores -->
    `;

    const correctScoresList = teamStatsDiv.querySelector(`#${safeTeamName}-correct-scores`);
if (correctScoresList) {
    Object.entries(correctScores).forEach(([scoreline, count]) => {
        const li = document.createElement('li');
        li.textContent = `${scoreline} - ${count}`;
        correctScoresList.appendChild(li);
    });
} else {
    console.error(`Could not find correct scores list for team: ${teamName}`);
}

    container.appendChild(teamStatsDiv);
}

fetchAndDisplayDetails();


async function fetchOdds(eventId) {
            try {
                const response = await fetch(`https://www.sofascore.com/api/v1/event/${eventId}/odds/1/changes`);
                const data = await response.json();
                return data.changedOdds;
            } catch (error) {
                console.error('Error fetching odds:', error);
            }
        }

        function displayOdds(odds) {
            const container = document.getElementById('odds-container');
            container.innerHTML = '';

            odds.forEach(entry => {
                const timestamp = new Date(entry.timestamp * 1000).toLocaleString();
                const oddsInfo = `
                    <div>
                        <strong>${timestamp}</strong>: 
                        1: ${fractionalToDecimal(entry.choice1.fractionalValue)}, 
                        X: ${fractionalToDecimal(entry.choice2.fractionalValue)}, 
                        2: ${fractionalToDecimal(entry.choice3.fractionalValue)}
                    </div>
                `;
                container.innerHTML += oddsInfo;
            });
        }

        function renderChart(odds) {
            const timestamps = '.';
            const choice1 = odds.map(entry => fractionalToDecimal(entry.choice1.fractionalValue));
            const choice2 = odds.map(entry => fractionalToDecimal(entry.choice2.fractionalValue));
            const choice3 = odds.map(entry => fractionalToDecimal(entry.choice3.fractionalValue));

            const options = {
                chart: {
                    type: 'line',
                    toolbar: { show: false }, // Hide the toolbar
                },
                series: [
                    { name: 'Home', data: choice1 },
                    { name: 'Draw', data: choice2 },
                    { name: 'Away', data: choice3 }
                ],
                xaxis: {
                    categories: timestamps,
                    labels: { show: true }, // Show x-axis labels
                },
                legend: {
                    show: true, // Show the legend
                    position: 'top',
                },
                stroke: {
                    width: 2 // Set the thickness of the lines (default is 2)
                },
                dataLabels: { enabled: false }, // Remove data labels
                tooltip: {
                    enabled: false, // Disable tooltips
                },
            };

            const chart = new ApexCharts(document.querySelector("#oddsChart"), options);
            chart.render();
        }


        async function init(eventId) {
            const odds = await fetchOdds(eventId);
            if (odds) {
                displayOdds(odds);
                renderChart(odds);
            }
        }
 
    
        function processTeamStats(events) {
    let totalGoalsScored = 0, totalGoalsConceded = 0, wins = 0, draws = 0, losses = 0;
    let over1_5 = 0, over2_5 = 0, over3_5 = 0, under2_5 = 0, btts = 0;
    let drawsHalfTime = 0, cleanSheets = 0, scoredBothHalves = 0, bttsWin = 0, bttsOver2_5 = 0;
    let totalFirstHalfGoals = 0, totalSecondHalfGoals = 0;
    let totalFirstHalfConceded = 0, totalSecondHalfConceded = 0;
    let winAndOver2_5 = 0; // New variable for "Win & Over 2.5"

    const gamesPlayed = events.length;

    events.forEach(event => {
        const { homeScore, awayScore } = event;
        const isHomeTeam = event.homeTeam.id === teamIds.home; 
        const totalScore = homeScore.current + awayScore.current;

        totalGoalsScored += isHomeTeam ? homeScore.current : awayScore.current;
        totalGoalsConceded += isHomeTeam ? awayScore.current : homeScore.current;

        // First and Second Half Goals
        totalFirstHalfGoals += isHomeTeam ? (homeScore.period1 || 0) : (awayScore.period1 || 0);
        totalFirstHalfConceded += isHomeTeam ? (awayScore.period1 || 0) : (homeScore.period1 || 0);
        totalSecondHalfGoals += isHomeTeam ? (homeScore.period2 || 0) : (awayScore.period2 || 0);
        totalSecondHalfConceded += isHomeTeam ? (awayScore.period2 || 0) : (homeScore.period2 || 0);

        // Win/Draw/Loss Logic
        const teamWon = (isHomeTeam && homeScore.current > awayScore.current) || 
                        (!isHomeTeam && awayScore.current > homeScore.current);
        if (teamWon) {
            wins++;
            if (totalScore > 2.5) winAndOver2_5++; // Track "Win & Over 2.5"
        } else if (homeScore.current === awayScore.current) {
            draws++;
        } else {
            losses++;
        }

        // Over/Under, BTTS, Half-time, Clean Sheets, etc.
        if (totalScore > 1.5) over1_5++;
        if (totalScore > 2.5) over2_5++;
        if (totalScore > 3.5) over3_5++;
        if (totalScore < 2.5) under2_5++; 
        if (homeScore.period1 === awayScore.period1) drawsHalfTime++;
        if ((isHomeTeam && awayScore.current === 0) || (!isHomeTeam && homeScore.current === 0)) cleanSheets++;
        if ((isHomeTeam && homeScore.period1 > 0 && homeScore.period2 > 0) || 
            (!isHomeTeam && awayScore.period1 > 0 && awayScore.period2 > 0)) scoredBothHalves++;
        if (homeScore.current > 0 && awayScore.current > 0) { 
            btts++; 
            if (teamWon) {
                bttsWin++; 
            }
            if (totalScore > 2.5) {
                bttsOver2_5++; 
            }
        }
    });

    return {
        gamesPlayed, totalGoalsScored, totalGoalsConceded, wins, draws, losses,
        over1_5, over2_5, over3_5, under2_5, btts, drawsHalfTime, cleanSheets,
        scoredBothHalves, bttsWin, bttsOver2_5, totalFirstHalfGoals, totalSecondHalfGoals,
        totalFirstHalfConceded, totalSecondHalfConceded, winAndOver2_5 // Return the new stat
    };
}

function calculateCorrectScores(events, isHomeTeam) {
    const scoreCounts = {};

    events.forEach(event => {
        const { homeScore, awayScore } = event;

        // Ensure valid scores
        if (!homeScore || !awayScore || homeScore.normaltime == null || awayScore.normaltime == null) {
            return;
        }

        const homeGoals = homeScore.normaltime || 0;
        const awayGoals = awayScore.normaltime || 0;

        const scoreline = `${homeGoals}:${awayGoals}`;

        if (!scoreCounts[scoreline]) {
            scoreCounts[scoreline] = 0;
        }

        scoreCounts[scoreline]++;
    });

    return scoreCounts;
}



function processLast3GamesStats(events, isHomeTeam) {
    const filteredEvents = events.filter(event => 
        isHomeTeam ? event.homeScore.current != null : event.awayScore.current != null
    );

    const last3Games = filteredEvents.slice(-3).reverse();

    let gamesScoredIn = 0, goalsScored = 0, over2_5 = 0, lastMatchTotalGoals = 0;
    let firstHalfGoals = 0, secondHalfGoals = 0;

    last3Games.forEach((event, i) => {
        const { homeScore, awayScore } = event;
        const totalScore = homeScore.current + awayScore.current;

        const teamGoals = isHomeTeam ? homeScore.current : awayScore.current;
        if (teamGoals > 0) gamesScoredIn++;
        goalsScored += teamGoals;

        // First Half and Second Half Goals
        firstHalfGoals += isHomeTeam ? (homeScore.period1 || 0) : (awayScore.period1 || 0);
        secondHalfGoals += isHomeTeam ? (homeScore.period2 || 0) : (awayScore.period2 || 0);

        if (totalScore > 2.5) over2_5++;

        if (i === 0) lastMatchTotalGoals = totalScore;
    });

    return {
        gamesScoredIn,
        goalsScored,
        over2_5,
        lastMatchTotalGoals,
        firstHalfGoals,
        secondHalfGoals
    };
}    

const filterEventsByTime = (events, hours) => {
            const now = new Date().getTime();
            const timeRange = hours * 60 * 60 * 1000; // Convert hours to milliseconds
        
            return events.filter(event => {
                const eventTime = new Date(event.startTimestamp * 1000).getTime();
                return eventTime >= now && eventTime <= now + timeRange;
            });
        };
        
        const displayCategories = async (startDate, endDate, hours, status) => {
            const topTournamentsUrl = `${baseURL}/config/top-unique-tournaments/UG/football`;
            const scheduledEventsUrl = `${baseURL}/sport/football/scheduled-events/${startDate}`;
            const scheduledEventsUrl2 = `${baseURL}/sport/football/scheduled-events/${startDate}/inverse`;
            const oddsResponse = `${baseURL}/sport/football/odds/1/${startDate}`;

            let filteredEvents = [];
            let odds = {};

            const fetchData = async () => {
                try {
                    const topTournamentsData = await fetchJson(topTournamentsUrl);
                    const scheduledEventsData = await fetchJson(scheduledEventsUrl);
                    const scheduledEventsData2 = await fetchJson(scheduledEventsUrl2);
                    const oddsData = await fetchJson(oddsResponse);

                    const events = [...scheduledEventsData.events, ...scheduledEventsData2.events];
                    odds = oddsData?.odds || {};

                    // Filter events
                    filteredEvents = events.filter(event => {
                        const eventDate = new Date(event.startTimestamp * 1000).toISOString().split('T')[0];
                        return eventDate >= startDate && eventDate <= endDate;
                    });

                    if (hours) {
                        filteredEvents = filterEventsByTime(filteredEvents, hours);
                    }

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

                    filteredEvents = filteredEvents.filter(event => odds[event.id]);

                    const topTournaments = topTournamentsData.uniqueTournaments;
                    const topTournamentIds = topTournaments.map(tournament => tournament.id);

                    const container = document.getElementById('categories-container');
                    container.innerHTML = '';

                    const topTournamentsMap = new Map();
                    const otherCategoriesMap = new Map();

                    filteredEvents.forEach(event => {
                        const homeTeamId = event.homeTeam.id;
                        const awayTeamId = event.awayTeam.id;
                        const categoryName = event.tournament.category.name;
                        const tournamentId = event.tournament.uniqueTournament.id;
                        const tournamentName = event.tournament.name;

                        const targetMap = topTournamentIds.includes(tournamentId) ? topTournamentsMap : otherCategoriesMap;

                        if (!targetMap.has(categoryName)) {
                            targetMap.set(categoryName, new Map());
                        }

                        const tournaments = targetMap.get(categoryName);
                        if (!tournaments.has(tournamentName)) {
                            tournaments.set(tournamentName, {
                                id: tournamentId,
                                events: []
                            });
                        }

                        tournaments.get(tournamentName).events.push(event);
                    });

                    const createCategorySection = (tournaments, categoryName) => {
                        const categoryItem = document.createElement('div');
                        categoryItem.classList.add('category');

                        const categoryHeader = document.createElement('div');
                        categoryHeader.classList.add('category-header', 'flex', 'gT10', '_F_ac');
                        const categoryImage = tournaments.values().next().value.events[0].tournament.category.alpha2
                            ? tournaments.values().next().value.events[0].tournament.category.alpha2.toLowerCase()
                            : tournaments.values().next().value.events[0].tournament.category.flag;
                        categoryHeader.innerHTML = ` 
                            <img src="https://www.sofascore.com/static/images/flags/${categoryImage}.png" width="20" height="20" loading="lazy" />
                            <span><span class="cat-name">${categoryName}</span></span> 
                        `;
                        categoryHeader.addEventListener('click', () => {
                            categoryItem.classList.toggle('active');
                            const tournamentsContainer = categoryItem.querySelector('.tournaments-container');
                            tournamentsContainer.style.display = categoryItem.classList.contains('active') ? 'block' : 'none';
                        });

                        const tournamentsContainer = document.createElement('div');
                        tournamentsContainer.classList.add('tournaments-container');

                        tournaments.forEach((tournament, tournamentName) => {
                            const tournamentSection = document.createElement('div');
                            tournamentSection.classList.add('tournament');

                            const tournamentHeader = document.createElement('h3');
                            tournamentHeader.classList.add('flex', '_F_ac');
                            const tournamentImage = `${baseURL}/unique-tournament/${tournament.id}/image`;
                            tournamentHeader.innerHTML = `
                                <img class="tourn" src="${tournamentImage}" alt="${tournamentName}" width="16" height="16" loading="lazy" />
                                ${tournamentName}
                            `;
                            tournamentSection.appendChild(tournamentHeader);

                            const eventsList = document.createElement('ul');
                            tournament.events.forEach(event => {
                                const listItem = document.createElement('li');
                                const eventLink = document.createElement('a');
                                eventLink.className = 'match-card';
                                eventLink.dataset.eventId = event.id;

                                // Get odds data
                                const oddsData = odds[event.id] || {};
                                const homeFractional = oddsData.choices?.find(choice => choice.name === '1')?.initialFractionalValue;
                                const drawFractional = oddsData.choices?.find(choice => choice.name === 'X')?.initialFractionalValue;
                                const awayFractional = oddsData.choices?.find(choice => choice.name === '2')?.initialFractionalValue;

                                const homeOdds = homeFractional ? fractionalToDecimal(homeFractional) : '-';
                                const drawOdds = drawFractional ? fractionalToDecimal(drawFractional) : '-';
                                const awayOdds = awayFractional ? fractionalToDecimal(awayFractional) : '-';

                                const homeScore = event.homeScore?.current ?? 0;
                                const awayScore = event.awayScore?.current ?? 0;

                                const isHomeTeamWinner = homeScore > awayScore;
                                const isAwayTeamWinner = awayScore > homeScore;

                                const homeTeamName = isHomeTeamWinner ? `<strong>${event.homeTeam.shortName}</strong>` : event.homeTeam.shortName;
                                const awayTeamName = isAwayTeamWinner ? `<strong>${event.awayTeam.shortName}</strong>` : event.awayTeam.shortName;

                                eventLink.innerHTML = `
                                    <div class="match-time-status">
                                        <span class="match-time">${new Date(event.startTimestamp * 1000).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }).replace(',', ' ').replace('/', ' ')}</span>
                                        <span class="match-status">${new Date(event.startTimestamp * 1000).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                    <div class="team-info">
                                        <div class="teams-info">
                                            <div class="team">
                                                <img src="${baseURL}/team/${event.homeTeam.id}/image" width="16" height="16" alt="${event.homeTeam.shortName}" loading="lazy" class="team-logo">
                                                <span class="team-name">${homeTeamName}</span>
                                            </div>
                                            <div class="team">
                                                <img src="${baseURL}/team/${event.awayTeam.id}/image" width="16" height="16" alt="${event.awayTeam.shortName}" loading="lazy" class="team-logo">
                                                <span class="team-name">${awayTeamName}</span>
                                            </div>
                                        </div>
                                        <div class="match-odds">
                                            <div class="odd-choice">
                                                <span class="odds">1</span>
                                                <span class="odds">${homeOdds}</span>
                                            </div>
                                            <div class="odd-choice">
                                                <span class="odds">X</span>
                                                <span class="odds">${drawOdds}</span>
                                            </div>
                                            <div class="odd-choice">
                                                <span class="odds">2</span>
                                                <span class="odds">${awayOdds}</span>
                                            </div>
                                        </div>
                                        <div class="match-score" id="${event.status.type}">
                                            <span class="score" id="homeScore-${event.id}">${event.homeScore?.current ?? ''}</span>
                                            <span class="score" id="awayScore-${event.id}">${event.awayScore?.current ?? ''}</span>
                                        </div>
                                    </div> 
                                `; 
                                listItem.appendChild(eventLink);
                                eventsList.appendChild(listItem);
                            });

                            tournamentSection.appendChild(eventsList);
                            tournamentsContainer.appendChild(tournamentSection);
                        });

                        categoryItem.appendChild(categoryHeader);
                        categoryItem.appendChild(tournamentsContainer);
                        return categoryItem;
                    };

                    topTournamentsMap.forEach((tournaments, categoryName) => {
                        const categoryItem = createCategorySection(tournaments, categoryName);
                        container.appendChild(categoryItem);
                    });

                    otherCategoriesMap.forEach((tournaments, categoryName) => {
                        const categoryItem = createCategorySection(tournaments, categoryName);
                        container.appendChild(categoryItem);
                    });

                    if (filteredEvents.length > 0) {
                        displayEventDetails(filteredEvents[0].id);
                        init(filteredEvents[0].id);
                    }

                    document.querySelectorAll('.match-card').forEach(card => {
                        card.addEventListener('click', async (event) => {
                            const eventId = event.currentTarget.dataset.eventId;
                            const selectedEvent = filteredEvents.find(event => event.id === parseInt(eventId));
                            
                            if (selectedEvent) { // Check if event is found
                                await displayEventDetails(selectedEvent); // Pass the selectedEvent object
                                const teamIds = { home: selectedEvent.homeTeam.id, away: selectedEvent.awayTeam.id };
                                await fetchAndDisplayDetails(teamIds, document.getElementById('event-details-div'));
                            } else {
                                console.error('Event not found:', eventId);
                            }
                        });
                    });

                } catch (error) {
                    console.error('Error displaying categories:', error);
                }
            };
            await fetchData();
        }
        const fractionalToDecimal = (fractional) => {
            const [numerator, denominator] = fractional.split('/').map(Number);
            return (numerator / denominator + 1).toFixed(2);
        };

   

    </script>
</body>
</html>
 