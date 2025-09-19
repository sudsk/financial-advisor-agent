// ui/src/components/AgentStatusDashboard.jsx - Enhanced with processing highlights
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

// Enhanced pulse animation for active processing
{/*const activePulse = keyframes`
  0% { 
    transform: scale(1);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1), 0 0 0 0 rgba(255, 193, 7, 0.7);
  }
  50% { 
    transform: scale(1.02);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15), 0 0 0 8px rgba(255, 193, 7, 0.3);
  }
  100% { 
    transform: scale(1);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1), 0 0 0 0 rgba(255, 193, 7, 0.7);
  }
`;*/}

// Glowing border animation for processing
{/*const glowBorder = keyframes`
  0% { border-color: #ffc107; }
  25% { border-color: #fd7e14; }
  50% { border-color: #ffc107; }
  75% { border-color: #fd7e14; }
  100% { border-color: #ffc107; }
`;*/}

// Shimmer effect for processing cards
{/*const shimmer = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
`;*/}

const AgentCard = styled(motion.div)`
  background: ${props => {
    if (props.$status === 'processing') return 'linear-gradient(135deg, #fff3cd, #ffeaa7)';
    if (props.$status === 'active') return 'linear-gradient(135deg, #d4edda, #c3e6cb)';
    return '#f8f9fa';
  }};
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 3px solid ${props => {
    if (props.$status === 'processing') return '#ffc107';
    if (props.$status === 'active') return '#28a745';
    return '#e1e8ed';
  }};
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;

  /* Enhanced processing state styling */
  {/*${props => props.$status === 'processing' && `
    animation: ${activePulse} 1.5s infinite;
    border-animation: ${glowBorder} 2s infinite;
    z-index: 10;
    
    /* Add shimmer effect overlay for processing */
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.6),
        transparent
      );
      background-size: 200px 100%;
      animation: ${shimmer} 2s infinite;
      pointer-events: none;
    }
  `}*/}

  /* Regular hover effects for non-processing states */
  ${props => props.$status !== 'processing' && `
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
  `}
`;

const AgentIcon = styled.div`
  font-size: 2.5em;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 2;
  color: ${props => {
    if (props.$status === 'processing') return '#fd7e14';
    if (props.$status === 'active') return '#28a745';
    return '#6c757d';
  }};

  /* Add subtle glow for processing icons */
  ${props => props.$status === 'processing' && `
    filter: drop-shadow(0 0 8px rgba(253, 126, 20, 0.6));
  `}
`;

const AgentName = styled.div`
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
  font-size: 1.1em;
  position: relative;
  z-index: 2;
`;

const AgentStatusText = styled.div`
  font-size: 0.9em;
  color: #666;
  font-weight: 500;
  position: relative;
  z-index: 2;
  
  /* Make processing status text more prominent */
  ${props => props.$status === 'processing' && `
    color: #856404;
    font-weight: 600;
    text-shadow: 0 0 4px rgba(133, 100, 4, 0.3);
  `}
`;

const StatusIndicator = styled(motion.div)`
  position: absolute;
  top: 8px;
  right: 8px;
  width: ${props => props.$status === 'processing' ? '14px' : '12px'};
  height: ${props => props.$status === 'processing' ? '14px' : '12px'};
  border-radius: 50%;
  background: ${props => {
    if (props.$status === 'processing') return '#fd7e14';
    if (props.$status === 'active') return '#28a745';
    return '#6c757d';
  }};
  box-shadow: ${props => 
    props.$status === 'processing' 
      ? '0 0 12px rgba(253, 126, 20, 0.8)' 
      : '0 0 8px rgba(0, 0, 0, 0.3)'
  };
  z-index: 3;
`;

const PerformanceMetrics = styled.div`
  margin-top: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  font-size: 0.8em;
  position: relative;
  z-index: 2;
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  color: #555;
`;

// Processing progress bar for active agents
const ProcessingProgressBar = styled(motion.div)`
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #ffc107, #fd7e14, #ffc107);
  background-size: 200% 100%;
  border-radius: 0 0 12px 12px;
  z-index: 1;
`;

{/*const progressAnimation = keyframes`
  0% {
    width: 0%;
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    width: 100%;
    background-position: 0% 50%;
  }
`;*/} 

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
              whileHover={status.status !== 'processing' ? { scale: 1.02 } : {}}
              whileTap={status.status !== 'processing' ? { scale: 0.98 } : {}}
            >
              <StatusIndicator
                $status={status.status}
                animate={status.status === 'processing' ? {
                  scale: [1, 1.3, 1],
                  opacity: [1, 0.6, 1]
                } : {}}
                transition={{ 
                  duration: status.status === 'processing' ? 1 : 0.5, 
                  repeat: status.status === 'processing' ? Infinity : 0 
                }}
              />
              
              <AgentIcon $status={status.status}>
                <motion.div
                  animate={status.status === 'processing' ? {
                    rotate: [0, 10, -10, 0],
                    scale: [1, 1.1, 1]
                  } : {}}
                  transition={{ 
                    duration: 2, 
                    repeat: status.status === 'processing' ? Infinity : 0,
                    repeatType: 'reverse'
                  }}
                >
                  <IconComponent size={40} />
                </motion.div>
              </AgentIcon>
              
              <AgentName>{agent.name}</AgentName>
              <AgentStatusText $status={status.status}>
                {status.statusText}
                {status.status === 'processing' && (
                  <motion.span
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                    style={{ marginLeft: '4px' }}
                  >
                    ⚡
                  </motion.span>
                )}
              </AgentStatusText>
              
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
                <ProcessingProgressBar
                  initial={{ width: '0%' }}
                  animate={{ 
                    width: '100%',
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                  }}
                  transition={{ 
                    width: { duration: 2, repeat: Infinity },
                    backgroundPosition: { duration: 1.5, repeat: Infinity }
                  }}
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
        <br />
        <small style={{ opacity: 0.8 }}>
          💡 Processing agents are highlighted with enhanced visual effects
        </small>
      </motion.div>
    </Container>
  );
}

export default AgentStatusDashboard;
