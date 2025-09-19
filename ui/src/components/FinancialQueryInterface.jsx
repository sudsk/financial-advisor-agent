// ui/src/components/FinancialQueryInterface.jsx - Enhanced with better quick scenarios
import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Send, RefreshCw } from 'lucide-react';

const Container = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
`;

const Title = styled.h3`
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.4em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const InputGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
  font-size: 0.95em;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    transform: translateY(-1px);
  }

  &::placeholder {
    color: #aaa;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
  max-height: 200px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    transform: translateY(-1px);
  }

  &::placeholder {
    color: #aaa;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 20px;
`;

const AnalyzeButton = styled(motion.button)`
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }
`;

const ResetButton = styled(motion.button)`
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  color: white;
  border: none;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3);
  }
`;

const ErrorMessage = styled(motion.div)`
  background: #f8d7da;
  color: #721c24;
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
  margin-top: 10px;
  font-weight: 500;
`;

const QuickScenariosSection = styled.div`
  margin-top: 25px;
  padding-top: 20px;
  border-top: 2px solid #e1e8ed;
`;

const QuickScenariosTitle = styled(Label)`
  margin-bottom: 12px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
`;

const ScenariosGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 12px;
`;

const ScenarioButton = styled(motion.button)`
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
  }

  &:hover:not(:disabled)::before {
    left: 100%;
  }

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(23, 162, 184, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const HelpText = styled.div`
  margin-top: 15px;
  padding: 12px 15px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  border-left: 4px solid #17a2b8;
  font-size: 0.85rem;
  color: #495057;
  line-height: 1.4;
`;

function FinancialQueryInterface({ onAnalyze, isLoading, onReset }) {
  const [formData, setFormData] = useState({
    userId: 'testuser',
    accountId: '1234567890',
    query: "Help me save $80,000 for a house down payment in 3 years. I currently spend about $4,500 per month."
  });
  
  const [error, setError] = useState('');

  // Quick scenario templates
  const scenarios = {
    house: "Help me save $80,000 for a house down payment in 3 years. I currently spend about $4,500 per month.",
    retirement: "I'm 35 years old and want to retire comfortably at 60. What's my best investment strategy?",
    debt: "I have $15,000 in credit card debt at 18% interest. How should I pay this off while still saving?",
    investment: "I have $25,000 to invest and want to balance growth with safety. What do you recommend?"
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.userId.trim() || !formData.accountId.trim() || !formData.query.trim()) {
      setError('Please fill in all fields');
      return;
    }
    
    setError('');
    
    try {
      await onAnalyze({
        user_id: formData.userId.trim(),
        account_id: formData.accountId.trim(),
        query: formData.query.trim()
      });
    } catch (err) {
      setError('Failed to analyze query. Please try again.');
    }
  };

  const handleReset = () => {
    setError('');
    onReset();
  };

  const loadScenario = (scenarioKey) => {
    if (scenarios[scenarioKey]) {
      setFormData(prev => ({
        ...prev,
        query: scenarios[scenarioKey]
      }));
      setError(''); // Clear any existing errors
    }
  };

  return (
    <Container
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Title>💬 Ask Your Financial Question</Title>
      
      <form onSubmit={handleSubmit}>
        <InputGroup>
          <Label htmlFor="userId">User ID</Label>
          <Input
            id="userId"
            name="userId"
            type="text"
            value={formData.userId}
            onChange={handleInputChange}
            placeholder="Enter user ID"
            disabled={isLoading}
          />
        </InputGroup>

        <InputGroup>
          <Label htmlFor="accountId">Account ID</Label>
          <Input
            id="accountId"
            name="accountId"
            type="text"
            value={formData.accountId}
            onChange={handleInputChange}
            placeholder="Enter account ID"
            disabled={isLoading}
          />
        </InputGroup>

        <InputGroup>
          <Label htmlFor="query">Your Financial Question</Label>
          <TextArea
            id="query"
            name="query"
            value={formData.query}
            onChange={handleInputChange}
            placeholder="e.g., Help me save $80,000 for a house down payment in 3 years"
            disabled={isLoading}
          />
        </InputGroup>

        {error && (
          <ErrorMessage
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {error}
          </ErrorMessage>
        )}

        <ButtonContainer>
          <AnalyzeButton
            type="submit"
            disabled={isLoading}
            whileHover={{ scale: isLoading ? 1 : 1.02 }}
            whileTap={{ scale: isLoading ? 1 : 0.98 }}
          >
            {isLoading ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <RefreshCw size={18} />
                </motion.div>
                Analyzing...
              </>
            ) : (
              <>
                <Send size={18} />
                Analyze with AI Agents
              </>
            )}
          </AnalyzeButton>

          <ResetButton
            type="button"
            onClick={handleReset}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <RefreshCw size={18} />
          </ResetButton>
        </ButtonContainer>
      </form>

      {/* Quick Scenarios Section - Enhanced */}
      <QuickScenariosSection>
        <QuickScenariosTitle>Quick Scenarios:</QuickScenariosTitle>
        <ScenariosGrid>
          <ScenarioButton
            type="button"
            onClick={() => loadScenario('house')}
            disabled={isLoading}
            whileHover={{ scale: isLoading ? 1 : 1.05 }}
            whileTap={{ scale: isLoading ? 1 : 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            🏠 House
          </ScenarioButton>
          
          <ScenarioButton
            type="button"
            onClick={() => loadScenario('retirement')}
            disabled={isLoading}
            whileHover={{ scale: isLoading ? 1 : 1.05 }}
            whileTap={{ scale: isLoading ? 1 : 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            🏖️ Retirement
          </ScenarioButton>
          
          <ScenarioButton
            type="button"
            onClick={() => loadScenario('debt')}
            disabled={isLoading}
            whileHover={{ scale: isLoading ? 1 : 1.05 }}
            whileTap={{ scale: isLoading ? 1 : 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            💳 Debt
          </ScenarioButton>
          
          <ScenarioButton
            type="button"
            onClick={() => loadScenario('investment')}
            disabled={isLoading}
            whileHover={{ scale: isLoading ? 1 : 1.05 }}
            whileTap={{ scale: isLoading ? 1 : 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            💼 Investment
          </ScenarioButton>
        </ScenariosGrid>
        
        <HelpText>
          💡 <strong>Tip:</strong> Click any scenario above to load a sample question, then customize it with your specific situation and amounts.
        </HelpText>
      </QuickScenariosSection>
    </Container>
  );
}

export default FinancialQueryInterface;
