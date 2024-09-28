const baseFixturesURL = "https://api.sofascore.com/api/v1/sport/football/scheduled-events/";
const baseOddsURL = "https://www.sofascore.com/api/v1/sport/football/odds/1/";

async function fetchData() {
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0]; // Format as YYYY-MM-DD

    const fixturesURL = `${baseFixturesURL}${formattedDate}`;
    const oddsURL = `${baseOddsURL}${formattedDate}`;

    try {
        const fixturesResponse = await fetch(fixturesURL);
        const oddsResponse = await fetch(oddsURL);
        
        const fixturesData = await fixturesResponse.json();
        const oddsData = await oddsResponse.json();

        const oddsMapping = {};
        for (let matchId in oddsData.odds) {
            oddsMapping[matchId] = oddsData.odds[matchId];
        }

        displayFixtures(fixturesData.events, oddsMapping);
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function fractionalToDecimal(fractional) {
    const [numerator, denominator] = fractional.split('/').map(Number);
    return (numerator / denominator + 1).toFixed(2);
}

function displayFixtures(events, oddsMapping) {
    const fixtureList = document.getElementById("fixture-list");
    fixtureList.innerHTML = ''; // Clear existing content

    const homeGames = [];
    const awayGames = [];

    events.forEach(event => {
        const odds = oddsMapping[event.id];
        if (odds) {
            let oddsDropped = false;

            odds.choices.forEach(choice => {
                if (choice.change < 0) { // Check if odds have dropped
                    oddsDropped = true;
                }
            });

            if (oddsDropped) {
                if (event.homeTeam.name) {
                    homeGames.push(event);
                } else {
                    awayGames.push(event);
                }
            }
        }
    });

    // Initialize display for home and away games
    displayFilteredGames(homeGames, "home");
    displayFilteredGames(awayGames, "away");
}

function displayFilteredGames(games, type) {
    const fixtureList = document.getElementById("fixture-list");
    games.forEach(event => {
        const fixtureItem = document.createElement("div");
        fixtureItem.classList.add("fixture-item");

        let oddsDisplay = '';
        const odds = oddsMapping[event.id];

        if (odds) {
            odds.choices.forEach(choice => {
                const decimalOdds = fractionalToDecimal(choice.fractionalValue);
                const changeIndicator = choice.change < 0 ? 
                    `<span class="odds-indicator" style="background-image: url(down.svg);">${decimalOdds}</span>` :
                    `<span class="odds-indicator" style="background-image: url(up.svg);">${decimalOdds}</span>`;

                oddsDisplay += `<div class="odds-choice">${choice.name}: ${changeIndicator}</div>`;
            });
        }

        fixtureItem.innerHTML = `
            <div class="fixture-header">
                <strong>${event.homeTeam.name} vs ${event.awayTeam.name}</strong>
                <span class="fixture-status">${event.status.description}</span>
            </div>
            <div class="fixture-details">
                <span>Tournament: ${event.tournament.name}</span><br>
                <span>Score: ${event.homeScore.current} - ${event.awayScore.current}</span>
            </div>
            <div class="fixture-odds"><strong>Odds:</strong>${oddsDisplay}</div>
        `;
        
        fixtureList.appendChild(fixtureItem);
    });
}

// Tab navigation functionality
document.getElementById("home-games").addEventListener("click", () => {
    filterGames("home");
});
document.getElementById("away-games").addEventListener("click", () => {
    filterGames("away");
});

function filterGames(type) {
    const fixtureItems = document.querySelectorAll(".fixture-item");
    fixtureItems.forEach(item => {
        const isHome = item.querySelector(".fixture-header strong").textContent.includes("vs"); // Simplistic check
        if ((type === "home" && isHome) || (type === "away" && !isHome)) {
            item.style.display = "block";
        } else {
            item.style.display = "none";
        }
    });
}

// Initiate data fetching
fetchData();
