/**
 * Helper to categorize individual themes into 4 general categories
 * Mirrors the backend categorization logic
 */

const CATEGORY_KEYWORDS = {
    "Qualité": {
        fr: ["formation", "contenu", "qualité", "niveau", "excellent", "bon", "mauvais", "obsolète", "théorique", "pratique", "exemples"],
        ar: ["تدريب", "محتوى", "المحتوى", "جودة", "ممتاز", "جيد"],
        darija: ["formation", "contenu", "mezyana", "mzyana", "khayba", "top"]
    },
    "Formateur": {
        fr: ["formateur", "instructeur", "prof", "enseignant", "compétent", "professionnel"],
        ar: ["مدرب", "المدرب", "محترف"],
        darija: ["formateur", "prof", "instructor", "professionnel", "kamel"]
    },
    "Logistique": {
        fr: ["logistique", "organisation", "salle", "équipement", "matériel", "supports"],
        ar: ["تنظيم", "قاعة", "القاعة"],
        darija: ["organisation", "qa3a", "waqt"]
    },
    "Utilité": {
        fr: ["applicable", "utile", "pratique", "pertinent", "recommande"],
        ar: ["تطبيق", "مفيد", "عملي"],
        darija: ["practique", "fayda", "استفدت"]
    }
};

export function categorizeTheme(theme, language = "FR") {
    if (!theme) return "Autre";

    const themeLower = theme.toLowerCase();
    const lang = language.toLowerCase();

    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
        const relevantKeywords = keywords[lang] || keywords.fr;

        for (const keyword of relevantKeywords) {
            if (themeLower.includes(keyword) || keyword.includes(themeLower)) {
                return category;
            }
        }
    }

    return "Autre";
}

export function categorizeThemes(themes, language = "FR") {
    if (!themes || themes.length === 0) return [];

    const categories = new Set();
    themes.forEach(theme => {
        const category = categorizeTheme(theme, language);
        if (category !== "Autre") {
            categories.add(category);
        }
    });

    return Array.from(categories);
}
