import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Target, DollarSign, Calendar, Users, Eye, EyeOff, AlertCircle } from 'lucide-react';

const CreateBet = () => {
  const navigate = useNavigate();
  
  const semesterOptions = [
    { value: '1,24', label: 'Semester 1, 2024'},
    { value: '2,24', label: 'Semester 2, 2024'},
    { value: '3,24', label: 'Summer Semester, 2024'},
    { value: '1,25', label: 'Semester 1, 2025'},
    { value: '2,25', label: 'Semester 2, 2025'},
    { value: '3,25', label: 'Summer Semester, 2025'}
  ];

  const [formData, setFormData] = useState({
    user1:'',
    type: 1,
    courseCode: '', // Changed from 'course'
    semester: '', // New field
    assessment: '',
    targetGrade: '',
    lower: '',
    wagerAmount: '',
    expirationDate: '',
    isPublic: true,
    invitedPeers: '',
    description: ''
  });

  // Add these missing state variables
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Add state for API assessments
  const [assessments, setAssessments] = useState([]);
  const [isLoadingAssessments, setIsLoadingAssessments] = useState(false);


  // ✅ Auto-fill username from localStorage when component mounts
  useEffect(() => {
    const storedData = localStorage.getItem('userData');
    if (storedData) {
      const userData = JSON.parse(storedData);
      if (userData.username) {
        setFormData(prev => ({
          ...prev,
          user1: userData.username
        }));
        console.log('Username auto-filled:', userData.username);
      }
    }
  }, []);



  const gradeOptions = [
    { value: 'HD', label: 'HD (85%+)', description: 'High Distinction' },
    { value: 'D', label: 'D (75-84%)', description: 'Distinction' },
    { value: 'C', label: 'C (65-74%)', description: 'Credit' },
    { value: 'P', label: 'P (50-64%)', description: 'Pass' },
    { value: 'F', label: 'F (<50%)', description: 'Fail' }
  ];


  const fetchAssessments = async (courseCode, semester) => {
    if (!courseCode || courseCode.length < 3 || !semester) return;
    
    // Parse semester format (e.g., "1,25" -> semester: 1, year: 2025)
    const [sem, year] = semester.split(',');
    const fullYear = `20${year}`;
    
    setIsLoadingAssessments(true);
    try {
      const url = `https://4bv6rwmc-5000.auc1.devtunnels.ms/courses/${courseCode}/${sem}/${fullYear}/assessments`;
      console.log('Fetching assessments from:', url);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      
      if (Array.isArray(data)) {
        setAssessments(data);
        console.log('Assessments set successfully:', data.length, 'items');
      } else {
        console.error('API response is not an array:', data);
        setAssessments([]);
      }
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
      setAssessments([]);
    } finally {
      setIsLoadingAssessments(false);
    }
  };


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
    
    if (name === 'courseCode' || name === 'semester') {
      if (name === 'courseCode') {
        // If course code changed, wait for semester to be selected
        if (formData.semester) {
          fetchAssessments(value, formData.semester);
        }
      } else if (name === 'semester') {
        // If semester changed, check if course code exists
        if (formData.courseCode) {
          fetchAssessments(formData.courseCode, value);
        }
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};
  
    if (!formData.user1) newErrors.user1 = 'Please enter a username';
    if (!formData.courseCode) newErrors.courseCode = 'Please enter a course code';
    if (!formData.semester) newErrors.semester = 'Please select a semester';
    if (!formData.assessment) newErrors.assessment = 'Please select an assessment';
    if (!formData.targetGrade) newErrors.targetGrade = 'Please select a target grade';
    if (!formData.lower) newErrors.lower = 'Please enter lower bound';
    if (!formData.wagerAmount) {
      newErrors.wagerAmount = 'Please enter a wager amount';
    } else if (parseFloat(formData.wagerAmount) < 5) {
      newErrors.wagerAmount = 'Minimum wager is $5.00';
    } else if (parseFloat(formData.wagerAmount) > 500) {
      newErrors.wagerAmount = 'Maximum wager is $500.00';
    }
  
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted');
    
    if (!validateForm()) {
      console.log('validation failed');
      return;
    }
    console.log('Validation passed, starting submission...');
    setIsSubmitting(true);
    
    try {
      // Parse semester to get year
      const [sem, year] = formData.semester.split(',');
      const fullYear = `20${year}`;
      
      // Prepare data in your exact format
      const betData = {
        u1: formData.user1,
        u2: "NONE",
        type: 'M',
        coursecode: formData.courseCode,
        year: fullYear,
        semester: formData.semester,
        assessment: formData.assessment,
        upper: 100, // Always set to 100 for "above" type
        lower: formData.lower,
        wager1: formData.wagerAmount,
        wager2: formData.wagerAmount,
        description: formData.description
      };

      console.log('Submitting bet data:', betData);


       // Send to your API
       const response = await fetch('https://4bv6rwmc-5000.auc1.devtunnels.ms/create_bet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(betData)
      });
      
      if (response.ok) {
        alert('Bet created successfully!');
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        alert(errorData.error || 'Failed to create bet');
      }
    } catch (error) {
      console.error('Error creating bet:', error);
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



        {/* User & Bet Type Selection */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Users className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">User & Bet Type</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="user1" className="block text-sm font-medium text-gray-700 mb-2">
                Username *
              </label>
              <input
                type="text"
                id="user1"
                name="user1"
                value={formData.user1}
                onChange={handleInputChange}
                placeholder="Enter your username"
                className={`input-field ${errors.user1 ? 'border-danger-500' : ''}`}
              />
              {errors.user1 && (
                <p className="mt-1 text-sm text-danger-600">{errors.user1}</p>
              )}
            </div>

            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-2">
                Bet Type
              </label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="input-field"
              >
                <option value="above">Above (Upper: 100)</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">Currently only supports "above" type with upper bound of 100</p>
            </div>

            <div>
              <label htmlFor="lower" className="block text-sm font-medium text-gray-700 mb-2">
                Lower Bound *
              </label>
              <input
                type="number"
                id="lower"
                name="lower"
                value={formData.lower}
                onChange={handleInputChange}
                min="0"
                max="99"
                placeholder="Enter lower bound (0-99)"
                className={`input-field ${errors.lower ? 'border-danger-500' : ''}`}
              />
              {errors.lower && (
                <p className="mt-1 text-sm text-danger-600">{errors.lower}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">You're betting to score above this percentage</p>
            </div>
          </div>
        </div>



        {/* Course & Semester Selection */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <BookOpen className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Course & Semester</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="courseCode" className="block text-sm font-medium text-gray-700 mb-2">
                Course Code *
              </label>
              <input
                type="text"
                id="courseCode"
                name="courseCode"
                value={formData.courseCode}
                onChange={handleInputChange}
                placeholder="e.g., COMP3506"
                className={`input-field ${errors.courseCode ? 'border-danger-500' : ''}`}
              />
              {errors.courseCode && (
                <p className="mt-1 text-sm text-danger-600">{errors.courseCode}</p>
              )}
            </div>

            <div>
              <label htmlFor="semester" className="block text-sm font-medium text-gray-700 mb-2">
                Semester *
              </label>
              <select
                id="semester"
                name="semester"
                value={formData.semester}
                onChange={handleInputChange}
                className={`input-field ${errors.semester ? 'border-danger-500' : ''}`}
              >
                <option value="">Select a semester</option>
                {semesterOptions.map((semester) => (
                  <option key={semester.value} value={semester.value}>
                    {semester.label}
                  </option>
                ))}
              </select>
              {errors.semester && (
                <p className="mt-1 text-sm text-danger-600">{errors.semester}</p>
              )}
            </div>

            {/* Assessment Selection - Now populated from API */}
            <div>
              <label htmlFor="assessment" className="block text-sm font-medium text-gray-700 mb-2">
                Assessment *
              </label>
              <select
                id="assessment"
                name="assessment"
                value={formData.assessment}
                onChange={handleInputChange}
                disabled={isLoadingAssessments || assessments.length === 0}
                className={`input-field ${errors.assessment ? 'border-danger-500' : ''}`}
              >
                <option value="">
                  {isLoadingAssessments 
                    ? 'Loading assessments...' 
                    : assessments.length === 0 
                      ? 'Enter course code to see assessments' 
                      : 'Select an assessment'
                  }
                </option>
                {assessments.map((assessment, index) => (
                  <option key={index} value={assessment['Assessment task']}>
                    {assessment['Assessment task']} ({assessment['Category']}) - {assessment['Weight']}%
                  </option>
                ))}
              </select>
              {errors.assessment && (
                <p className="mt-1 text-sm text-danger-600">{errors.assessment}</p>
              )}
              {isLoadingAssessments && (
                <p className="mt-1 text-xs text-gray-500">Loading assessments...</p>
              )}

              {!isLoadingAssessments && (
                  <p className="mt-1 text-xs text-gray-500">
                    {Array.isArray(assessments) ? `${assessments.length} assessments found` : 'No assessments data'}
                  </p>
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
