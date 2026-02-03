import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Questions for assessment
const QUESTIONS = [
  {
    id: 1,
    question: "How often do you feel mentally exhausted after work?",
    options: ["Never", "Sometimes", "Often", "Always"]
  },
  {
    id: 2,
    question: "How frequently do you think about work outside of work hours?",
    options: ["Never", "Sometimes", "Often", "Always"]
  },
  {
    id: 3,
    question: "How would you describe your motivation level in the morning?",
    options: ["High and energized", "Moderate", "Low", "Very low or none"]
  },
  {
    id: 4,
    question: "How often do you feel overwhelmed by your tasks?",
    options: ["Never", "Sometimes", "Often", "Always"]
  },
  {
    id: 5,
    question: "How satisfied are you with your work-life balance?",
    options: ["Very satisfied", "Somewhat satisfied", "Not very satisfied", "Not satisfied at all"]
  },
  {
    id: 6,
    question: "How would you rate your sleep quality on workdays?",
    options: ["Excellent", "Good", "Poor", "Very poor"]
  },
  {
    id: 7,
    question: "Do you find meaning and purpose in your work?",
    options: ["Always", "Often", "Sometimes", "Never"]
  }
];

function App() {
  // State management
  const [step, setStep] = useState('registration'); // registration, email_otp, mobile_otp, assessment, preview, payment_return, report
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Registration data
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [mobile, setMobile] = useState('');
  
  // OTP data
  const [emailOtp, setEmailOtp] = useState('');
  const [mobileOtp, setMobileOtp] = useState('');
  const [otpMessage, setOtpMessage] = useState('');
  
  // Assessment data
  const [answers, setAnswers] = useState({});
  
  // Results data
  const [score, setScore] = useState(null);
  const [level, setLevel] = useState('');
  const [previewInsight, setPreviewInsight] = useState('');
  const [reportContent, setReportContent] = useState('');
  
  // Check for payment return on load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const paymentStatus = urlParams.get('payment');
    const returnedSessionId = urlParams.get('session_id');
    
    if (paymentStatus === 'success' && returnedSessionId) {
      setSessionId(returnedSessionId);
      handlePaymentReturn(returnedSessionId);
    }
  }, []);
  
  // Step 1: Registration
  const handleRegistration = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/register`, {
        full_name: fullName,
        email: email,
        mobile: mobile
      });
      
      if (response.data.success) {
        setSessionId(response.data.session_id);
        // Automatically send email OTP
        await sendOTP(response.data.session_id, 'email');
        setStep('email_otp');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };
  
  // Send OTP
  const sendOTP = async (sid, type) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/otp/send`, {
        session_id: sid || sessionId,
        otp_type: type
      });
      
      if (response.data.success) {
        setOtpMessage(`OTP sent to your ${type}`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to send OTP to ${type}`);
    }
  };
  
  // Resend OTP
  const handleResendOTP = async (type) => {
    setLoading(true);
    setError('');
    try {
      await sendOTP(sessionId, type);
    } finally {
      setLoading(false);
    }
  };
  
  // Verify Email OTP
  const handleEmailOtpVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/otp/verify`, {
        session_id: sessionId,
        otp_type: 'email',
        otp_code: emailOtp
      });
      
      if (response.data.success) {
        // Automatically send mobile OTP
        await sendOTP(sessionId, 'mobile');
        setStep('mobile_otp');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };
  
  // Verify Mobile OTP
  const handleMobileOtpVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/otp/verify`, {
        session_id: sessionId,
        otp_type: 'mobile',
        otp_code: mobileOtp
      });
      
      if (response.data.success) {
        setStep('assessment');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle answer selection
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };
  
  // Submit Assessment
  const handleAssessmentSubmit = async (e) => {
    e.preventDefault();
    
    if (Object.keys(answers).length !== 7) {
      setError('Please answer all 7 questions');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessment/submit`, {
        session_id: sessionId,
        answers: answers
      });
      
      if (response.data.success) {
        setScore(response.data.score);
        setLevel(response.data.level);
        setPreviewInsight(response.data.preview_insight);
        setStep('preview');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };
  
  // Unlock Full Report (Redirect to Gumroad)
  const handleUnlockReport = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/payment/redirect`, {
        params: { session_id: sessionId }
      });
      
      if (response.data.success) {
        // Redirect to Gumroad
        window.location.href = response.data.payment_url;
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initiate payment');
      setLoading(false);
    }
  };
  
  // Handle Payment Return
  const handlePaymentReturn = async (sid) => {
    setLoading(true);
    setError('');
    
    try {
      // Confirm payment
      const confirmResponse = await axios.post(`${API_BASE_URL}/api/payment/confirm`, {
        session_id: sid
      });
      
      if (confirmResponse.data.success) {
        // Generate report
        const generateResponse = await axios.post(`${API_BASE_URL}/api/report/generate`, {
          session_id: sid
        });
        
        if (generateResponse.data.success) {
          setReportContent(generateResponse.data.report_content);
          
          // Send email
          await axios.post(`${API_BASE_URL}/api/report/email`, {
            session_id: sid
          });
          
          setStep('report');
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process payment return');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3" data-testid="app-title">
            Burnout Score Checker
          </h1>
          <p className="text-lg text-gray-600">
            Professional burnout assessment for working professionals
          </p>
        </header>
        
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-6" data-testid="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {/* Step 1: Registration */}
        {step === 'registration' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6" data-testid="registration-title">Get Started</h2>
            <form onSubmit={handleRegistration} data-testid="registration-form">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                    data-testid="full-name-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="john@example.com"
                    data-testid="email-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mobile Number</label>
                  <input
                    type="tel"
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                    required
                    minLength="10"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="+1234567890"
                    data-testid="mobile-input"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                data-testid="register-button"
              >
                {loading ? 'Processing...' : 'Continue'}
              </button>
            </form>
          </div>
        )}
        
        {/* Step 2: Email OTP Verification */}
        {step === 'email_otp' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4" data-testid="email-otp-title">Verify Your Email</h2>
            <p className="text-gray-600 mb-6">We've sent a 6-digit code to <strong>{email}</strong></p>
            {otpMessage && <p className="text-green-600 mb-4">{otpMessage}</p>}
            <form onSubmit={handleEmailOtpVerify} data-testid="email-otp-form">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Enter 6-digit OTP</label>
                <input
                  type="text"
                  value={emailOtp}
                  onChange={(e) => setEmailOtp(e.target.value)}
                  required
                  maxLength="6"
                  pattern="[0-9]{6}"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-center text-2xl tracking-widest focus:ring-2 focus:ring-blue-500"
                  placeholder="000000"
                  data-testid="email-otp-input"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                data-testid="verify-email-button"
              >
                {loading ? 'Verifying...' : 'Verify Email'}
              </button>
              <button
                type="button"
                onClick={() => handleResendOTP('email')}
                disabled={loading}
                className="w-full mt-3 text-blue-600 hover:text-blue-700 font-medium"
                data-testid="resend-email-otp-button"
              >
                Resend OTP
              </button>
            </form>
          </div>
        )}
        
        {/* Step 3: Mobile OTP Verification */}
        {step === 'mobile_otp' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4" data-testid="mobile-otp-title">Verify Your Mobile</h2>
            <p className="text-gray-600 mb-6">We've sent a 6-digit code to <strong>{mobile}</strong></p>
            {otpMessage && <p className="text-green-600 mb-4">{otpMessage}</p>}
            <form onSubmit={handleMobileOtpVerify} data-testid="mobile-otp-form">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Enter 6-digit OTP</label>
                <input
                  type="text"
                  value={mobileOtp}
                  onChange={(e) => setMobileOtp(e.target.value)}
                  required
                  maxLength="6"
                  pattern="[0-9]{6}"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-center text-2xl tracking-widest focus:ring-2 focus:ring-blue-500"
                  placeholder="000000"
                  data-testid="mobile-otp-input"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                data-testid="verify-mobile-button"
              >
                {loading ? 'Verifying...' : 'Verify Mobile'}
              </button>
              <button
                type="button"
                onClick={() => handleResendOTP('mobile')}
                disabled={loading}
                className="w-full mt-3 text-blue-600 hover:text-blue-700 font-medium"
                data-testid="resend-mobile-otp-button"
              >
                Resend OTP
              </button>
            </form>
          </div>
        )}
        
        {/* Step 4: Assessment */}
        {step === 'assessment' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6" data-testid="assessment-title">Burnout Assessment</h2>
            <form onSubmit={handleAssessmentSubmit} data-testid="assessment-form">
              <div className="space-y-8">
                {QUESTIONS.map((q, index) => (
                  <div key={q.id} className="border-b border-gray-200 pb-6 last:border-b-0">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      {index + 1}. {q.question}
                    </h3>
                    <div className="space-y-2">
                      {q.options.map((option, optionIndex) => (
                        <label
                          key={optionIndex}
                          className="flex items-center p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                          data-testid={`question-${q.id}-option-${optionIndex}`}
                        >
                          <input
                            type="radio"
                            name={`question-${q.id}`}
                            value={optionIndex}
                            checked={answers[q.id] === optionIndex}
                            onChange={() => handleAnswerChange(q.id, optionIndex)}
                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                            data-testid={`question-${q.id}-radio-${optionIndex}`}
                          />
                          <span className="ml-3 text-gray-700">{option}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-8 bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                data-testid="submit-assessment-button"
              >
                {loading ? 'Calculating...' : 'Get My Burnout Score'}
              </button>
            </form>
          </div>
        )}
        
        {/* Step 5: Preview Results + Payment Gate */}
        {step === 'preview' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center" data-testid="preview-title">
              Your Burnout Score
            </h2>
            
            <div className="text-center mb-6">
              <div className="inline-block bg-blue-50 rounded-lg p-6 mb-4">
                <div className="text-5xl font-bold text-blue-600" data-testid="burnout-score">{score}</div>
                <div className="text-gray-600 mt-1">out of 100</div>
              </div>
              
              <div className="mb-4">
                <span className="text-lg text-gray-700">Burnout Level: </span>
                <span
                  className={`text-xl font-bold ${
                    level === 'Low' ? 'text-green-600' :
                    level === 'Moderate' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}
                  data-testid="burnout-level"
                >
                  {level}
                </span>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-gray-800 mb-2">Preview Insight:</h3>
              <p className="text-gray-700" data-testid="preview-insight">{previewInsight}</p>
            </div>
            
            <div className="border-t-2 border-gray-200 pt-6 mt-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3">🔒 Unlock Your Full Recovery Report</h3>
                <ul className="text-sm text-gray-700 space-y-2 mb-4">
                  <li>✓ Complete personalized burnout analysis</li>
                  <li>✓ Detailed 14-day recovery action plan</li>
                  <li>✓ Work-life boundary strategies</li>
                  <li>✓ Sustainable habits to prevent relapse</li>
                  <li>✓ Email delivery + on-screen access</li>
                </ul>
              </div>
              
              <button
                onClick={handleUnlockReport}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-lg font-bold text-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg disabled:opacity-50"
                data-testid="unlock-report-button"
              >
                {loading ? 'Redirecting...' : 'Unlock Full Burnout Recovery Report'}
              </button>
            </div>
          </div>
        )}
        
        {/* Step 6: Full Report Display */}
        {step === 'report' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-700 font-medium" data-testid="report-success-message">
                ✓ Your full report has been generated and sent to your email!
              </p>
            </div>
            
            <div
              className="prose max-w-none"
              data-testid="full-report-content"
              dangerouslySetInnerHTML={{ __html: reportContent.replace(/\n/g, '<br>') }}
            />
          </div>
        )}
        
        {/* Loading Overlay */}
        {loading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-700 mt-4">Processing...</p>
            </div>
          </div>
        )}
        
        {/* Footer */}
        <footer className="text-center text-gray-500 text-sm mt-12">
          <p>For informational purposes only. Not a substitute for professional advice.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;