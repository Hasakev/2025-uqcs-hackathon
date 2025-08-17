import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, RefreshCw, TrendingUp, TrendingDown, DollarSign, Bell } from 'lucide-react';
import { base_url } from '../components/config';

const Dashboard = () => {
  //  Get username and email from localStorage
  const [userData, setUserData] = useState(null);
  
  //  Add state for API data
  const [userBets, setUserBets] = useState([]);
  const [openBets, setOpenBets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    const storedData = localStorage.getItem('userData');
    if (storedData) {
      const parsedData = JSON.parse(storedData);
      setUserData(parsedData);
      
      //  Fetch user's bets and open bets when component mounts
      if (parsedData.username) {
        fetchUserBets(0); // 0 = all bets
        fetchOpenBets(0);
      }
    }
  }, []);

  //  Fetch user's bets by status
  // NEW
  const fetchUserBets = async (betStatus = 0) => {
    if (!userData?.username) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${base_url}check_bets/${userData.username}/${betStatus}`);
      if (response.ok) {
        const data = await response.json();
        setUserBets(data);
        console.log('User bets fetched:', data);
      } else {
        console.error('Failed to fetch user bets');
      }
    } catch (error) {
      console.error('Error fetching user bets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchOpenBets = async (betStatus = 0) => {
    if (!userData?.username) return;
    try {
      const response = await fetch(`${base_url}check_open_bets/${userData.username}/0`);
      if (response.ok) {
        const data = await response.json();
        setOpenBets(data);
        console.log('Open bets fetched:', data);
      } else {
        console.error('Failed to fetch open bets');
      }
    } catch (error) {
      console.error('Error fetching open bets:', error);
    }
  };


  //  Accept a bet
  const acceptBet = async (betId) => {
    if (!userData?.username) {
      alert('Please login first');
      return;
    }

    try {
      const response = await fetch(`${base_url}/accept_open_bet/${userData.username}/${betId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        alert('Bet accepted successfully!');
        // Refresh the data
        fetchUserBets(userData.username, 0);
        fetchOpenBets(userData.username);
      } else {
        const errorData = await response.json();
        alert(errorData.error || 'Failed to accept bet');
      }
    } catch (error) {
      console.error('Error accepting bet:', error);
      alert('Failed to accept bet. Please try again.');
    }
  };

  //  Get bet status text
  const getBetStatusText = (status) => {
    console.log(status);
    return status;
  };

  //  Get bet status color
  const getBetStatusColor = (status) => {
    switch (status) {
      case "Pending": return 'bg-warning-100 text-warning-800 border-warning-200';
      case "Accepted": return 'bg-success-100 text-success-800 border-success-200';
      case "Rejected": return 'bg-danger-100 text-danger-800 border-danger-200';
      case "Completed": return 'bg-gray-100 text-gray-800 border-gray-200';
      // default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  //  Filter user bets by status
  const pendingBets = userBets.filter(bet => bet.status === "Pending").length;
  const acceptedBets = userBets.filter(bet => bet.status === "Accepted").length;

  return (
    <div className="space-y-6">
      {/* Page Header with User Info */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          {userData?.username && (
            <p className="text-sm text-gray-600">Welcome, {userData.username}!</p>
          )}
        </div>
        <button 
          onClick={() => {
            if (userData?.username) {
              fetchUserBets(userData.username, 0);
              fetchOpenBets(userData.username);
            }
          }}
          className="btn-primary flex items-center space-x-2"
          disabled={isLoading}
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {/* User Info Card */}
      {userData?.username && (
        <div className="card bg-blue-50 border-blue-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-semibold">
                {userData.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h3 className="font-medium text-blue-900">{userData.username}</h3>
              <p className="text-sm text-blue-700">{userData.email}</p>
            </div>
          </div>
        </div>
      )}

      {/* Account Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Account Balance</p>
              <p className="text-2xl font-bold text-gray-900">$1,250.75</p>
            </div>
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Bets</p>
              <p className="text-2xl font-bold text-warning-600">{pendingBets}</p>
            </div>
            <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
              <TrendingDown className="w-6 h-6 text-warning-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Accepted Bets</p>
              <p className="text-2xl font-bold text-gray-900">{acceptedBets}</p>
            </div>
            <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-warning-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            to="/create-bet"
            className="flex items-center justify-center p-6 border-2 border-dashed border-primary-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors duration-200 group"
          >
            <div className="text-center">
              <PlusCircle className="w-12 h-12 text-primary-400 group-hover:text-primary-500 mx-auto mb-3" />
              <p className="text-lg font-medium text-primary-600 group-hover:text-primary-700">Place New Bet</p>
              <p className="text-sm text-gray-500">Create a new bet on your grades</p>
            </div>
          </Link>

          <button 
            onClick={() => {
              if (userData?.username) {
                fetchUserBets(userData.username, 0);
                fetchOpenBets(userData.username);
              }
            }}
            className="flex items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-colors duration-200 group"
          >
            <div className="text-center">
              <RefreshCw className="w-12 h-12 text-gray-400 group-hover:text-gray-500 mx-auto mb-3" />
              <p className="text-lg font-medium text-gray-600 group-hover:text-gray-700">Refresh Data</p>
              <p className="text-sm text-gray-500">Update your latest bets and open bets</p>
            </div>
          </button>
        </div>
      </div>

      {/* My Bets Section */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">My Bets</h2>
          <div className="flex space-x-2">
            <button 
              onClick={() => fetchUserBets(0)}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              All
            </button>
            <button 
              onClick={() => fetchUserBets(1)}
              className="text-sm text-warning-600 hover:text-warning-700"
            >
              Pending
            </button>
            <button 
              onClick={() => fetchUserBets(2)}
              className="text-sm text-success-600 hover:text-success-700"
            >
              Accepted
            </button>
          </div>
        </div>
        
        {userBets.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No bets found.</p>
            <Link to="/create-bet" className="btn-primary mt-3 inline-block">
              Place Your First Bet
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {userBets.map((bet) => (
              <div key={bet.uuid} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{bet.coursecode}</h3>
                    <p className="text-sm text-gray-600">{bet.assessment}</p>
                    <div className="flex items-center space-x-4 mt-2 text-sm">
                      <span className="text-gray-600">Target: <span className="font-medium">Above {bet.lower}%</span></span>
                      <span className="text-gray-600">Wager: <span className="font-medium">${bet.wager1}</span></span>
                      <span className="text-gray-600">Type: <span className="font-medium">{bet.type}</span></span>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getBetStatusColor(bet.status)}`}>
                    {getBetStatusText(bet.status)}
                  </span>

                  {/* ✅ Add Accept button for pending bets */}
                  {bet.u1 !== userData?.username && bet.status === "Pending" && (
                    <button
                      onClick={() => acceptBet(bet.uuid)}
                      className="btn-primary text-xs px-3 py-1"
                    >
                      Accept Bet
                    </button>
                  )}

                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Open Bets Section */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Open Public Bets</h2>
          <button 
            onClick={fetchOpenBets}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            Refresh
          </button>
        </div>
        
        {openBets.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No open public bets available.</p>
        ) : (
          <div className="space-y-3">
            {openBets.map((bet) => (
              <div key={bet.uuid} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{bet.coursecode}</h3>
                    <p className="text-sm text-gray-600">{bet.assessment}</p>
                    <div className="flex items-center space-x-4 mt-2 text-sm">
                      <span className="text-gray-600">User: <span className="font-medium">{bet.u1}</span></span>
                      <span className="text-gray-600">Target: <span className="font-medium">Above {bet.lower}%</span></span>
                      <span className="text-gray-600">Wager: <span className="font-medium">${bet.wager1}</span></span>
                    </div>
                    {bet.description && (
                      <p className="text-sm text-gray-500 mt-2">{bet.description}</p>
                    )}
                  </div>
                  <div className="flex flex-col space-y-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getBetStatusColor(bet.status)}`}>
                      {getBetStatusText(bet.status)}
                    </span>
                    {bet.u1 !== userData?.username && bet.status === "Pending" && (
                      <button
                        onClick={() => acceptBet(bet.uuid)}
                        className="btn-primary text-xs px-3 py-1"
                      >
                        Accept Bet
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;