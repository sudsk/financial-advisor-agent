// ui/src/components/AgentStatusDashboard.jsx - Simplified with clear processing indicators
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Target, DollarSign, TrendingUp, Shield, Activity } from 'lucide-react';

const Container = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 18px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  min-height: 180px;
`;

const Title = styled.h3`
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.2em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const AgentsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
`;

const AgentCard = styled(motion.div)`
  background: ${props => {
    if (props.$status === 'processing') return 'linear-gradient(135deg, #fff3cd, #ffeaa7)';
    if (props.$status === 'active') return 'linear-gradient(135deg, #d4edda, #c3e6cb)';
    return 'linear-gradient(135deg, #f8f9fa, #e9ecef)';
  }};
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 2px solid ${props => {
    if (props.$status === 'processing') return '#ffc107';
    if (props.$status === 'active') return '#28a745';
    return '#e1e8ed';
  }};
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  }
`;

const AgentIcon = styled.div`
  font-size: 1.6em;
  margin-bottom: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${props => {
    if (props.$status === 'processing') return '#fd7e14';
    if (props.$status === 'active') return '#28a745';
    return '#6c757d';
  }};
  flex-shrink: 0;
`;

const AgentName = styled.div`
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 2px;
  font-size: 0.9em;
  flex-shrink: 0;
`;

const AgentStatusText = styled.div`
  font-size: 0.75em;
  color: ${props => {
    if (props.$status === 'processing') return '#856404';
    if (props.$status === 'active') return '#155724';
    return '#666';
  }};
  font-weight: ${props => props.$status === 'processing' ? '600' : '500'};
  line-height: 1.2;
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StatusIndicator = styled(motion.div)`
  position: absolute;
  top: 6px;
  right: 6px;
  width: ${props => props.$status === 'processing' ? '12px' : '10px'};
  height: ${props => props.$status === 'processing' ? '12px' : '10px'};
  border-radius: 50%;
  background: ${props => {
    if (props.$status === 'processing') return '#fd7e14';
    if (props.$status === 'active') return '#28a745';
    return '#6c757d';
  }};
  box-shadow: ${props => 
    props.$status === 'processing' 
      ? '0 0 8px rgba(253, 126, 20, 0.8)' 
      : '0 0 4px rgba(0, 0, 0, 0.3)'
  };
`;

const ProcessingBadge = styled(motion.div)`
  position: absolute;
  top: -3px;
  left: 50%;
  transform: translateX(-50%);
  background: #fd7e14;
  color: white;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 0.6em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 1px 4px rgba(253, 126, 20, 0.4);
`;

const PerformanceMetrics = styled.div`
  margin-top: 6px;
  padding: 6px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  font-size: 0.7em;
  flex-shrink: 0;
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
              
              {/* Top section with icon and name */}
              <div>
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
                    <IconComponent size={26} />
                  </motion.div>
                </AgentIcon>
                
                <AgentName>{agent.name}</AgentName>
              </div>
              
              {/* Middle section with status text */}
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
            </AgentCard>
          );
        })}
      </AgentsGrid>
      
    </Container>
  );
}

export default AgentStatusDashboard;
