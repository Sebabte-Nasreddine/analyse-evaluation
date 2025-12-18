"""
Service d'analyse quantitative automatisée
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging
from app.models.models import Evaluation, Analysis, Cluster, Theme, Insight, SentimentEnum
from scipy import stats

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service d'analyse quantitative et génération d'insights
    """
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, any]:
        """
        Calcule les statistiques pour le dashboard
        
        Args:
            db: Session de base de données
            
        Returns:
            Dict avec toutes les statistiques
        """
        # Nombre total d'évaluations
        total_evaluations = db.query(func.count(Evaluation.id)).scalar()
        
        # Moyennes des critères
        avg_stats = db.query(
            func.avg(Evaluation.satisfaction).label('avg_satisfaction'),
            func.avg(Evaluation.contenu).label('avg_contenu'),
            func.avg(Evaluation.logistique).label('avg_logistique'),
            func.avg(Evaluation.applicabilite).label('avg_applicabilite')
        ).first()
        
        # Distribution des sentiments
        sentiment_dist = db.query(
            Analysis.sentiment,
            func.count(Analysis.id)
        ).group_by(Analysis.sentiment).all()
        
        sentiment_distribution = {
            sentiment: count for sentiment, count in sentiment_dist
        }
        
        # Distribution des langues
        lang_dist = db.query(
            Evaluation.langue,
            func.count(Evaluation.id)
        ).group_by(Evaluation.langue).all()
        
        language_distribution = {
            lang: count for lang, count in lang_dist
        }
        
        # Types de formation
        formation_dist = db.query(
            Evaluation.type_formation,
            func.count(Evaluation.id)
        ).group_by(Evaluation.type_formation).all()
        
        formation_types = {
            type_form: count for type_form, count in formation_dist
        }
        
        # Thèmes catégorisés en 4 catégories générales
        from app.services.theme_categorizer import theme_categorizer
        categorized_themes = theme_categorizer.get_categorized_themes(db, top_n=50)
        
        # Insights récents
        recent_insights = db.query(Insight).order_by(
            desc(Insight.created_at)
        ).limit(5).all()
        
        return {
            "total_evaluations": total_evaluations or 0,
            "avg_satisfaction": float(avg_stats.avg_satisfaction or 0),
            "avg_contenu": float(avg_stats.avg_contenu or 0),
            "avg_logistique": float(avg_stats.avg_logistique or 0),
            "avg_applicabilite": float(avg_stats.avg_applicabilite or 0),
            "sentiment_distribution": sentiment_distribution,
            "language_distribution": language_distribution,
            "formation_types": formation_types,
            "theme_categories": categorized_themes,  # 4 catégories générales
            "recent_insights": recent_insights
        }
    
    @staticmethod
    def analyze_trends(
        db: Session,
        days: int = 30,
        formation_type: Optional[str] = None,
        formateur_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyse les tendances temporelles
        
        Args:
            db: Session de base de données
            days: Nombre de jours à analyser
            formation_type: Filtrer par type de formation
            formateur_id: Filtrer par formateur
            
        Returns:
            Dict avec les tendances
        """
        # Date de début
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query de base
        query = db.query(Evaluation).filter(Evaluation.date >= start_date)
        
        if formation_type:
            query = query.filter(Evaluation.type_formation == formation_type)
        if formateur_id:
            query = query.filter(Evaluation.formateur_id == formateur_id)
        
        evaluations = query.all()
        
        if not evaluations:
            return {"error": "No data for the specified period"}
        
        # Convertir en DataFrame
        df = pd.DataFrame([
            {
                "date": e.date,
                "satisfaction": e.satisfaction,
                "contenu": e.contenu,
                "logistique": e.logistique,
                "applicabilite": e.applicabilite,
            }
            for e in evaluations
        ])
        
        # Grouper par semaine
        df['week'] = pd.to_datetime(df['date']).dt.to_period('W')
        weekly = df.groupby('week').agg({
            'satisfaction': 'mean',
            'contenu': 'mean',
            'logistique': 'mean',
            'applicabilite': 'mean',
        }).reset_index()
        
        # Calculer les tendances (régression linéaire simple)
        trends = {}
        for col in ['satisfaction', 'contenu', 'logistique', 'applicabilite']:
            if len(weekly) > 1:
                x = np.arange(len(weekly))
                y = weekly[col].values
                slope, _, _, _, _ = stats.linregress(x, y)
                trends[col] = {
                    "trend": "increasing" if slope > 0.05 else "decreasing" if slope < -0.05 else "stable",
                    "slope": float(slope)
                }
            else:
                trends[col] = {"trend": "stable", "slope": 0.0}
        
        return {
            "period_days": days,
            "total_evaluations": len(evaluations),
            "weekly_data": weekly.to_dict(orient='records'),
            "trends": trends
        }
    
    @staticmethod
    def analyze_correlations(db: Session) -> Dict[str, any]:
        """
        Analyse les corrélations entre critères
        
        Args:
            db: Session de base de données
            
        Returns:
            Dict avec les corrélations
        """
        # Récupérer toutes les évaluations
        evaluations = db.query(Evaluation).all()
        
        if len(evaluations) < 10:
            return {"error": "Not enough data for correlation analysis"}
        
        # Convertir en DataFrame
        df = pd.DataFrame([
            {
                "satisfaction": e.satisfaction,
                "contenu": e.contenu,
                "logistique": e.logistique,
                "applicabilite": e.applicabilite,
            }
            for e in evaluations
        ])
        
        # Calculer la matrice de corrélation
        corr_matrix = df.corr()
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": AnalyticsService._find_strong_correlations(corr_matrix)
        }
    
    @staticmethod
    def _find_strong_correlations(
        corr_matrix: pd.DataFrame, 
        threshold: float = 0.7
    ) -> List[Dict[str, any]]:
        """
        Trouve les corrélations fortes
        
        Args:
            corr_matrix: Matrice de corrélation
            threshold: Seuil de corrélation
            
        Returns:
            Liste de corrélations fortes
        """
        strong_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corr.append({
                        "variable1": corr_matrix.columns[i],
                        "variable2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong positive" if corr_value > 0 else "strong negative"
                    })
        
        return strong_corr
    
    @staticmethod
    def generate_insights(db: Session) -> List[Insight]:
        """
        Génère automatiquement des insights
        
        Args:
            db: Session de base de données
            
        Returns:
            Liste d'insights générés
        """
        insights = []
        
        # 1. Identifier les formations avec satisfaction faible
        low_satisfaction = db.query(
            Evaluation.type_formation,
            func.avg(Evaluation.satisfaction).label('avg_sat')
        ).group_by(
            Evaluation.type_formation
        ).having(
            func.avg(Evaluation.satisfaction) < 3
        ).all()
        
        for formation, avg_sat in low_satisfaction:
            insight = Insight(
                insight_type="signal_faible",
                title=f"Attention: Satisfaction faible pour {formation}",
                description=f"La formation '{formation}' a une satisfaction moyenne de {avg_sat:.2f}/5, "
                           f"ce qui est en dessous du seuil acceptable.",
                data={"formation": formation, "avg_satisfaction": float(avg_sat)},
                confidence=0.9,
                formation_type=formation
            )
            insights.append(insight)
        
        # 2. Identifier les formateurs excellents
        top_formateurs = db.query(
            Evaluation.formateur_id,
            func.avg(Evaluation.satisfaction).label('avg_sat'),
            func.count(Evaluation.id).label('count')
        ).group_by(
            Evaluation.formateur_id
        ).having(
            func.avg(Evaluation.satisfaction) >= 4.5
        ).having(
            func.count(Evaluation.id) >= 5
        ).all()
        
        for formateur, avg_sat, count in top_formateurs:
            insight = Insight(
                insight_type="tendance",
                title=f"Formateur excellent: {formateur}",
                description=f"Le formateur {formateur} obtient une satisfaction exceptionnelle de "
                           f"{avg_sat:.2f}/5 sur {count} évaluations.",
                data={"formateur": formateur, "avg_satisfaction": float(avg_sat), "evaluations": count},
                confidence=0.95,
                formateur_id=formateur
            )
            insights.append(insight)
        
        # 3. Analyser les tendances sentiment récentes
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_analyses = db.query(Analysis).join(
            Evaluation
        ).filter(
            Evaluation.date >= recent_date
        ).all()
        
        if recent_analyses:
            sentiment_counts = {
                SentimentEnum.POSITIVE.value: 0,
                SentimentEnum.NEUTRAL.value: 0,
                SentimentEnum.NEGATIVE.value: 0
            }
            
            for analysis in recent_analyses:
                if analysis.sentiment in sentiment_counts:
                    sentiment_counts[analysis.sentiment] += 1
            
            total = sum(sentiment_counts.values())
            negative_pct = (sentiment_counts[SentimentEnum.NEGATIVE.value] / total * 100) if total > 0 else 0
            
            if negative_pct > 30:
                insight = Insight(
                    insight_type="trend",
                    title="Augmentation des sentiments négatifs",
                    description=f"{negative_pct:.1f}% des évaluations récentes (7 derniers jours) "
                               f"expriment un sentiment négatif.",
                    data={"sentiment_distribution": sentiment_counts, "negative_percentage": negative_pct},
                    confidence=0.8,
                    date_range_start=recent_date,
                    date_range_end=datetime.utcnow()
                )
                insights.append(insight)
        
        # Sauvegarder les insights
        for insight in insights:
            db.add(insight)
        
        try:
            db.commit()
            logger.info(f"Generated {len(insights)} new insights")
        except Exception as e:
            logger.error(f"Error saving insights: {e}")
            db.rollback()
        
        return insights
    
    @staticmethod
    def compare_formations(
        db: Session,
        formation1: str,
        formation2: str
    ) -> Dict[str, any]:
        """
        Compare deux types de formation
        
        Args:
            db: Session
            formation1: Premier type de formation
            formation2: Deuxième type de formation
            
        Returns:
            Comparaison détaillée
        """
        stats = {}
        
        for formation in [formation1, formation2]:
            evals = db.query(Evaluation).filter(
                Evaluation.type_formation == formation
            ).all()
            
            if evals:
                df = pd.DataFrame([{
                    "satisfaction": e.satisfaction,
                    "contenu": e.contenu,
                    "logistique": e.logistique,
                    "applicabilite": e.applicabilite,
                } for e in evals])
                
                stats[formation] = {
                    "count": len(evals),
                    "satisfaction": float(df['satisfaction'].mean()),
                    "contenu": float(df['contenu'].mean()),
                    "logistique": float(df['logistique'].mean()),
                    "applicabilite": float(df['applicabilite'].mean()),
                }
            else:
                stats[formation] = None
        
        return {
            "formation1": formation1,
            "formation2": formation2,
            "stats": stats,
            "comparison": "completed" if all(stats.values()) else "incomplete_data"
        }
