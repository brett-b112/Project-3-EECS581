/**
 * File Description:
 * This file implements the Authentication Context for the React application. It provides a global
 * state for user authentication, handling login, logout, token storage (local storage), and 
 * automatic token refreshing. It also includes a utility for making authenticated HTTP requests.
 * * Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

/**
 * Function: useAuth
 * Description: A custom hook that allows components to consume the AuthContext.
 * Ensures the hook is used within a valid AuthProvider.
 * Inputs: None
 * Outputs: The AuthContext value (user object, login/logout functions, etc.)
 * Contributors: Jay Patel, Arnav Jain
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Function: AuthProvider
 * Description: The main provider component that wraps the application. It manages the 
 * state for the current user and loading status.
 * Inputs: children (React components to be wrapped)
 * Outputs: JSX Element (AuthContext.Provider)
 * Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for stored tokens on app load
  /**
   * Function: useEffect (Initialization)
   * Description: Runs on component mount to check LocalStorage for existing session data
   * to rehydrate the user state.
   * Inputs: None (Dependency array is empty)
   * Outputs: None (Updates internal state 'user' and 'loading')
   * Contributors: Brett Balquist
   */
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    const userData = localStorage.getItem('userData');

    if (accessToken && userData) {
      setUser(JSON.parse(userData));
    }

    setLoading(false);
  }, []);

  /**
   * Function: login
   * Description: Updates the user state and persists authentication tokens and user data
   * to LocalStorage.
   * Inputs: userData (Object), accessToken (String), refreshToken (String)
   * Outputs: None (Void)
   * Contributors: Daniel Neugent, Tej Gumaste, Jay Patel, Arnav Jain
   */
  const login = (userData, accessToken, refreshToken) => {
    setUser(userData);
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('userData', JSON.stringify(userData));
  };

  /**
   * Function: logout
   * Description: Clears the user state and removes all authentication data from LocalStorage.
   * Inputs: None
   * Outputs: None (Void)
   * Contributors: Tej Gumaste, Daniel Neugent
   */
  const logout = () => {
    setUser(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userData');
  };

  /**
   * Function: getAccessToken
   * Description: Retrieves the current access token directly from LocalStorage.
   * Inputs: None
   * Outputs: accessToken (String) or null
   * Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
   */
  const getAccessToken = () => {
    return localStorage.getItem('accessToken');
  };

  /**
   * Function: refreshAccessToken
   * Description: Attempts to get a new access token from the backend using the stored refresh token.
   * Logs the user out if the refresh fails.
   * Inputs: None (Uses stored refresh token)
   * Outputs: newAccessToken (String) or null
   * Contributors: Jay Patel, Daniel Neugent, Brett Balquist
   */
  const refreshAccessToken = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      logout();
      return null;
    }

    try {
      const response = await fetch('http://localhost:5001/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        const newAccessToken = data.access_token;
        localStorage.setItem('accessToken', newAccessToken);
        return newAccessToken;
      } else {
        logout();
        return null;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return null;
    }
  };

  /**
   * Function: makeAuthenticatedRequest
   * Description: A wrapper around the fetch API that automatically attaches the Authorization header.
   * If a 401 error occurs, it attempts to refresh the token and retry the request.
   * Inputs: url (String), options (Object - fetch options)
   * Outputs: response (Promise<Response>)
   * Contributors: Arnav Jain, Tej Gumaste
   */
  const makeAuthenticatedRequest = async (url, options = {}) => {
    let token = getAccessToken();

    if (!token) {
      throw new Error('No access token available');
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };

    let response = await fetch(url, { ...options, headers });

    // If token is expired, try to refresh it
    if (response.status === 401) {
      token = await refreshAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        response = await fetch(url, { ...options, headers });
      }
    }

    return response;
  };

  const value = {
    user,
    loading,
    login,
    logout,
    getAccessToken,
    makeAuthenticatedRequest,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
