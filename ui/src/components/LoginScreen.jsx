// ui/src/components/LoginScreen.jsx - Bank of Anthos style login
import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { User, Lock, LogIn } from 'lucide-react';

const LoginContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const LoginCard = styled(motion.div)`
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  overflow: hidden;
`;

const Header = styled.div`
  background: white;
  padding: 30px 40px 20px;
  border-bottom: 1px solid #e0e0e0;
`;

const BankTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 400;
  color: #333;
  margin: 0;
  letter-spacing: 0.5px;
`;

const LoginForm = styled.div`
  padding: 40px;
`;

const WelcomeSection = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const WelcomeText = styled.div`
  color: #888;
  font-size: 0.9rem;
  font-weight: 400;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 8px;
`;

const SignInTitle = styled.h2`
  color: #333;
  font-size: 1.8rem;
  font-weight: 300;
  margin: 0;
  letter-spacing: 0.5px;
`;

const FormGroup = styled.div`
  margin-bottom: 25px;
`;

const Label = styled.label`
  display: block;
  color: #888;
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 8px;
`;

const InputContainer = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const InputIcon = styled.div`
  position: absolute;
  left: 0;
  color: #4caf50;
  z-index: 1;
  padding: 0 4px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 0 12px 30px;
  border: none;
  border-bottom: 1px solid #ddd;
  background: transparent;
  font-size: 1rem;
  color: #333;
  outline: none;
  transition: border-color 0.3s ease;

  &:focus {
    border-bottom-color: #4caf50;
  }

  &::placeholder {
    color: #999;
  }

  /* For password field with dots */
  &.password-field {
    font-family: monospace;
    font-size: 1.2rem;
    letter-spacing: 2px;
    color: #333;
  }
`;

const SignInButton = styled(motion.button)`
  width: 100%;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 15px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 30px;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: #45a049;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled(motion.div)`
  background: #ffebee;
  color: #c62828;
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 15px;
  font-size: 0.9rem;
  border-left: 4px solid #c62828;
`;

const LoadingSpinner = styled(motion.div)`
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
`;

const PoweredBy = styled.div`
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  color: #999;
  font-size: 0.8rem;
`;

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('testuser');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Fixed password for demo (matches Bank of Anthos)
  const demoPassword = 'bankofanthos';

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      // Call the authentication API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: demoPassword
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          // Pass the JWT token and user info to parent
          onLogin({
            token: data.token,
            username: username.trim(),
            authenticated: true
          });
        } else {
          setError(data.message || 'Login failed');
        }
      } else {
        setError('Network error. Please try again.');
      }
    } catch (err) {
      setError('Unable to connect to authentication service');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Header>
          <BankTitle>Bank of Anthos</BankTitle>
        </Header>

        <LoginForm>
          <WelcomeSection>
            <WelcomeText>Welcome</WelcomeText>
            <SignInTitle>SIGN IN</SignInTitle>
          </WelcomeSection>

          <form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="username">Username</Label>
              <InputContainer>
                <InputIcon>
                  <User size={16} />
                </InputIcon>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="testuser"
                  disabled={isLoading}
                />
              </InputContainer>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="password">Password</Label>
              <InputContainer>
                <InputIcon>
                  <Lock size={16} />
                </InputIcon>
                <Input
                  id="password"
                  type="text"
                  value="••••••••••••"
                  className="password-field"
                  readOnly
                  title="Demo password: bankofanthos"
                />
              </InputContainer>
            </FormGroup>

            {error && (
              <ErrorMessage
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {error}
              </ErrorMessage>
            )}

            <SignInButton
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: isLoading ? 1 : 1.02 }}
              whileTap={{ scale: isLoading ? 1 : 0.98 }}
            >
              {isLoading ? (
                <>
                  <LoadingSpinner
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  />
                  Signing In...
                </>
              ) : (
                <>
                  <LogIn size={18} />
                  Sign In
                </>
              )}
            </SignInButton>
          </form>

          <PoweredBy>
            🤖 AI Financial Advisor powered by GKE • ADK • MCP • Vertex AI
          </PoweredBy>
        </LoginForm>
      </LoginCard>
    </LoginContainer>
  );
}

export default LoginScreen;
