import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [inputType, setInputType] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let response;

      if (inputType === 'text') {
        if (!textInput.trim()) {
          setError('Please enter some text to fact-check');
          setLoading(false);
          return;
        }
        response = await axios.post('/api/factcheck/text', {
          text: textInput
        });
      } else if (inputType === 'url') {
        if (!urlInput.trim()) {
          setError('Please enter a URL to fact-check');
          setLoading(false);
          return;
        }
        response = await axios.post('/api/factcheck/url', {
          url: urlInput
        });
      } else if (inputType === 'image') {
        if (!imageFile) {
          setError('Please select an image to fact-check');
          setLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append('file', imageFile);
        response = await axios.post('/api/factcheck/image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        {/* Header */}
        <header className="header">
          <h1>🔍 Fact-Checker MVP</h1>
          <p className="subtitle">Powered by Alibaba Qwen 3 LLM</p>
        </header>

        {/* Input Section */}
        <div className="input-card">
          <h2>Submit Content for Fact-Checking</h2>
          
          {/* Input Type Selector */}
          <div className="input-type-selector">
            <button 
              className={`type-btn ${inputType === 'text' ? 'active' : ''}`}
              onClick={() => setInputType('text')}
            >
              📝 Text
            </button>
            <button 
              className={`type-btn ${inputType === 'url' ? 'active' : ''}`}
              onClick={() => setInputType('url')}
            >
              🔗 URL
            </button>
            <button 
              className={`type-btn ${inputType === 'image' ? 'active' : ''}`}
              onClick={() => setInputType('image')}
            >
              📷 Image
            </button>
          </div>

          {/* Input Fields */}
          {inputType === 'text' && (
            <textarea 
              className="text-input"
              placeholder="Enter text to fact-check..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              rows={6}
            />
          )}

          {inputType === 'url' && (
            <input 
              type="text"
              className="url-input"
              placeholder="Enter article URL..."
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
            />
          )}

          {inputType === 'image' && (
            <div className="file-input-wrapper">
              <input 
                type="file"
                accept="image/*"
                onChange={(e) => setImageFile(e.target.files[0])}
                id="file-input"
              />
              <label htmlFor="file-input" className="file-label">
                {imageFile ? imageFile.name : 'Choose an image...'}
              </label>
            </div>
          )}

          <button 
            className="submit-btn"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Check Facts'}
          </button>

          {error && (
            <div className="error-box">
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && (
          <div className="results-section">
            {/* Verdict Card */}
            <VerdictCard verdict={results.verdict} confidence={results.confidence} />
            
            {/* Main Claim */}
            <div className="claim-card">
              <h3>📌 Main Claim</h3>
              <p>{results.main_claim}</p>
            </div>

            {/* Missing Context Alert - KEY DIFFERENTIATOR */}
            <MissingContextCard context={results.context} />
            
            {/* Timeline */}
            {results.timeline && results.timeline.length > 0 && (
              <TimelineView timeline={results.timeline} />
            )}

            {/* Evidence Sources */}
            <SourcesList evidence={results.evidence} />

            {/* Scores Breakdown */}
            <ScoresCard scores={results.scores} />
          </div>
        )}
      </div>
    </div>
  );
}

// Verdict Card Component
function VerdictCard({ verdict, confidence }) {
  const getVerdictColor = (verdict) => {
    if (verdict.includes('TRUE') || verdict.includes('VERIFIED')) return 'verdict-true';
    if (verdict.includes('FALSE') || verdict.includes('MISLEADING')) return 'verdict-false';
    return 'verdict-neutral';
  };

  return (
    <div className={`verdict-card ${getVerdictColor(verdict)}`}>
      <div className="verdict-label">Verdict</div>
      <div className="verdict-text">{verdict}</div>
      <div className="confidence-bar-container">
        <div className="confidence-label">Confidence: {(confidence * 100).toFixed(0)}%</div>
        <div className="confidence-bar">
          <div 
            className="confidence-fill"
            style={{ width: `${confidence * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}

// Missing Context Component - Main Innovation
function MissingContextCard({ context }) {
  if (!context || !context.missing_context || context.missing_context.length === 0) {
    return null;
  }

  return (
    <div className="context-card">
      <h3>📋 Context You Should Know</h3>
      <ul className="context-list">
        {context.missing_context.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
      {context.full_picture && (
        <div className="full-picture">
          <strong>Full Picture:</strong>
          <p>{context.full_picture}</p>
        </div>
      )}
    </div>
  );
}

// Timeline Component
function TimelineView({ timeline }) {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="timeline-card">
      <h3>📅 Timeline</h3>
      <div className="timeline">
        {timeline.slice(0, 5).map((event, i) => (
          <div key={i} className="timeline-item">
            <div className="timeline-date">{event.date}</div>
            <div className="timeline-event">{event.event}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Sources List Component
function SourcesList({ evidence }) {
  const allSources = [
    ...(evidence.direct_evidence || []),
    ...(evidence.existing_factchecks || [])
  ];

  if (allSources.length === 0) return null;

  return (
    <div className="sources-card">
      <h3>🔗 Sources</h3>
      <div className="sources-list">
        {allSources.slice(0, 5).map((source, i) => (
          <div key={i} className="source-item">
            <a href={source.url} target="_blank" rel="noopener noreferrer">
              {source.title}
            </a>
            <p className="source-snippet">{source.snippet}</p>
            {source.factcheck_site && (
              <span className="factcheck-badge">✓ Fact-Check Site</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Scores Card Component
function ScoresCard({ scores }) {
  if (!scores) return null;

  const scoreLabels = {
    source_agreement: 'Source Agreement',
    reputable_sources: 'Source Quality',
    context_completeness: 'Context Completeness',
    fact_check_exists: 'Fact-Check Coverage'
  };

  return (
    <div className="scores-card">
      <h3>📊 Detailed Scores</h3>
      <div className="scores-grid">
        {Object.entries(scores).map(([key, value]) => (
          <div key={key} className="score-item">
            <div className="score-label">{scoreLabels[key] || key}</div>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ width: `${value * 100}%` }}
              ></div>
            </div>
            <div className="score-value">{(value * 100).toFixed(0)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
