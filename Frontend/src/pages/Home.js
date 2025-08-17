import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { base_url } from '../components/config';

const Home = () => {
  const navigate = useNavigate();

  // Write a landing page
  return (
    <>
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-4">Academic Comeback</h1>
      <p className="text-lg mb-8">Track your academic progress, with repercussions among your mates*...</p>
      <Link to="/signup" className="bg-blue-500 text-white px-4 py-2 rounded">
        Get Started
      </Link>
    </div>

    <div className="absolute bottom-0 left-0 p-4">
      <p className="text-sm text-gray-500">*We are not responsible for the bets you make 😶‍🌫️</p>
    </div>
</>
  );
};

export default Home;