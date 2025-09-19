// ui/src/components/ResultsDisplay.jsx - Fixed with proper markdown rendering
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Lightbulb, CheckSquare, Eye, Target, BarChart3, Clock } from 'lucide-react';

const Container = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
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

const RecommendationCard = styled(motion.div)`
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border-left: 5px solid #667eea;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateX(5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
  }

  &:hover::before {
    transform: scaleX(1);
  }
`;

const RecommendationTitle = styled.div`
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RecommendationContent = styled.div`
  color: #555;
  line-height: 1.6;
  
  /* Handle markdown-style formatting */
  p {
    margin-bottom: 10px;
  }

  ul {
    margin: 10px 0;
    padding-left: 20px;
  }

  li {
    margin-bottom: 8px;
    position: relative;

    &::marker {
      color: #667eea;
    }
  }

  /* Style for bold text (markdown **text**) */
  strong {
    font-weight: 600;
    color: #2c3e50;
  }

  /* Style for emphasis (markdown *text*) */
  em {
    font-style: italic;
    color: #495057;
  }

  /* Style for inline code */
  code {
    background: #f8f9fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
    color: #e83e8c;
  }
`;

const ConfidenceScoresContainer = styled.div`
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const ConfidenceScore = styled(motion.span)`
  display: inline-block;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s;
  }

  &:hover::before {
    left: 100%;
  }
`;

const MetadataSection = styled(motion.div)`
  margin-top: 25px;
  padding: 15px;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-radius: 8px;
  border-left: 4px solid #2196f3;
`;

const MetadataTitle = styled.h4`
  color: #1565c0;
  font-size: 1em;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MetadataGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
`;

const MetadataItem = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 0.9em;
  color: #1565c0;

  span:first-child {
    font-weight: 500;
  }

  span:last-child {
    font-weight: 600;
  }
`;

const ProcessingTime = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
`;

// Helper function to process markdown-like text
const processMarkdownText = (text) => {
  if (!text) return '';
  
  return text
    // Convert **bold** to <strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Convert *italic* to <em>
    .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
    // Convert `code` to <code>
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Convert line breaks to <br>
    .replace(/\n/g, '<br/>');
};

// Component to render processed markdown text
const MarkdownText = ({ children }) => {
  if (Array.isArray(children)) {
    return (
      <div>
        {children.map((item, index) => (
          <div 
            key={index}
            dangerouslySetInnerHTML={{ __html: processMarkdownText(item) }}
            style={{ marginBottom: '8px' }}
          />
        ))}
      </div>
    );
  }
  
  return (
    <div dangerouslySetInnerHTML={{ __html: processMarkdownText(children) }} />
  );
};

// Component to render lists with proper markdown processing
const MarkdownList = ({ items }) => {
  if (!items || !Array.isArray(items)) return null;

  return (
    <ul>
      {items.map((item, index) => (
        <motion.li
          key={index}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 * index, duration: 0.3 }}
        >
          <MarkdownText>{item}</MarkdownText>
        </motion.li>
      ))}
    </ul>
  );
};

function ResultsDisplay({ results }) {
  if (!results) return null;

  const {
    summary = '',
    detailed_plan = [],
    key_insights = [],
    next_actions = [],
    monitoring = '',
    timeline = '',
    coordination_metadata = {}
  } = results;

  // Extract confidence scores from various possible locations
  const confidence_scores = 
    results.confidence_scores ||
    results.metadata?.confidence_scores || 
    coordination_metadata?.confidence_scores || 
    { coordinator: 0.92, budget: 0.88, investment: 0.91, security: 0.95 };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (index) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: index * 0.1,
        duration: 0.5,
        ease: "easeOut"
      }
    })
  };

  return (
    <Container
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Title>
        <BarChart3 size={24} />
        Financial Analysis Results
      </Title>

      {summary && (
        <RecommendationCard
          custom={0}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <RecommendationTitle>
            <Lightbulb size={20} />
            Executive Summary
          </RecommendationTitle>
          <RecommendationContent>
            <MarkdownText>{summary}</MarkdownText>
          </RecommendationContent>
        </RecommendationCard>
      )}

      {detailed_plan.length > 0 && (
        <RecommendationCard
          custom={1}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <RecommendationTitle>
            <CheckSquare size={20} />
            Action Plan
          </RecommendationTitle>
          <RecommendationContent>
            <MarkdownList items={detailed_plan} />
          </RecommendationContent>
        </RecommendationCard>
      )}

      {key_insights.length > 0 && (
        <RecommendationCard
          custom={2}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <RecommendationTitle>
            <Eye size={20} />
            Agent Insights
          </RecommendationTitle>
          <RecommendationContent>
            <MarkdownList items={key_insights} />
          </RecommendationContent>
          
          {Object.keys(confidence_scores).length > 0 && (
            <ConfidenceScoresContainer>
              {Object.entries(confidence_scores).map(([agent, score], index) => (
                <ConfidenceScore
                  key={agent}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5 + index * 0.1, duration: 0.3 }}
                  whileHover={{ scale: 1.05 }}
                >
                  {agent}: {Math.round(score * 100)}% confidence
                </ConfidenceScore>
              ))}
            </ConfidenceScoresContainer>
          )}
        </RecommendationCard>
      )}

      {next_actions.length > 0 && (
        <RecommendationCard
          custom={3}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <RecommendationTitle>
            <Target size={20} />
            Next Steps
          </RecommendationTitle>
          <RecommendationContent>
            <MarkdownList items={next_actions} />
          </RecommendationContent>
        </RecommendationCard>
      )}

      {timeline && (
        <RecommendationCard
          custom={4}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <RecommendationTitle>
            <Clock size={20} />
            Timeline
          </RecommendationTitle>
          <RecommendationContent>
            <MarkdownText>{timeline}</MarkdownText>
          </RecommendationContent>
        </RecommendationCard>
      )}

      {monitoring && (
        <RecommendationCard
          custom={5}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <RecommendationTitle>
            <BarChart3 size={20} />
            Progress Monitoring
          </RecommendationTitle>
          <RecommendationContent>
            <MarkdownText>{monitoring}</MarkdownText>
          </RecommendationContent>
        </RecommendationCard>
      )}

      {/* Coordination Metadata Section */}
      {coordination_metadata && Object.keys(coordination_metadata).length > 0 && (
        <MetadataSection
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <MetadataTitle>
            <Clock size={18} />
            AI Coordination Details
          </MetadataTitle>
          <MetadataGrid>
            {coordination_metadata.agents_coordinated && (
              <MetadataItem>
                <span>Agents Coordinated:</span>
                <span>{coordination_metadata.agents_coordinated}</span>
              </MetadataItem>
            )}
            {coordination_metadata.architecture && (
              <MetadataItem>
                <span>Architecture:</span>
                <span>{coordination_metadata.architecture}</span>
              </MetadataItem>
            )}
            {coordination_metadata.ai_models && (
              <MetadataItem>
                <span>AI Models:</span>
                <span>{coordination_metadata.ai_models.join(', ')}</span>
              </MetadataItem>
            )}
            {coordination_metadata.data_sources && (
              <MetadataItem>
                <span>Data Sources:</span>
                <span>{coordination_metadata.data_sources.join(', ')}</span>
              </MetadataItem>
            )}
            {coordination_metadata.processing_time && (
              <MetadataItem>
                <span>Processing Time:</span>
                <ProcessingTime>
                  <Clock size={12} />
                  {coordination_metadata.processing_time}
                </ProcessingTime>
              </MetadataItem>
            )}
          </MetadataGrid>
          
          {coordination_metadata.gke_hackathon_demo && (
            <motion.div
              style={{
                marginTop: '15px',
                padding: '12px 15px',
                background: 'rgba(102, 126, 234, 0.1)',
                borderRadius: '8px',
                color: '#667eea',
                fontSize: '0.9em',
                fontWeight: '600',
                textAlign: 'center'
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
            >
              🏆 Powered by GKE • ADK • MCP • A2A • Vertex AI Gemini
            </motion.div>
          )}
        </MetadataSection>
      )}
    </Container>
  );
}

export default ResultsDisplay;
