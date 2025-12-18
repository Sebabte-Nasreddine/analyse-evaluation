import React from 'react';
import { TrendingUp, Users, Settings, Target } from 'lucide-react';

const CATEGORY_CONFIG = {
    "Qualité de la Formation": {
        icon: Target,
        bgClass: "bg-blue-50",
        hoverClass: "hover:bg-blue-100",
        borderClass: "border-blue-200",
        iconBgClass: "bg-blue-100",
        iconColorClass: "text-blue-600",
        textColorClass: "text-blue-600",
        progressClass: "bg-blue-600",
        badgeBgClass: "bg-white",
        badgeTextClass: "text-blue-700",
        badgeBorderClass: "border-blue-300"
    },
    "Compétences du Formateur": {
        icon: Users,
        bgClass: "bg-green-50",
        hoverClass: "hover:bg-green-100",
        borderClass: "border-green-200",
        iconBgClass: "bg-green-100",
        iconColorClass: "text-green-600",
        textColorClass: "text-green-600",
        progressClass: "bg-green-600",
        badgeBgClass: "bg-white",
        badgeTextClass: "text-green-700",
        badgeBorderClass: "border-green-300"
    },
    "Organisation et Logistique": {
        icon: Settings,
        bgClass: "bg-yellow-50",
        hoverClass: "hover:bg-yellow-100",
        borderClass: "border-yellow-200",
        iconBgClass: "bg-yellow-100",
        iconColorClass: "text-yellow-600",
        textColorClass: "text-yellow-600",
        progressClass: "bg-yellow-600",
        badgeBgClass: "bg-white",
        badgeTextClass: "text-yellow-700",
        badgeBorderClass: "border-yellow-300"
    },
    "Applicabilité et Utilité": {
        icon: TrendingUp,
        bgClass: "bg-cyan-50",
        hoverClass: "hover:bg-cyan-100",
        borderClass: "border-cyan-200",
        iconBgClass: "bg-cyan-100",
        iconColorClass: "text-cyan-600",
        textColorClass: "text-cyan-600",
        progressClass: "bg-cyan-600",
        badgeBgClass: "bg-white",
        badgeTextClass: "text-cyan-700",
        badgeBorderClass: "border-cyan-300"
    }
};

export default function ThemeCategories({ categories }) {
    if (!categories || Object.keys(categories).length === 0) {
        return (
            <div className="text-center text-gray-500 py-8">
                Aucune catégorie de thème disponible
            </div>
        );
    }

    // Convertir en array et trier par fréquence
    const categoryArray = Object.entries(categories).map(([name, data]) => ({
        name,
        ...data
    })).sort((a, b) => b.total_frequency - a.total_frequency);

    return (
        <div className="space-y-4">
            {categoryArray.map((category, idx) => {
                const config = CATEGORY_CONFIG[category.name] || CATEGORY_CONFIG["Qualité de la Formation"];
                const Icon = config.icon;

                return (
                    <div
                        key={idx}
                        className={`p-4 rounded-lg border-2 ${config.borderClass} ${config.bgClass} ${config.hoverClass} transition-all duration-200`}
                    >
                        <div className="flex items-start gap-4">
                            {/* Icône */}
                            <div className={`p-3 rounded-lg ${config.iconBgClass}`}>
                                <Icon className={`h-6 w-6 ${config.iconColorClass}`} />
                            </div>

                            {/* Contenu */}
                            <div className="flex-1 min-w-0">
                                {/* Nom et pourcentage */}
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="text-lg font-semibold text-gray-900">
                                        {category.name}
                                    </h4>
                                    <span className={`text-2xl font-bold ${config.textColorClass}`}>
                                        {category.percentage}%
                                    </span>
                                </div>

                                {/* Statistiques */}
                                <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                                    <span>
                                        <strong>{category.total_frequency}</strong> mentions
                                    </span>
                                    <span>•</span>
                                    <span>
                                        <strong>{category.count}</strong> thèmes uniques
                                    </span>
                                </div>

                                {/* Barre de progression */}
                                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                                    <div
                                        className={`${config.progressClass} h-2 rounded-full transition-all duration-500`}
                                        style={{ width: `${category.percentage}%` }}
                                    />
                                </div>

                                {/* Top 5 thèmes de cette catégorie */}
                                {category.themes && category.themes.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-3">
                                        {category.themes.slice(0, 5).map((theme, i) => (
                                            <span
                                                key={i}
                                                className={`px-2 py-1 rounded-md text-xs font-medium ${config.badgeBgClass} ${config.badgeTextClass} border ${config.badgeBorderClass}`}
                                                title={`${theme.frequency} mentions`}
                                            >
                                                {theme.name} ({theme.frequency})
                                            </span>
                                        ))}
                                        {category.themes.length > 5 && (
                                            <span className="px-2 py-1 rounded-md text-xs text-gray-500">
                                                +{category.themes.length - 5} autres
                                            </span>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
