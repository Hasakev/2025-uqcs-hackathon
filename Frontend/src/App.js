import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import CreateBet from './pages/CreateBet';
import BetHistory from './pages/BetHistory';
import Home from './pages/Home';
import SignUp from './pages/SignUp';
import Login from './pages/Login';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Only show Navigation on pages other than Home */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/login" element={<Login />} />w
          <Route path="/dashboard" element={
            <>
              <Navigation />
              <main className="container mx-auto px-4 py-8">
                <Dashboard />
              </main>
            </>
          } />
          <Route path="/create-bet" element={
            <>
              <Navigation />
              <main className="container mx-auto px-4 py-8">
                <CreateBet />
              </main>
            </>
          } />
          <Route path="/history" element={
            <>
              <Navigation />
              <main className="container mx-auto px-4 py-8">
                <BetHistory />
              </main>
            </>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
