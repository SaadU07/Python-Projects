An interactive Python adventure game that combines core programming concepts with real-time API data to create a unique gameplay experience. Built as a culminating computer science project, it demonstrates practical use of functions, conditionals, randomness, external APIs, error handling, and UI design.

Features

Live Weather Integration:
Uses the Open-Meteo API to fetch current weather data. Weather influences the narrative, scene descriptions, and difficulty.

Random Monster Generation:
Retrieves creature names from the Creaturator API. Falls back to internal defaults if the API fails.

Complete Error Handling:

Safe failures when API requests break or return unexpected data

Default behavior for missing weather codes

Default names when monster data is malformed

Graceful UI fallback

Interactive UI:
Custom-designed UI layout supporting buttons, scene transitions, and text display.

Replayability:
Each game run creates different encounters depending on weather and monster data.

How It Works
Weather System

A function requests NYC’s current weather from Open-Meteo.
If the API succeeds, conditions like high wind or rain alter the bridge and cave scenes.
If the API fails or the data is missing, the game defaults to atmospheric fallback descriptions.

Monster Generation

A function fetches a random monster name from Creaturator.
If the name cannot be retrieved, the game uses “nameless horror” as a safe fallback.

Game Flow

Player begins at the main scene.

Game fetches weather and monster data.

Environment and threats update based on live conditions.

Player navigates through decisions affecting outcomes.

Game ends with either a success or failure scene.

Technologies Used

Python

Requests (or equivalent HTTP method depending on your setup)

Custom-built UI framework (buttons, scenes, transitions)

Open-Meteo API

Creaturator API
