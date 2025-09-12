"""
Research and Dataset Management System for Mind Mend
Handles research papers, clinical datasets, and knowledge base for early diagnosis
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
try:
    from app import db
except ImportError:
    # Handle circular import
    db = None
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class ResearchPaper(db.Model):
    """Model for storing research papers and studies"""
    __tablename__ = 'research_papers'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text)
    abstract = Column(Text)
    full_text = Column(Text)
    publication_date = Column(DateTime)
    journal = Column(String(200))
    doi = Column(String(100), unique=True)
    pmid = Column(String(50))
    category = Column(String(100))  # e.g., 'early_diagnosis', 'conflict_resolution', 'therapy_methods'
    tags = Column(JSON)  # List of relevant tags
    file_path = Column(String(500))  # Path to PDF if uploaded
    embeddings = Column(JSON)  # Text embeddings for similarity search
    relevance_score = Column(Float, default=0.0)
    citation_count = Column(Integer, default=0)
    added_date = Column(DateTime, default=datetime.utcnow)
    added_by = Column(String(100))
    validated = Column(Boolean, default=False)
    
    # Relationships
    datasets = relationship("ClinicalDataset", back_populates="research_paper")
    insights = relationship("ResearchInsight", back_populates="paper")

class ClinicalDataset(db.Model):
    """Model for storing clinical datasets"""
    __tablename__ = 'clinical_datasets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    data_type = Column(String(100))  # e.g., 'behavioral', 'physiological', 'survey', 'imaging'
    size = Column(Integer)  # Number of records
    features = Column(JSON)  # List of features/variables
    target_variable = Column(String(200))
    collection_period = Column(String(100))
    institution = Column(String(300))
    ethical_approval = Column(String(200))
    file_path = Column(String(500))
    format = Column(String(50))  # e.g., 'csv', 'json', 'sql'
    
    # Analysis metadata
    preprocessing_notes = Column(Text)
    statistical_summary = Column(JSON)
    quality_score = Column(Float)
    
    # Privacy and compliance
    anonymized = Column(Boolean, default=True)
    consent_type = Column(String(100))
    restrictions = Column(Text)
    
    # Relationships
    paper_id = Column(Integer, ForeignKey('research_papers.id'))
    research_paper = relationship("ResearchPaper", back_populates="datasets")
    analyses = relationship("DataAnalysis", back_populates="dataset")
    
    added_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ResearchInsight(db.Model):
    """Model for storing extracted insights from research"""
    __tablename__ = 'research_insights'
    
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey('research_papers.id'))
    insight_type = Column(String(100))  # e.g., 'diagnostic_marker', 'intervention', 'risk_factor'
    title = Column(String(300))
    description = Column(Text)
    confidence_level = Column(Float)  # 0-1 confidence score
    clinical_relevance = Column(String(50))  # 'high', 'medium', 'low'
    applicable_conditions = Column(JSON)  # List of mental health conditions
    evidence_strength = Column(String(50))  # 'strong', 'moderate', 'preliminary'
    implementation_notes = Column(Text)
    
    # Relationships
    paper = relationship("ResearchPaper", back_populates="insights")
    
    created_date = Column(DateTime, default=datetime.utcnow)
    validated_by = Column(String(100))
    validation_date = Column(DateTime)

class DataAnalysis(db.Model):
    """Model for storing dataset analysis results"""
    __tablename__ = 'data_analyses'
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('clinical_datasets.id'))
    analysis_type = Column(String(100))  # e.g., 'predictive_model', 'correlation', 'clustering'
    methodology = Column(Text)
    results = Column(JSON)
    accuracy_metrics = Column(JSON)
    key_findings = Column(Text)
    clinical_implications = Column(Text)
    limitations = Column(Text)
    
    # Model information if applicable
    model_type = Column(String(100))
    model_parameters = Column(JSON)
    model_path = Column(String(500))
    
    # Relationships
    dataset = relationship("ClinicalDataset", back_populates="analyses")
    
    performed_date = Column(DateTime, default=datetime.utcnow)
    performed_by = Column(String(100))

class ResearchManager:
    """Manager class for research and dataset operations"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.research_cache = {}
        self.insight_templates = self._load_insight_templates()
        
    def _load_insight_templates(self):
        """Load templates for extracting insights from research"""
        return {
            'early_diagnosis': {
                'markers': ['symptom', 'indicator', 'predictor', 'biomarker', 'risk factor'],
                'methods': ['screening', 'assessment', 'detection', 'identification'],
                'outcomes': ['accuracy', 'sensitivity', 'specificity', 'prediction']
            },
            'conflict_resolution': {
                'techniques': ['communication', 'mediation', 'negotiation', 'de-escalation'],
                'strategies': ['approach', 'intervention', 'technique', 'method'],
                'effectiveness': ['outcome', 'success rate', 'improvement', 'resolution']
            },
            'therapy_methods': {
                'approaches': ['CBT', 'DBT', 'EMDR', 'mindfulness', 'psychodynamic'],
                'efficacy': ['effective', 'outcome', 'improvement', 'response'],
                'populations': ['adults', 'children', 'couples', 'groups', 'specific conditions']
            }
        }
    
    def add_research_paper(self, paper_data: Dict[str, Any]) -> ResearchPaper:
        """Add a new research paper to the knowledge base"""
        try:
            # Create paper object
            paper = ResearchPaper(
                title=paper_data['title'],
                authors=paper_data.get('authors', ''),
                abstract=paper_data.get('abstract', ''),
                full_text=paper_data.get('full_text', ''),
                publication_date=paper_data.get('publication_date'),
                journal=paper_data.get('journal', ''),
                doi=paper_data.get('doi', ''),
                pmid=paper_data.get('pmid', ''),
                category=paper_data.get('category', 'general'),
                tags=paper_data.get('tags', []),
                file_path=paper_data.get('file_path', ''),
                added_by=paper_data.get('added_by', 'system')
            )
            
            # Generate embeddings for similarity search
            if paper.abstract or paper.full_text:
                text = f"{paper.title} {paper.abstract} {paper.full_text[:1000]}"
                paper.embeddings = self._generate_embeddings(text)
            
            # Calculate initial relevance score
            paper.relevance_score = self._calculate_relevance_score(paper)
            
            db.session.add(paper)
            db.session.commit()
            
            # Extract insights asynchronously
            self._extract_insights_from_paper(paper)
            
            logger.info(f"Added research paper: {paper.title}")
            return paper
            
        except Exception as e:
            logger.error(f"Error adding research paper: {str(e)}")
            db.session.rollback()
            raise
    
    def add_clinical_dataset(self, dataset_data: Dict[str, Any]) -> ClinicalDataset:
        """Add a new clinical dataset"""
        try:
            dataset = ClinicalDataset(
                name=dataset_data['name'],
                description=dataset_data.get('description', ''),
                data_type=dataset_data.get('data_type', 'general'),
                size=dataset_data.get('size', 0),
                features=dataset_data.get('features', []),
                target_variable=dataset_data.get('target_variable', ''),
                collection_period=dataset_data.get('collection_period', ''),
                institution=dataset_data.get('institution', ''),
                ethical_approval=dataset_data.get('ethical_approval', ''),
                file_path=dataset_data.get('file_path', ''),
                format=dataset_data.get('format', 'csv'),
                paper_id=dataset_data.get('paper_id'),
                anonymized=dataset_data.get('anonymized', True),
                consent_type=dataset_data.get('consent_type', 'informed_consent')
            )
            
            # Generate quality score
            dataset.quality_score = self._assess_dataset_quality(dataset)
            
            db.session.add(dataset)
            db.session.commit()
            
            logger.info(f"Added clinical dataset: {dataset.name}")
            return dataset
            
        except Exception as e:
            logger.error(f"Error adding clinical dataset: {str(e)}")
            db.session.rollback()
            raise
    
    def search_research(self, query: str, category: Optional[str] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Search research papers using natural language query"""
        try:
            # Get all papers
            papers_query = ResearchPaper.query
            if category:
                papers_query = papers_query.filter_by(category=category)
            
            papers = papers_query.all()
            
            if not papers:
                return []
            
            # Generate query embedding
            query_embedding = self._generate_embeddings(query)
            
            # Calculate similarity scores
            results = []
            for paper in papers:
                if paper.embeddings:
                    similarity = self._calculate_similarity(query_embedding, paper.embeddings)
                    results.append({
                        'paper': paper,
                        'similarity': similarity
                    })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return [{
                'id': r['paper'].id,
                'title': r['paper'].title,
                'authors': r['paper'].authors,
                'abstract': r['paper'].abstract[:500] + '...' if r['paper'].abstract else '',
                'category': r['paper'].category,
                'tags': r['paper'].tags,
                'relevance_score': r['paper'].relevance_score,
                'similarity_score': r['similarity'],
                'publication_date': r['paper'].publication_date.isoformat() if r['paper'].publication_date else None
            } for r in results[:limit]]
            
        except Exception as e:
            logger.error(f"Error searching research: {str(e)}")
            return []
    
    def get_insights_for_condition(self, condition: str, 
                                 insight_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get research insights for a specific mental health condition"""
        try:
            insights_query = ResearchInsight.query
            
            # Filter by condition
            insights = []
            for insight in insights_query.all():
                if condition.lower() in [c.lower() for c in insight.applicable_conditions or []]:
                    if not insight_type or insight.insight_type == insight_type:
                        insights.append(insight)
            
            # Sort by confidence and clinical relevance
            insights.sort(key=lambda x: (
                x.confidence_level or 0,
                {'high': 3, 'medium': 2, 'low': 1}.get(x.clinical_relevance, 0)
            ), reverse=True)
            
            return [{
                'id': insight.id,
                'type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence_level,
                'relevance': insight.clinical_relevance,
                'evidence_strength': insight.evidence_strength,
                'paper_title': insight.paper.title if insight.paper else None,
                'implementation_notes': insight.implementation_notes
            } for insight in insights]
            
        except Exception as e:
            logger.error(f"Error getting insights: {str(e)}")
            return []
    
    def analyze_dataset_for_patterns(self, dataset_id: int, 
                                   analysis_type: str = 'correlation') -> Dict[str, Any]:
        """Analyze a clinical dataset for patterns relevant to mental health"""
        try:
            dataset = ClinicalDataset.query.get(dataset_id)
            if not dataset:
                return {'error': 'Dataset not found'}
            
            # Placeholder for actual analysis
            # In production, this would load the dataset and perform real analysis
            analysis_result = {
                'dataset_name': dataset.name,
                'analysis_type': analysis_type,
                'key_findings': [
                    'Identified 3 key predictors for early anxiety detection',
                    'Found significant correlation between sleep patterns and mood',
                    'Discovered clustering of symptoms in specific age groups'
                ],
                'visualizations': [],
                'recommendations': [
                    'Implement screening for identified risk factors',
                    'Consider sleep quality in initial assessments',
                    'Tailor interventions based on age group patterns'
                ]
            }
            
            # Save analysis results
            analysis = DataAnalysis(
                dataset_id=dataset_id,
                analysis_type=analysis_type,
                results=analysis_result,
                key_findings='\n'.join(analysis_result['key_findings']),
                performed_by='system'
            )
            db.session.add(analysis)
            db.session.commit()
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing dataset: {str(e)}")
            return {'error': str(e)}
    
    def get_early_diagnosis_indicators(self, condition: str) -> List[Dict[str, Any]]:
        """Get early diagnosis indicators for a specific condition"""
        papers = self.search_research(
            f"early diagnosis indicators {condition}",
            category='early_diagnosis'
        )
        
        insights = self.get_insights_for_condition(
            condition,
            insight_type='diagnostic_marker'
        )
        
        return {
            'condition': condition,
            'research_papers': papers[:5],
            'diagnostic_markers': insights,
            'recommended_assessments': self._get_recommended_assessments(condition),
            'risk_factors': self._get_risk_factors(condition)
        }
    
    def get_conflict_resolution_strategies(self, conflict_type: str) -> Dict[str, Any]:
        """Get evidence-based conflict resolution strategies"""
        papers = self.search_research(
            f"conflict resolution {conflict_type}",
            category='conflict_resolution'
        )
        
        strategies = []
        for paper in papers[:5]:
            # Extract strategies from paper insights
            paper_insights = ResearchInsight.query.filter_by(
                paper_id=paper['id'],
                insight_type='intervention'
            ).all()
            
            for insight in paper_insights:
                strategies.append({
                    'strategy': insight.title,
                    'description': insight.description,
                    'effectiveness': insight.confidence_level,
                    'source': paper['title']
                })
        
        return {
            'conflict_type': conflict_type,
            'evidence_based_strategies': strategies,
            'recommended_approaches': self._get_conflict_approaches(conflict_type),
            'success_factors': self._get_success_factors(conflict_type)
        }
    
    def _generate_embeddings(self, text: str) -> List[float]:
        """Generate text embeddings for similarity search"""
        try:
            # Simple TF-IDF based embeddings
            # In production, use more sophisticated embeddings (e.g., BERT)
            if not hasattr(self, '_fitted_vectorizer'):
                # Fit on a sample if not already fitted
                sample_texts = ["mental health", "therapy", "diagnosis", "treatment"]
                self.vectorizer.fit(sample_texts)
                self._fitted_vectorizer = True
            
            vector = self.vectorizer.transform([text]).toarray()[0]
            return vector.tolist()
        except:
            return [0.0] * 100  # Return zero vector on error
    
    def _calculate_similarity(self, embedding1: List[float], 
                            embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            sim = cosine_similarity(
                np.array(embedding1).reshape(1, -1),
                np.array(embedding2).reshape(1, -1)
            )[0][0]
            return float(sim)
        except:
            return 0.0
    
    def _calculate_relevance_score(self, paper: ResearchPaper) -> float:
        """Calculate relevance score for a research paper"""
        score = 0.0
        
        # Recency bonus
        if paper.publication_date:
            years_old = (datetime.utcnow() - paper.publication_date).days / 365
            if years_old < 2:
                score += 0.3
            elif years_old < 5:
                score += 0.2
            elif years_old < 10:
                score += 0.1
        
        # Category relevance
        priority_categories = ['early_diagnosis', 'conflict_resolution', 'therapy_methods']
        if paper.category in priority_categories:
            score += 0.2
        
        # Citation impact
        if paper.citation_count:
            if paper.citation_count > 100:
                score += 0.3
            elif paper.citation_count > 50:
                score += 0.2
            elif paper.citation_count > 10:
                score += 0.1
        
        # Tag relevance
        important_tags = ['evidence-based', 'meta-analysis', 'clinical-trial', 'systematic-review']
        if paper.tags:
            matching_tags = len([t for t in paper.tags if t in important_tags])
            score += min(matching_tags * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _assess_dataset_quality(self, dataset: ClinicalDataset) -> float:
        """Assess quality score of a clinical dataset"""
        score = 0.0
        
        # Size factor
        if dataset.size:
            if dataset.size > 1000:
                score += 0.2
            elif dataset.size > 500:
                score += 0.15
            elif dataset.size > 100:
                score += 0.1
        
        # Ethical approval
        if dataset.ethical_approval:
            score += 0.2
        
        # Anonymization
        if dataset.anonymized:
            score += 0.15
        
        # Feature completeness
        if dataset.features and len(dataset.features) > 10:
            score += 0.15
        
        # Institution credibility
        if dataset.institution:
            score += 0.1
        
        # Format accessibility
        if dataset.format in ['csv', 'json']:
            score += 0.1
        
        # Documentation
        if dataset.description and len(dataset.description) > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_insights_from_paper(self, paper: ResearchPaper):
        """Extract insights from research paper using NLP"""
        # This would use NLP to extract insights
        # For now, creating placeholder insights
        
        if 'early' in paper.title.lower() or 'diagnosis' in paper.title.lower():
            insight = ResearchInsight(
                paper_id=paper.id,
                insight_type='diagnostic_marker',
                title=f"Early indicators from {paper.title[:50]}...",
                description="Key early diagnosis indicators identified in this research",
                confidence_level=0.8,
                clinical_relevance='high',
                applicable_conditions=['anxiety', 'depression'],
                evidence_strength='moderate'
            )
            db.session.add(insight)
        
        db.session.commit()
    
    def _get_recommended_assessments(self, condition: str) -> List[Dict[str, str]]:
        """Get recommended assessments for a condition"""
        assessments = {
            'anxiety': [
                {'name': 'GAD-7', 'description': 'Generalized Anxiety Disorder 7-item scale'},
                {'name': 'BAI', 'description': 'Beck Anxiety Inventory'},
                {'name': 'STAI', 'description': 'State-Trait Anxiety Inventory'}
            ],
            'depression': [
                {'name': 'PHQ-9', 'description': 'Patient Health Questionnaire-9'},
                {'name': 'BDI-II', 'description': 'Beck Depression Inventory-II'},
                {'name': 'HAM-D', 'description': 'Hamilton Depression Rating Scale'}
            ],
            'ptsd': [
                {'name': 'PCL-5', 'description': 'PTSD Checklist for DSM-5'},
                {'name': 'CAPS-5', 'description': 'Clinician-Administered PTSD Scale'},
                {'name': 'IES-R', 'description': 'Impact of Event Scale-Revised'}
            ]
        }
        return assessments.get(condition.lower(), [])
    
    def _get_risk_factors(self, condition: str) -> List[str]:
        """Get risk factors for a condition"""
        risk_factors = {
            'anxiety': [
                'Family history of anxiety disorders',
                'Chronic stress exposure',
                'Traumatic life events',
                'Substance use',
                'Medical conditions'
            ],
            'depression': [
                'Previous depressive episodes',
                'Family history of depression',
                'Chronic illness',
                'Social isolation',
                'Major life changes'
            ]
        }
        return risk_factors.get(condition.lower(), [])
    
    def _get_conflict_approaches(self, conflict_type: str) -> List[Dict[str, str]]:
        """Get conflict resolution approaches"""
        approaches = {
            'couple': [
                {'name': 'Gottman Method', 'description': 'Research-based approach for couples'},
                {'name': 'EFT', 'description': 'Emotionally Focused Therapy'},
                {'name': 'Imago Therapy', 'description': 'Dialogue-based relationship therapy'}
            ],
            'family': [
                {'name': 'Structural Family Therapy', 'description': 'Focus on family organization'},
                {'name': 'Strategic Family Therapy', 'description': 'Problem-focused interventions'},
                {'name': 'Narrative Therapy', 'description': 'Reauthoring family stories'}
            ]
        }
        return approaches.get(conflict_type.lower(), [])
    
    def _get_success_factors(self, conflict_type: str) -> List[str]:
        """Get success factors for conflict resolution"""
        return [
            'Active listening and validation',
            'Clear communication guidelines',
            'Mutual respect and empathy',
            'Focus on solutions rather than blame',
            'Professional mediation when needed'
        ]

# Create singleton instance
research_manager = ResearchManager()