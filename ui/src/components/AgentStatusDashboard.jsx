// ui/src/components/AgentStatusDashboard.jsx
import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import { Target, DollarSign, TrendingUp, Shield, Activity } from 'lucide-react';

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

const AgentsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
`;

const pulse = keyframes`
  0%, 100% { 
    transform: scale(1); 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  50% { 
    transform: scale(1.05); 
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
`;

const shimmer = keyframes`
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
`;

const AgentCard = styled(motion.div)`
  background: ${props => {
    if (props.$status === 'active') return 'linear-gradient(135deg, #d4edda, #c3e6cb)';
    if (props.$status === 'processing') return 'linear-gradient(135deg, #fff3cd, #ffeaa7)';
    return '#f8f9fa';
  }};
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 3px solid ${props => {
    if (props.$status === 'active') return '#28a745';
    if (props.$status === 'processing') return '#ffc107';
    return '#e1e8ed';
  }};
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;

  ${props => props.$status === 'processing' && `
    animation: ${pulse} 1.5s infinite;
  `}

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    transition: left 0.5s;
  }

  &:hover::before {
    animation: ${shimmer} 0.5s ease-out;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  }
`;

const AgentIcon = styled.div`
  font-size: 2.5em;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${props => {
    if (props.$status === 'active') return '#28a745';
    if (props.$status === 'processing') return '#ffc107';
    return '#6c757d';
  }};
`;

const AgentName = styled.div`
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
  font-size: 1.1em;
`;

const AgentStatusText = styled.div`
  font-size: 0.9em;
  color: #666;
  font-weight: 500;
`;

const StatusIndicator = styled(motion.div)`
  position: absolute;
  top: 8px;
  right: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => {
    if (props.$status === 'active') return '#28a745';
    if (props.$status === 'processing') return '#ffc107';
    return '#6c757d';
  }};
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
`;

const PerformanceMetrics = styled.div`
  margin-top: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  font-size: 0.8em;
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  color: #555;
`;

function AgentStatusDashboard({ agentStatuses }) {
  const agents = [
    {
      id: 'coordinator',
      name: 'Coordinator',
      icon: Target,
      description: 'ADK Orchestration',
      capabilities: ['Query Analysis', 'Agent Coordination', 'Response Synthesis']
    },
    {
      id: 'budget',
      name: 'Budget Agent',
      icon: DollarSign,
      description: 'Spending Analysis',
      capabilities: ['Transaction Analysis', 'Budget Optimization', 'Savings Planning']
    },
    {
      id: 'investment',
      name: 'Investment Agent',
      icon: TrendingUp,
      description: 'Portfolio Strategy',
      capabilities: ['Risk Assessment', 'Portfolio Design', 'Market Analysis']
    },
    {
      id: 'security',
      name: 'Security Agent',
      icon: Shield,
      description: 'Risk Assessment',
      capabilities: ['Fraud Detection', 'Financial Health', 'Security Monitoring']
    }
  ];

  const getAgentStatus = (agentId) => {
    return agentStatuses[agentId] || { status: 'ready', statusText: 'Ready', confidence: 0 };
  };

  return (
    <Container
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Title>
        <Activity size={24} />
        Agent Coordination Status
      </Title>
      
      <AgentsGrid>
        {agents.map((agent, index) => {
          const status = getAgentStatus(agent.id);
          const IconComponent = agent.icon;
          
          return (
            <AgentCard
              key={agent.id}
              $status={status.status}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <StatusIndicator
                $status={status.status}
                animate={status.status === 'processing' ? {
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.7, 1]
                } : {}}
                transition={{ duration: 1, repeat: status.status === 'processing' ? Infinity : 0 }}
              />
              
              <AgentIcon $status={status.status}>
                <IconComponent size={40} />
              </AgentIcon>
              
              <AgentName>{agent.name}</AgentName>
              <AgentStatusText>{status.statusText}</AgentStatusText>
              
              {status.confidence > 0 && (
                <PerformanceMetrics>
                  <MetricRow>
                    <span>Confidence:</span>
                    <span>{Math.round(status.confidence * 100)}%</span>
                  </MetricRow>
                  <MetricRow>
                    <span>Capabilities:</span>
                    <span>{agent.capabilities.length}</span>
                  </MetricRow>
                </PerformanceMetrics>
              )}
              
              {status.status === 'processing' && (
                <motion.div
                  style={{
                    position: 'absolute',
                    bottom: '0',
                    left: '0',
                    height: '3px',
                    background: 'linear-gradient(90deg, #ffc107, #fd7e14)',
                    borderRadius: '0 0 12px 12px'
                  }}
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </AgentCard>
          );
        })}
      </AgentsGrid>
      
      <motion.div
        style={{
          marginTop: '20px',
          padding: '15px',
          background: 'linear-gradient(135deg, #f8f9fa, #e9ecef)',
          borderRadius: '8px',
          fontSize: '0.9em',
          color: '#555'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <strong>🔗 Architecture:</strong> ADK coordination • MCP integration • A2A protocol • Vertex AI Gemini
      </motion.div>
    </Container>
  );
}

export default AgentStatusDashboard;
