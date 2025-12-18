"""
Modèles de données SQLAlchemy et Pydantic
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


Base = declarative_base()



class Evaluation(Base):
    """Table des évaluations de formation"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(String(100), unique=True, index=True)
    formation_id = Column(String(100), index=True)
    type_formation = Column(String(200))
    formateur_id = Column(String(100), index=True)
    
    # Critères notés
    satisfaction = Column(Integer)  # 1-5
    contenu = Column(Integer)  # 1-5
    logistique = Column(Integer)  # 1-5
    applicabilite = Column(Integer)  # 1-5
    
    # Commentaire textuel
    commentaire = Column(Text)
    langue = Column(String(10))  # FR, AR, DARIJA
    date = Column(DateTime, default=datetime.utcnow)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    file_source = Column(String(500))
    
    # Relations
    analysis = relationship("Analysis", back_populates="evaluation", uselist=False)


class Analysis(Base):
    """Table des analyses NLP"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), unique=True)
    
    # Résultats NLP
    detected_language = Column(String(10))
    sentiment = Column(String(20))  # positive, negative, neutral
    sentiment_score = Column(Float)  # -1 to 1
    
    # Thèmes extraits
    themes = Column(JSON)  # Liste de thèmes
    entities = Column(JSON)  # Entités nommées extraites
    
    # Clustering
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    embedding = Column(JSON)  # Vecteur d'embedding
    
    # Métadonnées
    processed_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))
    
    # Relations
    evaluation = relationship("Evaluation", back_populates="analysis")
    cluster = relationship("Cluster", back_populates="analyses")


class Cluster(Base):
    """Table des clusters"""
    __tablename__ = "clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_label = Column(String(200))
    cluster_number = Column(Integer)
    
    # Caractéristiques du cluster
    size = Column(Integer)
    representative_themes = Column(JSON)  # Thèmes principaux
    avg_sentiment = Column(Float)
    
    # Visualisation
    centroid = Column(JSON)  # Centre du cluster
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    analyses = relationship("Analysis", back_populates="cluster")


class Theme(Base):
    """Table des thèmes globaux"""
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, index=True)
    theme_name = Column(String(200))  # Removed unique=True
    frequency = Column(Integer, default=1)
    
    # Contexte
    keywords = Column(JSON)  # Mots-clés associés
    language = Column(String(10))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('theme_name', 'language', name='unique_theme_per_language'),
    )


class Insight(Base):
    """Table des insights automatiques générés"""
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String(50))  # trend, correlation, anomaly, recommendation
    title = Column(String(500))
    description = Column(Text)
    
    # Données associées
    data = Column(JSON)
    confidence = Column(Float)  # 0-1
    
    # Métadonnées
    formation_type = Column(String(200), nullable=True)
    formateur_id = Column(String(100), nullable=True)
    date_range_start = Column(DateTime, nullable=True)
    date_range_end = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== Pydantic Models ====================

class LanguageEnum(str, Enum):
    FRENCH = "FR"
    ARABIC = "AR"
    DARIJA = "DARIJA"


class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EvaluationBase(BaseModel):
    evaluation_id: str
    formation_id: str
    type_formation: str
    formateur_id: str
    satisfaction: int = Field(ge=1, le=5)
    contenu: int = Field(ge=1, le=5)
    logistique: int = Field(ge=1, le=5)
    applicabilite: int = Field(ge=1, le=5)
    commentaire: str
    langue: Optional[str] = None
    date: Optional[datetime] = None


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationResponse(EvaluationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    id: int
    evaluation_id: int
    detected_language: str
    sentiment: str
    sentiment_score: float
    themes: List[str]
    entities: Optional[Dict[str, Any]] = None
    cluster_id: Optional[int] = None
    processed_at: datetime
    
    class Config:
        from_attributes = True


class EvaluationWithAnalysis(EvaluationResponse):
    analysis: Optional[AnalysisResponse] = None


class ClusterResponse(BaseModel):
    id: int
    cluster_label: str
    cluster_number: int
    size: int
    representative_themes: List[str]
    avg_sentiment: float
    
    class Config:
        from_attributes = True


class ThemeResponse(BaseModel):
    id: int
    theme_name: str
    frequency: int
    keywords: List[str]
    language: str
    
    class Config:
        from_attributes = True


class InsightResponse(BaseModel):
    id: int
    insight_type: str
    title: str
    description: str
    confidence: float
    data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    message: str
    file_name: str
    total_evaluations: int
    processing_started: bool
    job_id: Optional[str] = None


class DashboardStats(BaseModel):
    total_evaluations: int
    avg_satisfaction: float
    avg_contenu: float
    avg_logistique: float
    avg_applicabilite: float
    sentiment_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    formation_types: Dict[str, int]
    theme_categories: Dict[str, Any]  # Changed from top_themes to theme_categories
    recent_insights: List[InsightResponse]
