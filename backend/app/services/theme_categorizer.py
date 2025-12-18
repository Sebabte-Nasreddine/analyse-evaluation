"""
Service de catégorisation des thèmes en 4 catégories générales
"""
from typing import Dict, List
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Theme


class ThemeCategorizer:
    """Catégorise les thèmes en 4 grandes catégories"""
    
    # Mapping des mots-clés vers les catégories (multilingue)
    CATEGORIES = {
        "Qualité de la Formation": {
            "keywords_fr": ["formation", "contenu", "qualité", "niveau", "profondeur", "structuré", "organisé", 
                           "excellent", "bon", "mauvais", "nul", "obsolète", "périmé", "nouveau", "clair",
                           "théorique", "pratique", "exemples", "exercices", "cas"],
            "keywords_ar": ["تدريب", "محتوى", "المحتوى", "جودة", "ممتاز", "جيد", "سيء", "قديم", "جداً", 
                           "واضح", "مفيد", "نظري", "عملي", "أمثلة"],
            "keywords_darija": ["formation", "contenu", "niveau", "mezyana", "mzyana", "khayba", "top", 
                              "zina", "practique", "exemples"]
        },
        "Compétences du Formateur": {
            "keywords_fr": ["formateur", "instructeur", "prof", "enseignant", "compétent", "incompétent",
                           "préparé", "professionnel", "dynamique", "passionné", "engageant", "monotone",
                           "maîtrise", "expert", "expérience", "pédagogique", "communication"],
            "keywords_ar": ["مدرب", "المدرب", "معلم", "محترف", "مؤهل", "خبرة", "شرح", "يشرح", "تفسير",
                           "مستعد", "جاهز"],
            "keywords_darija": ["formateur", "prof", "instructor", "maalem", "professionnel", "kamel",
                              "ma3arafch", "khatar"]
        },
        "Organisation et Logistique": {
            "keywords_fr": ["logistique", "organisation", "organisé", "salle", "équipement", "matériel",
                           "supports", "horaire", "temps", "durée", "pause", "accueil", "réservation",
                           "planification", "coordination", "infrastructure"],
            "keywords_ar": ["تنظيم", "قاعة", "القاعة", "مكان", "وقت", "الوقت", "ساعات", "مدة", "مرافق",
                           "معدات", "صوت"],
            "keywords_darija": ["organisation", "qa3a", "blassa", "waqt", "lwaqt", "ma9an", "organisation"]
        },
        "Applicabilité et Utilité": {
            "keywords_fr": ["applicable", "applicabilité", "utile", "pratique", "concret", "réaliste",
                           "pertinent", "efficace", "recommande", "valeur", "bénéfice", "impact",
                           "résultat", "amélioration", "compétences", "apprises", "acquérir"],
            "keywords_ar": ["تطبيق", "التطبيق", "عملي", "مفيد", "فائدة", "نتيجة", "تحسين", "مهارات",
                           "استفدت", "استفادة", "واقعي"],
            "keywords_darija": ["practique", "fayda", "nafed", "ستفدت", "3jbni", "mazyan", "t3allemt",
                              "استفدت"]
        }
    }
    
    @classmethod
    def categorize_theme(cls, theme_name: str, language: str) -> str:
        """
        Catégorise un thème dans une des 4 catégories
        
        Args:
            theme_name: Nom du thème
            language: Code langue (FR, AR, DARIJA)
            
        Returns:
            Nom de la catégorie
        """
        theme_lower = theme_name.lower()
        
        # Vérifier chaque catégorie
        for category, keywords in cls.CATEGORIES.items():
            # Sélectionner les bons keywords selon la langue
            if language == "FR":
                relevant_keywords = keywords.get("keywords_fr", [])
            elif language == "AR":
                relevant_keywords = keywords.get("keywords_ar", [])
            elif language == "DARIJA":
                relevant_keywords = keywords.get("keywords_darija", [])
            else:
                relevant_keywords = keywords.get("keywords_fr", [])  # Fallback
            
            # Vérifier si le thème contient un des mots-clés
            for keyword in relevant_keywords:
                if keyword in theme_lower or theme_lower in keyword:
                    return category
        
        # Par défaut, catégoriser dans "Qualité de la Formation"
        return "Qualité de la Formation"
    
    @classmethod
    def get_categorized_themes(cls, db: Session, top_n: int = 50) -> Dict[str, Dict]:
        """
        Récupère les thèmes et les groupe par catégorie
        
        Args:
            db: Session de base de données
            top_n: Nombre de thèmes à analyser
            
        Returns:
            Dict avec les 4 catégories et leurs stats
        """
        # Récupérer les top thèmes
        themes = db.query(Theme).order_by(desc(Theme.frequency)).limit(top_n).all()
        
        # Initialiser les catégories
        categories = {
            "Qualité de la Formation": {"count": 0, "total_frequency": 0, "themes": []},
            "Compétences du Formateur": {"count": 0, "total_frequency": 0, "themes": []},
            "Organisation et Logistique": {"count": 0, "total_frequency": 0, "themes": []},
            "Applicabilité et Utilité": {"count": 0, "total_frequency": 0, "themes": []}
        }
        
        # Catégoriser chaque thème
        for theme in themes:
            category = cls.categorize_theme(theme.theme_name, theme.language)
            
            categories[category]["count"] += 1
            categories[category]["total_frequency"] += theme.frequency
            categories[category]["themes"].append({
                "name": theme.theme_name,
                "frequency": theme.frequency,
                "language": theme.language
            })
        
        # Calculer le pourcentage pour chaque catégorie
        total_frequency = sum(cat["total_frequency"] for cat in categories.values())
        
        for category in categories:
            if total_frequency > 0:
                categories[category]["percentage"] = round(
                    (categories[category]["total_frequency"] / total_frequency) * 100, 1
                )
            else:
                categories[category]["percentage"] = 0
        
        return categories


# Instance pour export
theme_categorizer = ThemeCategorizer()
