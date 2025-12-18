import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Lightbulb, TrendingUp, AlertTriangle, Award, Info } from 'lucide-react';
import api from '../services/api';

const INSIGHT_ICONS = {
    trend: TrendingUp,
    tendance: TrendingUp,  // French version
    alert: AlertTriangle,
    recommendation: Award,
    signal_faible: AlertTriangle,  // Weak signal icon
    correlation: Info,
};

const INSIGHT_CONFIG = {
    trend: { bgClass: 'bg-blue-100', textClass: 'text-blue-600', borderClass: 'border-blue-500', cardBgClass: 'bg-blue-50' },
    tendance: { bgClass: 'bg-blue-100', textClass: 'text-blue-600', borderClass: 'border-blue-500', cardBgClass: 'bg-blue-50' },
    alert: { bgClass: 'bg-red-100', textClass: 'text-red-600', borderClass: 'border-red-500', cardBgClass: 'bg-red-50' },
    signal_faible: { bgClass: 'bg-red-100', textClass: 'text-red-600', borderClass: 'border-red-500', cardBgClass: 'bg-red-50' },  // RED for weak signals
    recommendation: { bgClass: 'bg-green-100', textClass: 'text-green-600', borderClass: 'border-green-500', cardBgClass: 'bg-green-50' },
    correlation: { bgClass: 'bg-yellow-100', textClass: 'text-yellow-600', borderClass: 'border-yellow-500', cardBgClass: 'bg-yellow-50' },
};

export default function InsightsPage() {
    const { data: insights, isLoading } = useQuery({
        queryKey: ['insights'],
        queryFn: () => api.getInsights({ limit: 20 }),
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    const groupedInsights = insights?.reduce((acc, insight) => {
        if (!acc[insight.insight_type]) {
            acc[insight.insight_type] = [];
        }
        acc[insight.insight_type].push(insight);
        return acc;
    }, {}) || {};

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Insights Automatiques</h1>
                    <p className="text-gray-600 mt-1">
                        Découvertes et recommandations générées par l'analyse IA
                    </p>
                </div>
                <button
                    className="btn-primary"
                    onClick={() => api.generateInsights()}
                >
                    <Lightbulb className="h-4 w-4 mr-2" />
                    Générer nouveaux insights
                </button>
            </div>

            {Object.entries(groupedInsights).map(([type, typeInsights]) => {
                const Icon = INSIGHT_ICONS[type] || Info;
                const config = INSIGHT_CONFIG[type] || INSIGHT_CONFIG.trend;

                return (
                    <div key={type} className="card">
                        <div className="card-header">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${config.bgClass}`}>
                                    <Icon className={`h-5 w-5 ${config.textClass}`} />
                                </div>
                                <h2 className="text-xl font-semibold capitalize">
                                    {type}s ({typeInsights.length})
                                </h2>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {typeInsights.map((insight, idx) => (
                                <div
                                    key={idx}
                                    className={`p-4 border-l-4 rounded-r-lg ${config.cardBgClass} ${config.borderClass}`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-gray-900 mb-2">
                                                {insight.title}
                                            </h3>
                                            <p className="text-sm text-gray-700 mb-3">
                                                {insight.description}
                                            </p>

                                            {insight.data && (
                                                <div className="mt-3 p-3 bg-white rounded-lg">
                                                    <p className="text-xs font-medium text-gray-500 mb-2">
                                                        Données associées:
                                                    </p>
                                                    <pre className="text-xs text-gray-700 overflow-x-auto">
                                                        {JSON.stringify(insight.data, null, 2)}
                                                    </pre>
                                                </div>
                                            )}
                                        </div>

                                        <div className="ml-4 flex items-center gap-2">
                                            <div className={`px-3 py-1 rounded-full ${config.bgClass}`}>
                                                <span className={`text-sm font-medium ${config.textClass}`}>
                                                    {(insight.confidence * 100).toFixed(0)}% confiance
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
                                        <span>
                                            Généré le {new Date(insight.created_at).toLocaleDateString('fr-FR')}
                                        </span>
                                        {insight.formation_type && (
                                            <span className="badge badge-neutral">
                                                {insight.formation_type}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}

            {insights?.length === 0 && (
                <div className="card text-center py-12">
                    <Lightbulb className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 mb-4">
                        Aucun insight disponible pour le moment
                    </p>
                    <button className="btn-primary" onClick={() => api.generateInsights()}>
                        Générer les premiers insights
                    </button>
                </div>
            )}
        </div>
    );
}
