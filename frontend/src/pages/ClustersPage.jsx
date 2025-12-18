import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Group } from 'lucide-react';
import api from '../services/api';
import { categorizeThemes } from '../utils/themeHelper';

export default function ClustersPage() {
    const { data: clusters, isLoading } = useQuery({
        queryKey: ['clusters'],
        queryFn: api.getClusters,
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    const getSentimentColor = (score) => {
        if (score > 0.3) return 'text-success-600';
        if (score < -0.3) return 'text-danger-600';
        return 'text-gray-600';
    };

    const getSentimentBg = (score) => {
        if (score > 0.3) return 'bg-success-50 border-success-200';
        if (score < -0.3) return 'bg-danger-50 border-danger-200';
        return 'bg-gray-50 border-gray-200';
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Clusters d'Évaluations</h1>
                <p className="text-gray-600 mt-1">
                    Groupes d'évaluations similaires identifiés par algorithme de clustering
                </p>
            </div>

            {clusters && clusters.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {clusters.map((cluster, idx) => (
                        <div
                            key={idx}
                            className={`card border-2 ${getSentimentBg(cluster.avg_sentiment)}`}
                        >
                            <div className="card-header">
                                <div className="flex items-center justify-between w-full">
                                    <div className="flex items-center gap-3">
                                        <div className="p-3 bg-primary-100 rounded-lg">
                                            <Group className="h-6 w-6 text-primary-600" />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">
                                                {cluster.cluster_label}
                                            </h3>
                                            <p className="text-sm text-gray-500">
                                                {cluster.size} évaluations
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-2xl font-bold ${getSentimentColor(cluster.avg_sentiment)}`}>
                                            {cluster.avg_sentiment > 0 ? '+' : ''}
                                            {cluster.avg_sentiment.toFixed(2)}
                                        </div>
                                        <p className="text-xs text-gray-500">Sentiment moyen</p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-gray-700 mb-3">
                                    Catégories de thèmes:
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                    {cluster.representative_themes && (() => {
                                        // Catégoriser les thèmes bruts
                                        const categories = categorizeThemes(cluster.representative_themes, 'FR');
                                        return categories.length > 0 ? categories.map((category, i) => (
                                            <span
                                                key={i}
                                                className="px-3 py-1 bg-blue-50 border border-blue-300 rounded-lg text-sm font-medium text-blue-700"
                                            >
                                                {category}
                                            </span>
                                        )) : (
                                            <span className="text-sm text-gray-400">Aucune catégorie identifiée</span>
                                        );
                                    })()}
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-gray-200">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-gray-600">Cluster #{cluster.cluster_number}</span>
                                    <span className="text-gray-500">
                                        {((cluster.size / clusters.reduce((sum, c) => sum + c.size, 0)) * 100).toFixed(1)}%
                                        du total
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card text-center py-12 text-gray-500">
                    Aucun cluster disponible. Uploadez plus d'évaluations pour activer le clustering.
                </div>
            )}
        </div>
    );
}
