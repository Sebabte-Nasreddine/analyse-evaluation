import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, Download, Smile, Meh, Frown } from 'lucide-react';
import api from '../services/api';
import { categorizeThemes } from '../utils/themeHelper';

export default function AnalysisPage() {
    const [filters, setFilters] = useState({
        formation_type: '',
        formateur_id: '',
        langue: '',
        sentiment: '',
    });

    const { data: evaluations, isLoading, refetch } = useQuery({
        queryKey: ['evaluations', filters],
        queryFn: () => api.getEvaluations(filters),
        staleTime: 0,  // Always fetch fresh data
        refetchOnMount: 'always',  // Refetch when page loads
    });

    const getSentimentIcon = (sentiment) => {
        switch (sentiment) {
            case 'positive': return <Smile className="h-5 w-5 text-success-600" />;
            case 'negative': return <Frown className="h-5 w-5 text-danger-600" />;
            default: return <Meh className="h-5 w-5 text-gray-600" />;
        }
    };

    const getSentimentBadge = (sentiment) => {
        switch (sentiment) {
            case 'positive': return 'badge-success';
            case 'negative': return 'badge-danger';
            default: return 'badge-neutral';
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Analyse Détaillée</h1>
                    <p className="text-gray-600 mt-1">Explorez les évaluations avec analyses NLP</p>
                </div>
                <button className="btn-primary">
                    <Download className="h-4 w-4 mr-2" />
                    Exporter
                </button>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="card-header">
                    <div className="flex items-center gap-2">
                        <Filter className="h-5 w-5 text-gray-600" />
                        <h3 className="text-lg font-semibold">Filtres</h3>
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Type de Formation
                        </label>
                        <input
                            type="text"
                            className="input"
                            placeholder="Tous"
                            value={filters.formation_type}
                            onChange={(e) => setFilters({ ...filters, formation_type: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Formateur
                        </label>
                        <input
                            type="text"
                            className="input"
                            placeholder="Tous"
                            value={filters.formateur_id}
                            onChange={(e) => setFilters({ ...filters, formateur_id: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Langue
                        </label>
                        <select
                            className="input"
                            value={filters.langue}
                            onChange={(e) => setFilters({ ...filters, langue: e.target.value })}
                        >
                            <option value="">Toutes</option>
                            <option value="FR">Français</option>
                            <option value="AR">Arabe</option>
                            <option value="DARIJA">Darija</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Sentiment
                        </label>
                        <select
                            className="input"
                            value={filters.sentiment}
                            onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}
                        >
                            <option value="">Tous</option>
                            <option value="positive">Positif</option>
                            <option value="neutral">Neutre</option>
                            <option value="negative">Négatif</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Results */}
            <div className="card">
                {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                        Formation
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                        Formateur
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                        Satisfaction
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                        Sentiment
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                        Thèmes
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                        Commentaire
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {evaluations?.map((evaluation, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">
                                                    {evaluation.type_formation}
                                                </div>
                                                <div className="text-xs text-gray-500">{evaluation.formation_id}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {evaluation.formateur_id}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-sm font-medium text-gray-900">
                                                {evaluation.satisfaction}/5
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {evaluation.analysis ? (
                                                <div className="flex items-center gap-2">
                                                    {getSentimentIcon(evaluation.analysis.sentiment)}
                                                    <span className={`badge ${getSentimentBadge(evaluation.analysis.sentiment)}`}>
                                                        {evaluation.analysis.sentiment}
                                                    </span>
                                                </div>
                                            ) : (
                                                <span className="text-gray-400 text-sm">N/A</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-wrap gap-1">
                                                {evaluation.analysis?.themes && (() => {
                                                    const categories = categorizeThemes(evaluation.analysis.themes, evaluation.langue);
                                                    return categories.map((category, i) => (
                                                        <span key={i} className="badge badge-primary text-xs">
                                                            {category}
                                                        </span>
                                                    ));
                                                })()}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <p className="text-sm text-gray-700 line-clamp-2 max-w-xs">
                                                {evaluation.commentaire}
                                            </p>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {evaluations?.length === 0 && (
                            <div className="text-center py-12 text-gray-500">
                                Aucune évaluation trouvée
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
