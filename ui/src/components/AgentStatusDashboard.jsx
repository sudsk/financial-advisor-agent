// ui/src/components/AgentStatusDashboard.jsx - Simplified with clear processing indicators
import React from 'react';
import styled from 'styled-components';
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

const AgentCard = styled(motion.div)`
  background: ${props => {
    if (props.$status === 'processing') return 'linear-gradient(135deg, #fff3cd, #ffeaa7)';
    if (props.$status === 'active') return 'linear-gradient(135deg, #d4edda, #c3e6cb)';
    return 'linear-gradient(135deg, #f8f9fa, #e9ecef)';
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

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
`;

const AgentIcon = styled.div`
  font-size: 2.5em;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${props => {
    if (props.$status === 'processing') return '#fd7e14';
    if (props.$status === 'active') return '#28a745';
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
  color: ${props => {
    if (props.$status === 'processing') return '#856404';
    if (props.$status === 'active') return '#155724';
    return '#666';
  }};
  font-weight: ${props => props.$status === 'processing' ? '600' : '500'};
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
      : '0 0 6px rgba(0, 0, 0, 0.3)'
  };
`;

const ProcessingBadge = styled(motion.div)`
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  background: #fd7e14;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(253, 126, 20, 0.4);
`;

const PerformanceMetrics = styled.div`
  margin-top: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  font-size: 0.8em;
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  color: #555;
`;

const TechInfo = styled(motion.div)`
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  font-size: 0.9em;
  color: #555;
  text-align: center;
`;

// Simple pulse animation for processing status
const pulseAnimation = {
  scale: [1, 1.05, 1],
  transition: {
    duration: 1.5,
    repeat: Infinity,
    ease: "easeInOut"
  }
};

// Simple glow animation for status indicator
const glowAnimation = {
  scale: [1, 1.3, 1],
  opacity: [1, 0.7, 1],
  transition: {
    duration: 1,
    repeat: Infinity,
    ease: "easeInOut"
  }
};

function AgentStatusDashboard({ agentStatuses }) {
  console.log(`📊 DASHBOARD RECEIVED:`, agentStatuses); // DEBUG

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
    const status = agentStatuses[agentId] || { status: 'ready', statusText: 'Ready', confidence: 0 };
    console.log(`🤖 AGENT ${agentId} STATUS:`, status); // DEBUG
    return status;
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
          
          console.log(`🎨 RENDERING ${agent.id} with status: ${status.status}`); // DEBUG
          
          return (
            <AgentCard
              key={agent.id}
              $status={status.status}
              initial={{ opacity: 0, y: 20 }}
              animate={{ 
                opacity: 1, 
                y: 0,
                ...(status.status === 'processing' ? pulseAnimation : {})
              }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              {status.status === 'processing' && (
                <ProcessingBadge
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  Processing
                </ProcessingBadge>
              )}
              
              <StatusIndicator
                $status={status.status}
                animate={status.status === 'processing' ? glowAnimation : {}}
              />
              
              <AgentIcon $status={status.status}>
                <motion.div
                  animate={status.status === 'processing' ? {
                    rotate: [0, 5, -5, 0],
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
            </AgentCard>
          );
        })}
      </AgentsGrid>
      
      <TechInfo
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <strong>🔗 Architecture:</strong> ADK coordination • MCP integration • A2A protocol • Vertex AI Gemini
        <br />
        <small style={{ opacity: 0.8 }}>
          💡 Watch agents light up as they process your financial query in real-time
        </small>
      </TechInfo>
    </Container>
  );
}

export default AgentStatusDashboard;
