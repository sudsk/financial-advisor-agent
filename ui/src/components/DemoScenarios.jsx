// ui/src/components/DemoScenarios.jsx
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Play, Home, Briefcase, CreditCard, PieChart, Info } from 'lucide-react';

const Container = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  margin-top: 30px;
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

const ButtonsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const DemoButton = styled(motion.button)`
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  padding: 15px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95em;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
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

  &:hover::before {
    left: 100%;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(23, 162, 184, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
`;

const ButtonContent = styled.div`
  flex: 1;
`;

const ButtonTitle = styled.div`
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 1em;
`;

const ButtonDescription = styled.div`
  font-size: 0.85em;
  opacity: 0.9;
  line-height: 1.3;
`;

const ArchitectureInfo = styled(motion.div)`
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #17a2b8;
  margin-top: 20px;
`;

const ArchitectureTitle = styled.div`
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TechGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
`;

const TechItem = styled(motion.div)`
  background: rgba(255, 255, 255, 0.8);
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: #17a2b8;
  }
`;

const TechLabel = styled.div`
  font-weight: 600;
  color: #17a2b8;
  font-size: 0.9em;
  margin-bottom: 4px;
`;

const TechDescription = styled.div`
  color: #6c757d;
  font-size: 0.85em;
  line-height: 1.3;
`;

const scenarios = [
  {
    key: 'house',
    icon: Home,
    title: 'Save for House Down Payment',
    description: 'Plan to save $80k in 3 years with current spending analysis',
    query: "Help me save $80,000 for a house down payment in 3 years. I currently spend about $4,500 per month."
  },
  {
    key: 'retirement',
    icon: Briefcase,
    title: 'Retirement Planning Strategy',
    description: 'Long-term wealth building from age 35 to comfortable retirement',
    query: "I'm 35 years old and want to retire comfortably at 60. What's my best investment strategy?"
  },
  {
    key: 'debt',
    icon: CreditCard,
    title: 'Debt Optimization Plan',
    description: 'Eliminate high-interest debt while maintaining emergency savings',
    query: "I have $15,000 in credit card debt at 18% interest. How should I pay this off while still saving?"
  },
  {
    key: 'investment',
    icon: PieChart,
    title: 'Investment Portfolio Strategy',
    description: 'Balance growth and safety with diversified investment approach',
    query: "I have $25,000 to invest and want to balance growth with safety. What do you recommend?"
  }
];

const techStack = [
  {
    label: 'ADK (Agent Development Kit)',
    description: 'Agent lifecycle management and coordination framework'
  },
  {
    label: 'MCP (Model Context Protocol)',
    description: 'Seamless integration with Bank of Anthos APIs'
  },
  {
    label: 'A2A (Agent-to-Agent)',
    description: 'Inter-agent communication and coordination protocol'
  },
  {
    label: 'Vertex AI Gemini',
    description: 'Advanced natural language processing and analysis'
  },
  {
    label: 'GKE Autopilot',
    description: 'Auto-scaling Kubernetes container orchestration'
  },
  {
    label: 'Workload Identity',
    description: 'Secure authentication without API key management'
  }
];

function DemoScenarios({ onLoadScenario }) {
  const handleScenarioClick = (scenario) => {
    if (onLoadScenario) {
      onLoadScenario(scenario.query);
    } else {
      // Fallback: trigger custom event that the parent can listen to
      const event = new CustomEvent('loadDemoScenario', { 
        detail: { query: scenario.query, key: scenario.key } 
      });
      window.dispatchEvent(event);
    }
  };

  return (
    <Container
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
    >
      <Title>
        <Play size={24} />
        Demo Scenarios
      </Title>
      
      <ButtonsContainer>
        {scenarios.map((scenario, index) => {
          const IconComponent = scenario.icon;
          
          return (
            <DemoButton
              key={scenario.key}
              onClick={() => handleScenarioClick(scenario)}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <IconComponent size={24} />
              <ButtonContent>
                <ButtonTitle>{scenario.title}</ButtonTitle>
                <ButtonDescription>{scenario.description}</ButtonDescription>
              </ButtonContent>
            </DemoButton>
          );
        })}
      </ButtonsContainer>

      <ArchitectureInfo
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <ArchitectureTitle>
          <Info size={20} />
          GKE Hackathon Architecture
        </ArchitectureTitle>
        
        <TechGrid>
          {techStack.map((tech, index) => (
            <TechItem
              key={tech.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <TechLabel>{tech.label}</TechLabel>
              <TechDescription>{tech.description}</TechDescription>
            </TechItem>
          ))}
        </TechGrid>
        
        <motion.div
          style={{
            marginTop: '15px',
            padding: '12px 15px',
            background: 'rgba(23, 162, 184, 0.1)',
            borderRadius: '8px',
            color: '#0c5460',
            fontSize: '0.9em',
            fontWeight: '500',
            textAlign: 'center'
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          🏆 Built for the Google Kubernetes Engine 10th Anniversary Hackathon
        </motion.div>
      </ArchitectureInfo>
    </Container>
  );
}

export default DemoScenarios;
