"""
Routes API FastAPI
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.models import (
    EvaluationResponse, EvaluationWithAnalysis, AnalysisResponse,
    ClusterResponse, ThemeResponse, InsightResponse, DashboardStats,
    UploadResponse, Evaluation, Analysis, Cluster, Theme, Insight
)
from app.services.file_parser import FileParser
from app.services.nlp_service import get_nlp_service
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["evaluations"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload et traitement d'un fichier d'évaluations
    """
    try:
        # Vérifier l'extension
        filename = file.filename
        ext = filename.split('.')[-1].lower()
        if ext not in ['csv', 'pdf', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {ext}"
            )
        
        # Lire le contenu
        content = await file.read()
        
        # Parser le fichier
        logger.info(f"Parsing file: {filename}")
        evaluation_data = FileParser.parse_file(content, filename)
        
        if not evaluation_data:
            raise HTTPException(
                status_code=400,
                detail="No valid evaluation data found in file"
            )
        
        # Créer les évaluations en DB
        evaluations = []
        for eval_data in evaluation_data:
            # Vérifier si l'évaluation existe déjà
            existing = db.query(Evaluation).filter(
                Evaluation.evaluation_id == eval_data.evaluation_id
            ).first()
            
            if existing:
                logger.warning(f"Evaluation {eval_data.evaluation_id} already exists, skipping")
                continue
            
            evaluation = Evaluation(
                **eval_data.model_dump(),
                file_source=filename
            )
            db.add(evaluation)
            evaluations.append(evaluation)
        
        db.commit()
        
        # Rafraîchir pour obtenir les IDs
        for evaluation in evaluations:
            db.refresh(evaluation)
        
        # Traiter les évaluations avec NLP
        logger.info(f"Processing {len(evaluations)} evaluations with NLP")
        nlp_service = get_nlp_service()
        analyses = nlp_service.process_batch(evaluations, db)
        
        # Générer des insights
        AnalyticsService.generate_insights(db)
        
        return UploadResponse(
            message="File processed successfully",
            file_name=filename,
            total_evaluations=len(evaluations),
            processing_started=True,
            job_id=None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/evaluations", response_model=List[EvaluationWithAnalysis])
def get_evaluations(
    skip: int = 0,
    limit: int = 100,
    formation_type: Optional[str] = None,
    formateur_id: Optional[str] = None,
    langue: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Récupère les évaluations avec filtres optionnels
    """
    query = db.query(Evaluation)
    
    if formation_type:
        query = query.filter(Evaluation.type_formation == formation_type)
    if formateur_id:
        query = query.filter(Evaluation.formateur_id == formateur_id)
    if langue:
        query = query.filter(Evaluation.langue == langue)
    
    evaluations = query.offset(skip).limit(limit).all()
    
    # Joindre les analyses
    results = []
    for eval in evaluations:
        eval_dict = EvaluationResponse.model_validate(eval)
        result = EvaluationWithAnalysis(**eval_dict.model_dump())
        
        if eval.analysis:
            # Filtrer par sentiment si demandé
            if sentiment and eval.analysis.sentiment != sentiment:
                continue
            result.analysis = AnalysisResponse.model_validate(eval.analysis)
        
        results.append(result)
    
    return results


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationWithAnalysis)
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """
    Récupère une évaluation spécifique avec son analyse
    """
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    eval_dict = EvaluationResponse.model_validate(evaluation)
    result = EvaluationWithAnalysis(**eval_dict.model_dump())
    
    if evaluation.analysis:
        result.analysis = AnalysisResponse.model_validate(evaluation.analysis)
    
    return result


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Récupère les statistiques pour le dashboard
    """
    stats = AnalyticsService.get_dashboard_stats(db)
    return DashboardStats(**stats)


@router.get("/themes", response_model=List[ThemeResponse])
def get_themes(
    language: Optional[str] = None,
    top_n: int = 20,
    db: Session = Depends(get_db)
):
    """
    Récupère les thèmes globaux
    """
    query = db.query(Theme).order_by(Theme.frequency.desc())
    
    if language:
        query = query.filter(Theme.language == language)
    
    themes = query.limit(top_n).all()
    return [ThemeResponse.model_validate(theme) for theme in themes]


@router.get("/clusters", response_model=List[ClusterResponse])
def get_clusters(db: Session = Depends(get_db)):
    """
    Récupère les clusters
    """
    clusters = db.query(Cluster).all()
    return [ClusterResponse.model_validate(cluster) for cluster in clusters]


@router.get("/insights", response_model=List[InsightResponse])
def get_insights(
    insight_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Récupère les insights
    """
    query = db.query(Insight).order_by(Insight.created_at.desc())
    
    if insight_type:
        query = query.filter(Insight.insight_type == insight_type)
    
    insights = query.limit(limit).all()
    return [InsightResponse.model_validate(insight) for insight in insights]


@router.get("/analytics/trends")
def get_trends(
    days: int = Query(default=30, ge=1, le=365),
    formation_type: Optional[str] = None,
    formateur_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyse les tendances
    """
    return AnalyticsService.analyze_trends(
        db,
        days=days,
        formation_type=formation_type,
        formateur_id=formateur_id
    )


@router.get("/analytics/correlations")
def get_correlations(db: Session = Depends(get_db)):
    """
    Analyse les corrélations
    """
    return AnalyticsService.analyze_correlations(db)


@router.get("/analytics/compare")
def compare_formations(
    formation1: str,
    formation2: str,
    db: Session = Depends(get_db)
):
    """
    Compare deux formations
    """
    return AnalyticsService.compare_formations(db, formation1, formation2)


@router.post("/analytics/generate-insights")
def generate_insights(db: Session = Depends(get_db)):
    """
    Génère de nouveaux insights
    """
    insights = AnalyticsService.generate_insights(db)
    return {
        "message": f"{len(insights)} new insights generated",
        "insights": [InsightResponse.model_validate(i) for i in insights]
    }
