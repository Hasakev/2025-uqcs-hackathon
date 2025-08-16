import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Target, DollarSign, Calendar, Users, Eye, EyeOff, AlertCircle } from 'lucide-react';

const CreateBet = () => {
  const navigate = useNavigate();
  
  // Mock data - replace with real data from your backend
  const [courses] = useState([
    'COMP3506 - Algorithms & Complexity',
    'COMP3702 - Artificial Intelligence',
    'COMP3400 - Computer Systems',
    'COMP3500 - Programming Languages',
    'COMP3600 - Design Computing Studio'
  ]);

  const [assessments] = useState([
    'Assignment 1',
    'Assignment 2',
    'Assignment 3',
    'Midterm Exam',
    'Final Exam',
    'Project'
  ]);

  const [formData, setFormData] = useState({
    course: '',
    assessment: '',
    targetGrade: '',
    wagerAmount: '',
    expirationDate: '',
    isPublic: true,
    invitedPeers: '',
    description: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const gradeOptions = [
    { value: 'HD', label: 'HD (85%+)', description: 'High Distinction' },
    { value: 'D', label: 'D (75-84%)', description: 'Distinction' },
    { value: 'C', label: 'C (65-74%)', description: 'Credit' },
    { value: 'P', label: 'P (50-64%)', description: 'Pass' },
    { value: 'F', label: 'F (<50%)', description: 'Fail' }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.course) newErrors.course = 'Please select a course';
    if (!formData.assessment) newErrors.assessment = 'Please select an assessment';
    if (!formData.targetGrade) newErrors.targetGrade = 'Please select a target grade';
    if (!formData.wagerAmount) {
      newErrors.wagerAmount = 'Please enter a wager amount';
    } else if (parseFloat(formData.wagerAmount) < 5) {
      newErrors.wagerAmount = 'Minimum wager is $5.00';
    } else if (parseFloat(formData.wagerAmount) > 500) {
      newErrors.wagerAmount = 'Maximum wager is $500.00';
    }
    if (!formData.expirationDate) newErrors.expirationDate = 'Please select an expiration date';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Mock API call - replace with real API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show success message and redirect
      alert('Bet created successfully!');
      navigate('/');
    } catch (error) {
      alert('Failed to create bet. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getMinimumDate = () => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => navigate(-1)}
          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors duration-200"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Create New Bet</h1>
      </div>

      {/* Rules Reminder */}
      <div className="card mb-6 bg-blue-50 border-blue-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium text-blue-900">Betting Rules & Guidelines</h3>
            <ul className="text-sm text-blue-800 mt-2 space-y-1">
              <li>• Minimum wager: $5.00, Maximum wager: $500.00</li>
              <li>• Bets expire after the assessment due date</li>
              <li>• You can only bet on your own grades</li>
              <li>• Public bets are visible to all users</li>
              <li>• Private bets can only be seen by invited peers</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bet Creation Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Course Selection */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <BookOpen className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Course & Assessment</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="course" className="block text-sm font-medium text-gray-700 mb-2">
                Course *
              </label>
              <select
                id="course"
                name="course"
                value={formData.course}
                onChange={handleInputChange}
                className={`input-field ${errors.course ? 'border-danger-500' : ''}`}
              >
                <option value="">Select a course</option>
                {courses.map((course, index) => (
                  <option key={index} value={course}>{course}</option>
                ))}
              </select>
              {errors.course && (
                <p className="mt-1 text-sm text-danger-600">{errors.course}</p>
              )}
            </div>

            <div>
              <label htmlFor="assessment" className="block text-sm font-medium text-gray-700 mb-2">
                Assessment *
              </label>
              <select
                id="assessment"
                name="assessment"
                value={formData.assessment}
                onChange={handleInputChange}
                className={`input-field ${errors.assessment ? 'border-danger-500' : ''}`}
              >
                <option value="">Select an assessment</option>
                {assessments.map((assessment, index) => (
                  <option key={index} value={assessment}>{assessment}</option>
                ))}
              </select>
              {errors.assessment && (
                <p className="mt-1 text-sm text-danger-600">{errors.assessment}</p>
              )}
            </div>
          </div>
        </div>

        {/* Bet Details */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Target className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Bet Details</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="targetGrade" className="block text-sm font-medium text-gray-700 mb-2">
                Target Grade *
              </label>
              <select
                id="targetGrade"
                name="targetGrade"
                value={formData.targetGrade}
                onChange={handleInputChange}
                className={`input-field ${errors.targetGrade ? 'border-danger-500' : ''}`}
              >
                <option value="">Select target grade</option>
                {gradeOptions.map((grade) => (
                  <option key={grade.value} value={grade.value}>
                    {grade.label} - {grade.description}
                  </option>
                ))}
              </select>
              {errors.targetGrade && (
                <p className="mt-1 text-sm text-danger-600">{errors.targetGrade}</p>
              )}
            </div>

            <div>
              <label htmlFor="wagerAmount" className="block text-sm font-medium text-gray-700 mb-2">
                Wager Amount ($) *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <DollarSign className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="number"
                  id="wagerAmount"
                  name="wagerAmount"
                  value={formData.wagerAmount}
                  onChange={handleInputChange}
                  min="5"
                  max="500"
                  step="0.01"
                  placeholder="0.00"
                  className={`input-field pl-10 ${errors.wagerAmount ? 'border-danger-500' : ''}`}
                />
              </div>
              {errors.wagerAmount && (
                <p className="mt-1 text-sm text-danger-600">{errors.wagerAmount}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">Min: $5.00 | Max: $500.00</p>
            </div>

            <div>
              <label htmlFor="expirationDate" className="block text-sm font-medium text-gray-700 mb-2">
                Expiration Date *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Calendar className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="date"
                  id="expirationDate"
                  name="expirationDate"
                  value={formData.expirationDate}
                  onChange={handleInputChange}
                  min={getMinimumDate()}
                  className={`input-field pl-10 ${errors.expirationDate ? 'border-danger-500' : ''}`}
                />
              </div>
              {errors.expirationDate && (
                <p className="mt-1 text-sm text-danger-600">{errors.expirationDate}</p>
              )}
            </div>
          </div>
        </div>

        {/* Privacy Settings */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Users className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Privacy & Visibility</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="isPublic"
                name="isPublic"
                checked={formData.isPublic}
                onChange={handleInputChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="isPublic" className="text-sm font-medium text-gray-700">
                Make this bet public (visible to all users)
              </label>
            </div>

            {!formData.isPublic && (
              <div>
                <label htmlFor="invitedPeers" className="block text-sm font-medium text-gray-700 mb-2">
                  Invite Specific Peers (optional)
                </label>
                <input
                  type="text"
                  id="invitedPeers"
                  name="invitedPeers"
                  value={formData.invitedPeers}
                  onChange={handleInputChange}
                  placeholder="Enter usernames separated by commas"
                  className="input-field"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Leave empty to make it private to yourself only
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Description */}
        <div className="card">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Additional Notes (optional)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={3}
            placeholder="Any additional context about your bet..."
            className="input-field resize-none"
          />
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating Bet...' : 'Create Bet'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateBet;
