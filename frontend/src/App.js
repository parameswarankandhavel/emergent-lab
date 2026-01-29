import React, { useState } from 'react';

// Questions for the burnout assessment
const QUESTIONS = [
  {
    id: 1,
    question: "How often do you feel mentally exhausted after work?",
    options: [
      { label: "Never", value: 0 },
      { label: "Sometimes", value: 1 },
      { label: "Often", value: 2 },
      { label: "Always", value: 3 }
    ]
  },
  {
    id: 2,
    question: "How frequently do you think about work outside of work hours?",
    options: [
      { label: "Never", value: 0 },
      { label: "Sometimes", value: 1 },
      { label: "Often", value: 2 },
      { label: "Always", value: 3 }
    ]
  },
  {
    id: 3,
    question: "How would you describe your motivation level in the morning?",
    options: [
      { label: "High and energized", value: 0 },
      { label: "Moderate", value: 1 },
      { label: "Low", value: 2 },
      { label: "Very low or none", value: 3 }
    ]
  },
  {
    id: 4,
    question: "How often do you feel overwhelmed by your tasks?",
    options: [
      { label: "Never", value: 0 },
      { label: "Sometimes", value: 1 },
      { label: "Often", value: 2 },
      { label: "Always", value: 3 }
    ]
  },
  {
    id: 5,
    question: "How satisfied are you with your work-life balance?",
    options: [
      { label: "Very satisfied", value: 0 },
      { label: "Somewhat satisfied", value: 1 },
      { label: "Not very satisfied", value: 2 },
      { label: "Not satisfied at all", value: 3 }
    ]
  },
  {
    id: 6,
    question: "How would you rate your sleep quality on workdays?",
    options: [
      { label: "Excellent", value: 0 },
      { label: "Good", value: 1 },
      { label: "Poor", value: 2 },
      { label: "Very poor", value: 3 }
    ]
  },
  {
    id: 7,
    question: "Do you find meaning and purpose in your work?",
    options: [
      { label: "Always", value: 0 },
      { label: "Often", value: 1 },
      { label: "Sometimes", value: 2 },
      { label: "Never", value: 3 }
    ]
  }
];

// Function to calculate burnout score and details
function calculateBurnoutScore(answers) {
  // Sum all answer values (each answer is 0-3)
  const rawScore = Object.values(answers).reduce((sum, val) => sum + val, 0);
  
  // Convert to 0-100 scale (max raw score is 21)
  const score = Math.round((rawScore / 21) * 100);
  
  // Determine burnout level
  let level = "";
  let insight = "";
  
  if (score <= 33) {
    level = "Low";
    insight = "You're managing well! Your burnout risk is low. Keep maintaining healthy work-life boundaries and continue prioritizing self-care to stay balanced.";
  } else if (score <= 66) {
    level = "Moderate";
    insight = "You're showing signs of moderate burnout. Consider taking steps to reduce stress, set clearer boundaries, and prioritize rest. Small changes now can prevent bigger issues later.";
  } else {
    level = "High";
    insight = "Your burnout risk is high. It's important to take action now. Consider talking to a manager, counselor, or trusted friend. Prioritize rest and explore ways to reduce your workload or stress.";
  }
  
  return { score, level, insight };
}

function App() {
  // State to store user answers (questionId -> answerValue)
  const [answers, setAnswers] = useState({});
  
  // State to track if form is submitted
  const [submitted, setSubmitted] = useState(false);
  
  // State to store calculated results
  const [results, setResults] = useState(null);

  // Handle answer selection
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Check if all questions are answered
    if (Object.keys(answers).length !== QUESTIONS.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    
    // Calculate results
    const calculatedResults = calculateBurnoutScore(answers);
    setResults(calculatedResults);
    setSubmitted(true);
    
    // Scroll to results
    setTimeout(() => {
      document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  // Reset form
  const handleReset = () => {
    setAnswers({});
    setSubmitted(false);
    setResults(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3" data-testid="app-title">
            Burnout Score Checker
          </h1>
          <p className="text-lg text-gray-600">
            A simple assessment for working professionals
          </p>
        </header>

        {/* Questionnaire Form */}
        {!submitted && (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <form onSubmit={handleSubmit} data-testid="burnout-form">
              <div className="space-y-8">
                {QUESTIONS.map((q, index) => (
                  <div key={q.id} className="border-b border-gray-200 pb-6 last:border-b-0">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      {index + 1}. {q.question}
                    </h3>
                    <div className="space-y-2">
                      {q.options.map((option) => (
                        <label
                          key={option.value}
                          className="flex items-center p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                          data-testid={`question-${q.id}-option-${option.value}`}
                        >
                          <input
                            type="radio"
                            name={`question-${q.id}`}
                            value={option.value}
                            checked={answers[q.id] === option.value}
                            onChange={() => handleAnswerChange(q.id, option.value)}
                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                            data-testid={`question-${q.id}-radio-${option.value}`}
                          />
                          <span className="ml-3 text-gray-700">{option.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 text-center">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-md"
                  data-testid="submit-button"
                >
                  Check My Burnout Score
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Results Section */}
        {submitted && results && (
          <div id="results-section" className="bg-white rounded-lg shadow-md p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center" data-testid="results-title">
              Your Results
            </h2>
            
            {/* Score Display */}
            <div className="text-center mb-6">
              <div className="inline-block bg-blue-50 rounded-lg p-6 mb-4">
                <div className="text-5xl font-bold text-blue-600" data-testid="burnout-score">
                  {results.score}
                </div>
                <div className="text-gray-600 mt-1">out of 100</div>
              </div>
              
              {/* Burnout Level */}
              <div className="mb-4">
                <span className="text-lg text-gray-700">Burnout Level: </span>
                <span 
                  className={`text-xl font-bold ${
                    results.level === 'Low' ? 'text-green-600' :
                    results.level === 'Moderate' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}
                  data-testid="burnout-level"
                >
                  {results.level}
                </span>
              </div>
            </div>

            {/* Insight */}
            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-gray-800 mb-2">Personalized Insight:</h3>
              <p className="text-gray-700 leading-relaxed" data-testid="burnout-insight">
                {results.insight}
              </p>
            </div>

            {/* Monetization Placeholder */}
            <div className="text-center mb-6">
              <button
                className="bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-900 transition-colors shadow-md"
                data-testid="unlock-report-button"
                onClick={() => alert('Coming Soon!')}
              >
                Unlock Full Burnout Report (Coming Soon)
              </button>
            </div>

            {/* Retake Button */}
            <div className="text-center">
              <button
                onClick={handleReset}
                className="text-blue-600 hover:text-blue-700 font-medium"
                data-testid="retake-button"
              >
                ← Take Assessment Again
              </button>
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
