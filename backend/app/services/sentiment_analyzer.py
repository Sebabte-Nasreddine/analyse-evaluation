"""
Service d'analyse de sentiment multilingue utilisant Hugging Face API
"""
import requests
from typing import Dict, Tuple, Optional
import logging
import os
from app.core.config import settings
from app.models.models import LanguageEnum, SentimentEnum

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyseur de sentiment avec modèles spécialisés par langue via Hugging Face API
    """
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.api_url = "https://api-inference.huggingface.co/models/"
        
        # URLs des modèles par langue
        self.models = {
            LanguageEnum.FRENCH.value: settings.FRENCH_SENTIMENT_MODEL,
            LanguageEnum.ARABIC.value: settings.ARABIC_SENTIMENT_MODEL,
            LanguageEnum.DARIJA.value: settings.DARIJA_MODEL,
        }
        
        logger.info("SentimentAnalyzer initialized with Hugging Face API")
    
    def _query_api(self, model_name: str, text: str) -> Optional[Dict]:
        """
        Interroge l'API Hugging Face
        
        Args:
            model_name: Nom du modèle
            text: Texte à analyser
            
        Returns:
            Résultat de l'API ou None si erreur
        """
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        url = f"{self.api_url}{model_name}"
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"inputs": text[:512]},  # Limiter la longueur
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # L'API retourne une liste, prendre le premier élément
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], list):
                        return result[0][0] if result[0] else None
                    return result[0]
            else:
                logger.warning(f"API returned status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            return None
    
    def analyze(self, text: str, language: str) -> Dict[str, any]:
        """
        Analyse le sentiment d'un texte via Hugging Face API
        
        Args:
            text: Texte à analyser
            language: Code langue (FR, AR, DARIJA)
            
        Returns:
            Dict avec sentiment, score, et label
        """
        if not text or not text.strip():
            return {
                "sentiment": SentimentEnum.NEUTRAL.value,
                "score": 0.0,
                "confidence": 0.0,
                "label": "neutral"
            }
        
        # Sélectionner le modèle approprié
        model_name = self.models.get(language, self.models[LanguageEnum.FRENCH.value])
        
        # Interroger l'API
        result = self._query_api(model_name, text)
        
        if result:
            try:
                # Normaliser le résultat
                sentiment, score = self._normalize_sentiment(result)
                
                return {
                    "sentiment": sentiment,
                    "score": score,
                    "confidence": result.get("score", 0.0),
                    "label": result.get("label", "neutral")
                }
            except Exception as e:
                logger.error(f"Error normalizing API result: {e}")
        
        # Fallback sur analyse règle-based simple
        logger.info(f"Using rule-based sentiment analysis for: {text[:50]}...")
        return self._rule_based_sentiment(text)
    
    def _normalize_sentiment(self, result: Dict) -> Tuple[str, float]:
        """
        Normalise le résultat du modèle vers notre format standard
        
        Args:
            result: Résultat du pipeline
            
        Returns:
            Tuple (sentiment, score) où score est entre -1 (négatif) et 1 (positif)
        """
        label = result.get("label", "").lower()
        confidence = result.get("score", 0.5)
        
        CONFIDENCE_THRESHOLD = 0.55  # 55% confidence minimum
        
        # Mapper les labels vers notre format
        if any(pos in label for pos in ["pos", "positive", "1", "5_stars", "4_stars"]):
            if confidence >= CONFIDENCE_THRESHOLD:
                sentiment = SentimentEnum.POSITIVE.value
                score = confidence
            else:
                # Confiance faible → neutral
                sentiment = SentimentEnum.NEUTRAL.value
                score = 0.0
        elif any(neg in label for neg in ["neg", "negative", "0", "1_star", "2_stars"]):
            if confidence >= CONFIDENCE_THRESHOLD:
                sentiment = SentimentEnum.NEGATIVE.value
                score = -confidence
            else:
                # Confiance faible → neutral
                sentiment = SentimentEnum.NEUTRAL.value
                score = 0.0
        elif any(neu in label for neu in ["neu", "neutral", "3_stars"]):
            # Neutre explicite
            sentiment = SentimentEnum.NEUTRAL.value
            score = 0.0
        else:
            # Label inconnu → neutral par défaut
            sentiment = SentimentEnum.NEUTRAL.value
            score = 0.0
        
        return sentiment, score
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyse de sentiment basée sur des règles simples (fallback)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict avec sentiment et score
        """
        text_lower = text.lower()
        
        # Mots positifs (multilingue)
        positive_words = {
            # Français
            'excellent', 'très bien', 'parfait', 'super', 'génial', 'bon', 'bien',
            'satisfait', 'satisfaisant', 'intéressant', 'utile', 'efficace',
            'professionnel', 'compétent', 'clair', 'dynamique', 'enrichissant',
            'pertinent', 'recommande',
            # Arabe
            'ممتاز', 'جيد', 'مفيد', 'رائع',
            # Darija
            'mezyan', 'mzyan', 'zwina', 'labas', 'top', 'kamel'
        }
        
        # Mots négatifs (multilingue) - ÉLARGI pour mieux détecter
        negative_words = {
            # Français
            'mauvais', 'nul', 'décevant', 'déçu', 'insatisfait', 'problème', 'difficile',
            'compliqué', 'incompréhensible', 'ennuyeux', 'perte de temps', 'catastrophe',
            'inutile', 'médiocre', 'faible', 'horrible', 'terrible', 'désastre',
            'incompétent', 'mal', 'pire', 'vide', 'superficiel', 'obsolète',
            'périmé', 'désengagé', 'agressif', 'fausse', 'erreur', 'pas terrible',
            'manque', 'moyenne', 'correct sans plus', 'pas claire', 
            # Arabe
            'سيء', 'سيئة', 'ضعيف', 'قديم', 'غير', 'لا', 'مضيعة',
            # Darija  
            'khayb', 'khayba', 'machi mezyan', 'ma3lich', 'khsara', 'walo',
            'ma kanet', 'f9ir', 'katastroph'
        }
        
        # Compter les occurrences
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Déterminer le sentiment avec seuil plus bas pour négatif
        if neg_count > 0 and neg_count >= pos_count:  # Favoriser négatif si égalité
            return {
                "sentiment": SentimentEnum.NEGATIVE.value,
                "score": -min(0.8, 0.5 + (neg_count * 0.15)),  # Plus négatif avec plus de mots
                "confidence": min(0.75, 0.5 + (neg_count * 0.1)),
                "label": "negative (rule-based)"
            }
        elif pos_count > neg_count:
            return {
                "sentiment": SentimentEnum.POSITIVE.value,
                "score": min(0.8, 0.5 + (pos_count * 0.15)),
                "confidence": min(0.75, 0.5 + (pos_count * 0.1)),
                "label": "positive (rule-based)"
            }
        else:
            return {
                "sentiment": SentimentEnum.NEUTRAL.value,
                "score": 0.0,
                "confidence": 0.5,
                "label": "neutral (rule-based)"
            }
    
    def analyze_batch(self, texts: list[str], languages: list[str]) -> list[Dict]:
        """
        Analyse un batch de textes
        
        Args:
            texts: Liste de textes
            languages: Liste de codes langue correspondants
            
        Returns:
            Liste de résultats d'analyse
        """
        results = []
        for text, lang in zip(texts, languages):
            results.append(self.analyze(text, lang))
        return results


# Instance globale (singleton)
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Retourne l'instance singleton de SentimentAnalyzer"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
