"""
Service NLP principal orchestrant tous les services d'analyse
"""
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
import numpy as np
from app.models.models import (
    Evaluation, Analysis, Cluster, Theme,
    EvaluationCreate, LanguageEnum
)
from app.services.language_detector import LanguageDetector
from app.services.sentiment_analyzer import get_sentiment_analyzer
from app.services.topic_extractor import get_topic_extractor
from app.services.clustering_service import get_clustering_service

logger = logging.getLogger(__name__)


class NLPService:
    """
    Service NLP principal - orchestre toutes les analyses
    """
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.topic_extractor = get_topic_extractor()
        self.clustering_service = get_clustering_service()
    
    def process_evaluation(
        self,
        evaluation: Evaluation,
        db: Session
    ) -> Analysis:
        """
        Traite une évaluation unique
        
        Args:
            evaluation: Évaluation à traiter
            db: Session de base de données
            
        Returns:
            Objet Analysis
        """
        commentaire = evaluation.commentaire or ""
        
        # 1. Détection de langue
        detected_lang = self.language_detector.detect_language(commentaire)
        confidence = self.language_detector.get_confidence(commentaire, detected_lang)
        
        final_lang = evaluation.langue or detected_lang
        
        logger.info(f"Processing evaluation {evaluation.id}: lang={final_lang}")
        
        # 2. Analyse de sentiment
        sentiment_result = self.sentiment_analyzer.analyze(commentaire, final_lang)
        
        # 3. Extraction de thèmes
        themes = self.topic_extractor.extract_themes_single(commentaire, final_lang, top_n=5)
        
        
        # Créer l'analyse
        analysis = Analysis(
            evaluation_id=evaluation.id,
            detected_language=final_lang,
            sentiment=sentiment_result["sentiment"],
            sentiment_score=sentiment_result["score"],
            themes=themes,
            entities={},  # Pourrait être étendu avec NER
            embedding=[],  # Sera rempli lors du clustering batch
            model_version="1.0"
        )
        
        db.add(analysis)
        
        # Mettre à jour les thèmes globaux
        self._update_global_themes(themes, final_lang, db)
        
        return analysis
    
    def process_batch(
        self,
        evaluations: List[Evaluation],
        db: Session
    ) -> List[Analysis]:
        """
        Traite un batch d'évaluations
        
        Args:
            evaluations: Liste d'évaluations
            db: Session de base de données
            
        Returns:
            Liste des analyses créées
        """
        if not evaluations:
            return []
        
        logger.info(f"Processing batch of {len(evaluations)} evaluations")
        
        # Extraire les commentaires et langues
        commentaires = [e.commentaire or "" for e in evaluations]
        langues = []
        
        # Détecter les langues
        for eval in evaluations:
            if eval.langue:
                langues.append(eval.langue)
            else:
                detected = self.language_detector.detect_language(eval.commentaire or "")
                langues.append(detected)
                eval.langue = detected
        
        # 1. Analyse de sentiment batch
        sentiment_results = self.sentiment_analyzer.analyze_batch(commentaires, langues)
        
        # 2. Extraction de thèmes batch
        themes_list, topic_info = self.topic_extractor.extract_themes_batch(commentaires, langues)
        
        # 3. Générer embeddings pour clustering
        embeddings = self.clustering_service.get_embeddings(commentaires)
        
        # Créer les analyses
        analyses = []
        all_themes_to_update = []  # Collecter tous les thèmes pour update en batch
        
        for i, evaluation in enumerate(evaluations):
            analysis = Analysis(
                evaluation_id=evaluation.id,
                detected_language=langues[i],
                sentiment=sentiment_results[i]["sentiment"],
                sentiment_score=sentiment_results[i]["score"],
                themes=themes_list[i] if i < len(themes_list) else [],
                entities={},
                embedding=embeddings[i].tolist() if len(embeddings) > 0 else [],
                model_version="1.0"
            )
            analyses.append(analysis)
            db.add(analysis)
            
            # Collecter les thèmes pour mise à jour groupée
            if i < len(themes_list) and themes_list[i]:
                all_themes_to_update.append((themes_list[i], langues[i]))
        
        self._update_global_themes_batch(all_themes_to_update, db)
        
        # 4. Clustering
        if len(embeddings) > 0:
            self._perform_clustering(analyses, embeddings, commentaires, db)
        
        try:
            db.commit()
            logger.info(f"Successfully processed {len(analyses)} evaluations")
        except Exception as e:
            logger.error(f"Error committing analyses: {e}")
            db.rollback()
            raise
        
        return analyses
    
    def _update_global_themes(
        self,
        themes: List[str],
        language: str,
        db: Session
    ) -> None:
        """
        Met à jour les thèmes globaux dans la base de données
        
        Args:
            themes: Liste de thèmes
            language: Langue
            db: Session
        """
        for theme_name in themes:
            if not theme_name:
                continue
            
            # Chercher si le thème existe déjà
            theme = db.query(Theme).filter(
                Theme.theme_name == theme_name,
                Theme.language == language
            ).first()
            
            if theme:
                # Incrémenter la fréquence
                theme.frequency += 1
            else:
                # Créer un nouveau thème
                theme = Theme(
                    theme_name=theme_name,
                    frequency=1,
                    keywords=[theme_name],
                    language=language
                )
                db.add(theme)
    
    def _perform_clustering(
        self,
        analyses: List[Analysis],
        embeddings: np.ndarray,
        texts: List[str],
        db: Session
    ) -> None:
        """
        Effectue le clustering et crée les clusters
        
        Args:
            analyses: Liste des analyses
            embeddings: Embeddings correspondants
            texts: Textes originaux
            db: Session
        """
        try:
            # Effectuer le clustering
            _, cluster_labels, cluster_info = self.clustering_service.cluster(
                texts,
                method="kmeans"
            )
            
            # Créer ou récupérer les clusters
            cluster_map = {}  # label -> Cluster object
            
            for label in set(cluster_labels):
                if label == -1:  # Outliers
                    continue
                
                # Trouver les indices de ce cluster
                indices = np.where(cluster_labels == label)[0]
                
                # Calculer les thèmes représentatifs
                cluster_themes = []
                for idx in indices:
                    if analyses[idx].themes:
                        cluster_themes.extend(analyses[idx].themes)
                
                # Prendre les thèmes les plus fréquents
                from collections import Counter
                theme_counts = Counter(cluster_themes)
                top_themes = [theme for theme, _ in theme_counts.most_common(5)]
                
                # Calculer le sentiment moyen
                cluster_sentiments = [analyses[idx].sentiment_score for idx in indices]
                avg_sentiment = float(np.mean(cluster_sentiments))
                
                # Centroïde
                cluster_embeddings = embeddings[indices]
                centroid = np.mean(cluster_embeddings, axis=0).tolist()
                
                # Créer le cluster
                cluster = Cluster(
                    cluster_label=f"Cluster {label}",
                    cluster_number=int(label),
                    size=len(indices),
                    representative_themes=top_themes,
                    avg_sentiment=avg_sentiment,
                    centroid=centroid
                )
                db.add(cluster)
                db.flush()  # Pour obtenir l'ID
                
                cluster_map[label] = cluster
            
            # Assigner les clusters aux analyses
            for i, label in enumerate(cluster_labels):
                if label != -1 and label in cluster_map:
                    analyses[i].cluster_id = cluster_map[label].id
            
            logger.info(f"Created {len(cluster_map)} clusters")
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
    
    def _update_global_themes_batch(
        self,
        themes_data: List[tuple],  # [(themes_list, language), ...]
        db: Session
    ) -> None:
        """
        Met à jour les thèmes globaux en batch pour éviter les duplicatas
        
        Args:
            themes_data: Liste de tuples (themes_list, language)
            db: Session
        """
        from collections import Counter
        
        # Compter tous les thèmes par langue
        theme_counts = {}
        for themes, language in themes_data:
            if language not in theme_counts:
                theme_counts[language] = Counter()
            theme_counts[language].update(themes)
        
        # Mettre à jour en batch
        for language, counter in theme_counts.items():
            for theme_name, count in counter.items():
                if not theme_name:
                    continue
                
                # Chercher si le thème existe déjà
                theme = db.query(Theme).filter(
                    Theme.theme_name == theme_name,
                    Theme.language == language
                ).first()
                
                if theme:
                    # Incrémenter la fréquence
                    theme.frequency += count
                else:
                    # Créer un nouveau thème
                    theme = Theme(
                        theme_name=theme_name,
                        frequency=count,
                        keywords=[theme_name],
                        language=language
                    )
                    db.add(theme)
        
        logger.info(f"Updated themes for {len(theme_counts)} languages")


# Instance globale
_nlp_service: Optional[NLPService] = None


def get_nlp_service() -> NLPService:
    """Retourne l'instance singleton de NLPService"""
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPService()
    return _nlp_service
