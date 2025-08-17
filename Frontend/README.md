# Blackboard Betting Platform - Frontend

This is the frontend for the Blackboard Betting Platform, a web application that allows users to track academic progress and place friendly bets with their mates.

## Features

- User authentication (Sign Up, Login)
- Dashboard to view and manage bets
- Create new bets
- View bet history (in progress)
- Responsive UI built with React and Tailwind CSS
- Popup monitoring and webview popup components

## Project Structure

```
Frontend/
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── public/
│   └── index.html
└── src/
    ├── App.js
    ├── index.css
    ├── index.js
    ├── components/
    │   ├── config.js
    │   ├── Navigation.js
    │   ├── PopupMonitor.js
    │   └── WebviewPopup.js
    └── pages/
        ├── BetHistory.js
        ├── CreateBet.js
        ├── Dashboard.js
        ├── Home.js
        ├── Login.js
        └── SignUp.js
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v16 or higher recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)

### Installation

1. Navigate to the `Frontend` directory:

   ```sh
   cd Frontend
   ```

2. Install dependencies:

   ```sh
   npm install
   ```

### Running the Development Server

```sh
npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000).

### Building for Production

```sh
npm run build
```

## Configuration

- **Tailwind CSS:** See [`tailwind.config.js`](tailwind.config.js) and [`postcss.config.js`](postcss.config.js).
- **Environment Variables:** If needed, create a `.env` file in the root of the `Frontend` directory.

## Scripts

- `npm start` — Start the development server
- `npm run build` — Build the app for production
- `npm test` — Run tests

## License

This project is for educational and demonstration purposes.

---

*We are not responsible for the bets you make*