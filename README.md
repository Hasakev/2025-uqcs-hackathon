# Grade Gambit 

![Grade Gambit Logo](Gemini_Generated_Image_v91kdqv91kdqv91k.png)

## Goals

- **Bets to Promote Grade Success**: Only allows users to bet on the positive side of their own grades. This is to ensure only positive pressure to study.
- **No Fights**: The system automates payouts and grade checking to stop any arguments around payment or validity of results. To further this goal we hold funds for non-monetary payouts as a packup in case a party pulls-out.
- **For Laughs not Dollars**: We aim to include or add as many alternative betting types as possible to add to the keep the fun of a challenge amounts mates alive.

## Features

- **Verified Grade Results**: Using custom blackboard integration to verify results
- **Public + Private Betting**: Supports both open market bets, as well as specific bet offers to friends
- **Course Grade Checking**: Automatically finds and extracts courses grades to see updates live
- **Multiple Betting Types**: Supports betting of both monetary and non-monetary amounts (slaps, text custom text to a friends ex)




# Installation

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for backend dependency management.
- [Node.js](https://nodejs.org/en/download/) (which includes npm) for frontend dependency management.
- A modern web browser like Chrome or Firefox.

## Instructions

First, clone the repository to your local machine.

### Backend (Poetry)

1.  Navigate to the backend directory (assuming it's named `backend`):
    ```bash
    cd path/to/project/backend
    ```

2.  Install the required Python packages using Poetry:
    ```bash
    poetry install
    ```

3.  Run the backend server. You may need to set up a `.env` file for environment variables first.
    ```bash
    poetry run flask --app app run --debug
    ```
    *(Note: This command might differ based on your project's entry point, e.g., `poetry run uvicorn...`)*

### Frontend (npm)

1.  In a **new terminal**, navigate to the frontend directory (assuming it's named `frontend`):
    ```bash
    cd path/to/project/frontend
    ```

2.  Install the required node modules:
    ```bash
    npm install
    ```

3.  Start the frontend development server:
    ```bash
    npm start
    ```
    The application should now be accessible in your browser, typically at `http://localhost:3000`.

## License

This project is provided as-is for educational purposes. Please ensure compliance with your institution's terms of service and applicable laws.

## Disclaimer

This tool is not affiliated with Blackboard Inc. or any educational institution. Use at your own risk and ensure compliance with all applicable terms of service and laws.