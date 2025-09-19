// ui/src/App.jsx - Updated with authentication flow
import React, { useState, useEffect } from 'react';
import styled, { createGlobalStyle } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import LoginScreen from './components/LoginScreen';
import FinancialQueryInterface from './components/FinancialQueryInterface';
import AgentStatusDashboard from './components/AgentStatusDashboard';
import ResultsDisplay from './components/ResultsDisplay';
import { useFinancialAdvisor } from './hooks/useFinancialAdvisor';

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
    line-height: 1.6;
  }

  #root {
    min-height: 100vh;
  }
`;

const AppContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
`;

const Header = styled(motion.header)`
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
`;

const LogoutButton = styled(motion.button)`
  position: absolute;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
  }
`;

const WelcomeMessage = styled.div`
  position: absolute;
  top: 20px;
  left: 20px;
  color: #4caf50;
  font-size: 0.9rem;
  font-weight: 500;

  @media (max-width: 768px) {
    position: static;
    margin-bottom: 10px;
  }
`;

const Title = styled.h1`
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;

  @media (max-width: 768px) {
    font-size: 2rem;
  }
`;

const Subtitle = styled.p`
  color: #7f8c8d;
  font-size: 1.2rem;
  margin-bottom: 5px;

  &.tech-stack {
    color: #3498db;
    font-size: 1rem;
    font-weight: 500;
    margin-top: 10px;
  }
`;

const MainGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const LoadingSection = styled(motion.div)`
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  margin-top: 30px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
`;

const Spinner = styled(motion.div)`
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
`;

const LoadingText = styled.p`
  color: #555;
  font-size: 1.1rem;
  font-weight: 500;
`;

function App() {
  const [authState, setAuthState] = useState({
    authenticated: false,
    token: null,
    username: null
  });

  const [showResults, setShowResults] = useState(false);

  const {
    isLoading,
    results,
    agentStatuses,
    analyzeQuery,
    resetAnalysis
  } = useFinancialAdvisor();

  useEffect(() => {
    if (results && !isLoading) {
      setShowResults(true);
    }
  }, [results, isLoading]);

  const handleLogin = (loginData) => {
    setAuthState({
      authenticated: true,
      token: loginData.token,
      username: loginData.username
    });

    // Store token in localStorage for session persistence
    localStorage.setItem('authToken', loginData.token);
    localStorage.setItem('username', loginData.username);
  };

  const handleLogout = () => {
    setAuthState({
      authenticated: false,
      token: null,
      username: null
    });

    // Clear stored authentication
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    
    // Reset any existing analysis
    resetAnalysis();
    setShowResults(false);
  };

  const handleAnalyze = async (queryData) => {
    setShowResults(false);
    
    // Add authentication token to the request
    const enrichedQueryData = {
      ...queryData,
      authToken: authState.token
    };
    
    await analyzeQuery(enrichedQueryData);
  };

  const handleReset = () => {
    setShowResults(false);
    resetAnalysis();
  };

  // Check for existing authentication on app load
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedUsername = localStorage.getItem('username');
    
    if (storedToken && storedUsername) {
      setAuthState({
        authenticated: true,
        token: storedToken,
        username: storedUsername
      });
    }
  }, []);

  // Show login screen if not authenticated
  if (!authState.authenticated) {
    return (
      <>
        <GlobalStyle />
        <LoginScreen onLogin={handleLogin} />
      </>
    );
  }

  // Show main application if authenticated
  return (
    <>
      <GlobalStyle />
      <AppContainer>
        <Header
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <WelcomeMessage>
            👋 Welcome back, {authState.username}!
          </WelcomeMessage>
          
          <LogoutButton
            onClick={handleLogout}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Sign Out
          </LogoutButton>

          <Title>🤖 AI Financial Advisor</Title>
          <Subtitle>Multi-Agent Financial Intelligence on Google Kubernetes Engine</Subtitle>
          <Subtitle className="tech-stack">
            Powered by ADK • Vertex AI • MCP Protocol • A2A Communication
          </Subtitle>
        </Header>

        <MainGrid>
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <FinancialQueryInterface 
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              onReset={handleReset}
              authToken={authState.token}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <AgentStatusDashboard agentStatuses={agentStatuses} />
          </motion.div>
        </MainGrid>

        <AnimatePresence>
          {isLoading && (
            <LoadingSection
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3 }}
            >
              <Spinner
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              <LoadingText>
                AI agents are collaborating via A2A protocol to analyze your financial situation...
              </LoadingText>
            </LoadingSection>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showResults && results && (
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.5 }}
            >
              <ResultsDisplay results={results} />
            </motion.div>
          )}
        </AnimatePresence>
      </AppContainer>
    </>
  );
}

export default App;
