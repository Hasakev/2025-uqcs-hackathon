import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import CreateBet from './pages/CreateBet';
import BetHistory from './pages/BetHistory';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create-bet" element={<CreateBet />} />
            <Route path="/history" element={<BetHistory />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
