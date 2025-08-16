import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, RefreshCw, TrendingUp, TrendingDown, DollarSign, Bell } from 'lucide-react';

const Dashboard = () => {
  // Mock data - replace with real data from your backend
  const [accountBalance] = useState(1250.75);
  const [pendingBets] = useState(3);
  const [activeBets] = useState([
    {
      id: 1,
      course: 'COMP3506 - Algorithms & Complexity',
      assessment: 'Final Exam',
      targetGrade: 'HD (85%)',
      wager: 50.00,
      status: 'pending',
      expiration: '2025-02-15'
    },
    {
      id: 2,
      course: 'COMP3702 - Artificial Intelligence',
      assessment: 'Assignment 2',
      targetGrade: 'D (75%)',
      wager: 75.00,
      status: 'accepted',
      expiration: '2025-01-30'
    }
  ]);

  const [notifications] = useState([
    {
      id: 1,
      type: 'bet_accepted',
      message: 'Your bet on COMP3702 Assignment 2 has been accepted!',
      time: '2 hours ago'
    },
    {
      id: 2,
      type: 'bet_resolved',
      message: 'Bet on COMP3506 Midterm resolved - You won $45!',
      time: '1 day ago'
    }
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-warning-100 text-warning-800 border-warning-200';
      case 'accepted':
        return 'bg-success-100 text-success-800 border-success-200';
      case 'won':
        return 'bg-success-100 text-success-800 border-success-200';
      case 'lost':
        return 'bg-danger-100 text-danger-800 border-danger-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'accepted':
        return 'Accepted';
      case 'won':
        return 'Won';
      case 'lost':
        return 'Lost';
      default:
        return status;
    }
  };

return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        {/* Removed the Refresh Grades button */}
      </div>

      {/* Account Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Account Balance</p>
              <p className="text-2xl font-bold text-gray-900">${accountBalance.toFixed(2)}</p>
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
              <p className="text-sm font-medium text-gray-600">Active Bets</p>
              <p className="text-2xl font-bold text-gray-900">{activeBets.length}</p>
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

          <button className="flex items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-colors duration-200 group">
            <div className="text-center">
              <RefreshCw className="w-12 h-12 text-gray-400 group-hover:text-gray-500 mx-auto mb-3" />
              <p className="text-lg font-medium text-gray-600 group-hover:text-gray-700">Sync Grades</p>
              <p className="text-sm text-gray-500">Update your latest grades from Blackboard</p>
            </div>
          </button>
        </div>
      </div>

      {/* My Bets Section */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">My Bets</h2>
          <Link to="/history" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>
        
        {activeBets.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No active bets yet.</p>
            <Link to="/create-bet" className="btn-primary mt-3 inline-block">
              Place Your First Bet
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {activeBets.map((bet) => (
              <div key={bet.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{bet.course}</h3>
                    <p className="text-sm text-gray-600">{bet.assessment}</p>
                    <div className="flex items-center space-x-4 mt-2 text-sm">
                      <span className="text-gray-600">Target: <span className="font-medium">{bet.targetGrade}</span></span>
                      <span className="text-gray-600">Wager: <span className="font-medium">${bet.wager.toFixed(2)}</span></span>
                      <span className="text-gray-600">Expires: <span className="font-medium">{bet.expiration}</span></span>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(bet.status)}`}>
                    {getStatusText(bet.status)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Notifications */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Bell className="w-5 h-5 text-gray-600" />
          <h2 className="text-xl font-semibold text-gray-900">Recent Notifications</h2>
        </div>
        
        {notifications.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No new notifications.</p>
        ) : (
          <div className="space-y-3">
            {notifications.map((notification) => (
              <div key={notification.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{notification.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
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
