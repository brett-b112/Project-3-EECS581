/*
  File Description:
  This file defines the HintViewer component, responsible for fetching, displaying,
  and revealing progressively detailed hints for a given problem. It manages network
  requests, hint usage limits, reveal states, warnings, and user interaction.
  Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, and Arnav Jain.
*/

import React, { useState } from 'react';
import { useAuth } from './AuthContext';

/*
  Component Description:
  Main HintViewer component that retrieves hint metadata, displays partial/full hints,
  and handles reveal actions with usage tracking.
  Inputs: problemId (string/number), onReveal (function)
  Outputs: JSX rendering the hint viewer UI
  Contributors: Daniel Neugent, Jay Patel, Arnav Jain
*/
const HintViewer = ({ problemId, onReveal }) => {
  const { makeAuthenticatedRequest } = useAuth();
  const [hints, setHints] = useState(null);
  const [loading, setLoading] = useState(false);
  const [revealed, setRevealed] = useState({ partial: false, full: false });
  const [error, setError] = useState(null);

  /*
    Function Description:
    Fetches initial hint availability, daily usage, and basic hint metadata from server.
    Inputs: none
    Outputs: none
    Contributors: Tej Gumaste, Brett Balquist
  */
  const fetchHints = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await makeAuthenticatedRequest(`http://localhost:5001/api/hints/${problemId}`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error);
        return;
      }

      setHints(data);
    } catch (err) {
      setError('Failed to fetch hints');
    } finally {
      setLoading(false);
    }
  };

  /*
    Function Description:
    Reveals a specific hint level (partial or full), updates usage, adjusts hint state,
    and notifies parent component.
    Inputs: level (string: 'partial' or 'full')
    Outputs: none
    Contributors: Daniel Neugent, Arnav Jain, Jay Patel
  */
  const revealHint = async (level) => {
    setLoading(true);
    setError(null);
    try {
      const response = await makeAuthenticatedRequest(
        `http://localhost:5001/api/hints/${problemId}/${level}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (!response.ok) {
        setError(data.error);
        return;
      }

      setRevealed(prev => ({ ...prev, [level]: true }));

      if (hints) {
        setHints(prev => ({
          ...prev,
          hints: {
            ...prev.hints,
            [level]: data.hint
          },
          daily_usage: data.daily_usage
        }));
      }

      if (onReveal) {
        onReveal(level, data);
      }
    } catch (err) {
      setError('Failed to reveal hint');
    } finally {
      setLoading(false);
    }
  };

  /*
    Function Description:
    Generates a usage warning message based on hint level and previous reveals.
    Inputs: level (string)
    Outputs: string warning message
    Contributors: Brett Balquist, Tej Gumaste
  */
  const getWarningMessage = (level) => {
    if (level === 'full') {
      if (revealed.partial) {
        return 'This will use 1 hint charge (partial already used)';
      }
      return 'This will use 2 hint charges for the full solution';
    }
    return 'This will use 1 hint charge';
  };

  if (!hints && !loading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <button
          onClick={fetchHints}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Get Hints'}
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-2"></div>
          Loading hints...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
        <p className="text-red-700 mb-2">{error}</p>
        <button
          onClick={fetchHints}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <div className="mb-3">
        <h3 className="font-semibold text-gray-900">Hints</h3>
        <p className="text-sm text-gray-600">
          Daily usage: {hints.daily_usage}/{hints.max_daily_usage}
        </p>
        {hints.problem_hinted_today && (
          <p className="text-sm text-orange-600">⚠️ You've already used hints for this problem today</p>
        )}
      </div>

      {!hints.hints_available && (
        <p className="text-gray-500">No hints available for this problem.</p>
      )}

      {hints.hints && (
        <div className="space-y-3">
          {/* Partial Hint */}
          {hints.hints.partial && (
            <div className="bg-white rounded border p-3">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-900">Partial Hint</h4>
                {!revealed.partial && (
                  <button
                    onClick={() => revealHint('partial')}
                    className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600 transition-colors"
                    disabled={hints.daily_usage >= hints.max_daily_usage}
                  >
                    Reveal (1 charge)
                  </button>
                )}
              </div>
              {revealed.partial && (
                <p className="text-gray-700">{hints.hints.partial}</p>
              )}
            </div>
          )}

          {/* Full Solution */}
          {hints.hints.full && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <div>
                  <h4 className="font-medium text-gray-900">Full Solution</h4>
                  <p className="text-xs text-yellow-700">{getWarningMessage('full')}</p>
                </div>
                {!revealed.full && (
                  <button
                    onClick={() => revealHint('full')}
                    className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600 transition-colors"
                    disabled={hints.daily_usage >= hints.max_daily_usage}
                  >
                    Reveal Solution
                  </button>
                )}
              </div>
              {revealed.full && (
                <div className="bg-red-50 border border-red-300 rounded p-2 mt-2">
                  <p className="text-red-800 font-mono text-sm whitespace-pre-wrap">{hints.hints.full}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HintViewer;
