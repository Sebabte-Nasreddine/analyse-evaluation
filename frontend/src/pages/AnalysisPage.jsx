import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, Download, Smile, Meh, Frown, ArrowUpDown, ArrowUp, ArrowDown, Star } from 'lucide-react';
import api from '../services/api';
import { categorizeThemes } from '../utils/themeHelper';

export default function AnalysisPage() {
    const [filters, setFilters] = useState({
        formation_type: '',
        formateur_id: '',
        langue: '',
        sentiment: '',
    });
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 20;

    const { data: evaluations, isLoading, refetch } = useQuery({
        queryKey: ['evaluations', filters],
        queryFn: () => api.getEvaluations(filters),
        staleTime: 0,
        refetchOnMount: 'always',
    });

    // Calculate statistics for filtered data
    const statistics = useMemo(() => {
        if (!evaluations || evaluations.length === 0) return null;

        const total = evaluations.length;
        const avgSat = evaluations.reduce((sum, e) => sum + e.satisfaction, 0) / total;
        const avgCont = evaluations.reduce((sum, e) => sum + e.contenu, 0) / total;
        const avgLog = evaluations.reduce((sum, e) => sum + e.logistique, 0) / total;
        const avgApp = evaluations.reduce((sum, e) => sum + e.applicabilite, 0) / total;

        const sentiments = evaluations.reduce((acc, e) => {
            if (e.analysis?.sentiment) {
                acc[e.analysis.sentiment] = (acc[e.analysis.sentiment] || 0) + 1;
            }
            return acc;
        }, {});

        return {
            total,
            avgSatisfaction: avgSat.toFixed(2),
            avgContenu: avgCont.toFixed(2),
            avgLogistique: avgLog.toFixed(2),
            avgApplicabilite: avgApp.toFixed(2),
            sentimentDistribution: sentiments
        };
    }, [evaluations]);

    // Sorting logic
    const sortedEvaluations = useMemo(() => {
        if (!evaluations) return [];

        let sorted = [...evaluations];

        if (sortConfig.key) {
            sorted.sort((a, b) => {
                let aVal, bVal;

                if (sortConfig.key === 'moyenne') {
                    aVal = (a.satisfaction + a.contenu + a.logistique + a.applicabilite) / 4;
                    bVal = (b.satisfaction + b.contenu + b.logistique + b.applicabilite) / 4;
                } else if (sortConfig.key === 'sentiment') {
                    aVal = a.analysis?.sentiment || '';
                    bVal = b.analysis?.sentiment || '';
                } else {
                    aVal = a[sortConfig.key];
                    bVal = b[sortConfig.key];
                }

                if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
                return 0;
            });
        }

        return sorted;
    }, [evaluations, sortConfig]);

    // Pagination
    const paginatedEvaluations = useMemo(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        return sortedEvaluations.slice(startIndex, startIndex + itemsPerPage);
    }, [sortedEvaluations, currentPage]);

    const totalPages = Math.ceil((sortedEvaluations?.length || 0) / itemsPerPage);

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    const getSortIcon = (key) => {
        if (sortConfig.key !== key) return <ArrowUpDown className="h-4 w-4 opacity-30" />;
        return sortConfig.direction === 'asc' ?
            <ArrowUp className="h-4 w-4" /> :
            <ArrowDown className="h-4 w-4" />;
    };

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

    const getScoreColor = (score) => {
        if (score >= 4.5) return 'text-success-600 font-semibold';
        if (score >= 3.5) return 'text-primary-600';
        if (score >= 2.5) return 'text-warning-600';
        return 'text-danger-600 font-semibold';
    };

    const exportToCSV = () => {
        if (!sortedEvaluations || sortedEvaluations.length === 0) return;

        const headers = ['Formation', 'Formateur', 'Satisfaction', 'Contenu', 'Logistique', 'Applicabilité', 'Moyenne', 'Sentiment', 'Langue', 'Commentaire'];
        const rows = sortedEvaluations.map(e => [
            e.type_formation,
            e.formateur_id,
            e.satisfaction,
            e.contenu,
            e.logistique,
            e.applicabilite,
            ((e.satisfaction + e.contenu + e.logistique + e.applicabilite) / 4).toFixed(2),
            e.analysis?.sentiment || 'N/A',
            e.langue,
            `"${e.commentaire.replace(/"/g, '""')}"`
        ]);

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evaluations_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between animate-fade-in">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Analyse Détaillée</h1>
                    <p className="text-gray-600 mt-1">Explorez toutes les évaluations avec critères complets</p>
                </div>
                <button className="btn-primary" onClick={exportToCSV} disabled={!evaluations || evaluations.length === 0}>
                    <Download className="h-4 w-4 mr-2" />
                    Exporter CSV
                </button>
            </div>

            {/* Statistics Summary */}
            {statistics && (
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 animate-fade-in">
                    <div className="stat-card">
                        <div className="stat-value text-primary-600">{statistics.total}</div>
                        <div className="stat-label">Évaluations</div>
                    </div>
                    <div className="stat-card">
                        <div className={`stat-value ${getScoreColor(parseFloat(statistics.avgSatisfaction))}`}>
                            {statistics.avgSatisfaction}
                        </div>
                        <div className="stat-label">Satisfaction</div>
                    </div>
                    <div className="stat-card">
                        <div className={`stat-value ${getScoreColor(parseFloat(statistics.avgContenu))}`}>
                            {statistics.avgContenu}
                        </div>
                        <div className="stat-label">Contenu</div>
                    </div>
                    <div className="stat-card">
                        <div className={`stat-value ${getScoreColor(parseFloat(statistics.avgLogistique))}`}>
                            {statistics.avgLogistique}
                        </div>
                        <div className="stat-label">Logistique</div>
                    </div>
                    <div className="stat-card">
                        <div className={`stat-value ${getScoreColor(parseFloat(statistics.avgApplicabilite))}`}>
                            {statistics.avgApplicabilite}
                        </div>
                        <div className="stat-label">Applicabilité</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="card animate-fade-in">
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
                            onChange={(e) => { setFilters({ ...filters, formation_type: e.target.value }); setCurrentPage(1); }}
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
                            onChange={(e) => { setFilters({ ...filters, formateur_id: e.target.value }); setCurrentPage(1); }}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Langue
                        </label>
                        <select
                            className="input"
                            value={filters.langue}
                            onChange={(e) => { setFilters({ ...filters, langue: e.target.value }); setCurrentPage(1); }}
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
                            onChange={(e) => { setFilters({ ...filters, sentiment: e.target.value }); setCurrentPage(1); }}
                        >
                            <option value="">Tous</option>
                            <option value="positive">Positif</option>
                            <option value="neutral">Neutre</option>
                            <option value="negative">Négatif</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Results Table */}
            <div className="card animate-fade-in">
                {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    </div>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('type_formation')}>
                                            <div className="flex items-center gap-1">
                                                Formation {getSortIcon('type_formation')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('formateur_id')}>
                                            <div className="flex items-center gap-1">
                                                Formateur {getSortIcon('formateur_id')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('satisfaction')}>
                                            <div className="flex items-center justify-center gap-1">
                                                Satisfaction {getSortIcon('satisfaction')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('contenu')}>
                                            <div className="flex items-center justify-center gap-1">
                                                Contenu {getSortIcon('contenu')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('logistique')}>
                                            <div className="flex items-center justify-center gap-1">
                                                Logistique {getSortIcon('logistique')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('applicabilite')}>
                                            <div className="flex items-center justify-center gap-1">
                                                Applicabilité {getSortIcon('applicabilite')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('moyenne')}>
                                            <div className="flex items-center justify-center gap-1">
                                                Moyenne {getSortIcon('moyenne')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                                            onClick={() => handleSort('sentiment')}>
                                            <div className="flex items-center gap-1">
                                                Sentiment {getSortIcon('sentiment')}
                                            </div>
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                            Commentaire
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {paginatedEvaluations?.map((evaluation, idx) => {
                                        const moyenne = ((evaluation.satisfaction + evaluation.contenu + evaluation.logistique + evaluation.applicabilite) / 4).toFixed(2);

                                        return (
                                            <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                                <td className="px-4 py-3">
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-900">
                                                            {evaluation.type_formation}
                                                        </div>
                                                        <div className="text-xs text-gray-500">{evaluation.formation_id}</div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700">
                                                    {evaluation.formateur_id}
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <div className={`text-sm font-medium ${getScoreColor(evaluation.satisfaction)}`}>
                                                        {evaluation.satisfaction}/5
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <div className={`text-sm font-medium ${getScoreColor(evaluation.contenu)}`}>
                                                        {evaluation.contenu}/5
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <div className={`text-sm font-medium ${getScoreColor(evaluation.logistique)}`}>
                                                        {evaluation.logistique}/5
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <div className={`text-sm font-medium ${getScoreColor(evaluation.applicabilite)}`}>
                                                        {evaluation.applicabilite}/5
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <div className={`text-lg font-bold ${getScoreColor(parseFloat(moyenne))}`}>
                                                        {moyenne}
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
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
                                                <td className="px-4 py-3">
                                                    <p className="text-sm text-gray-700 line-clamp-2 max-w-xs">
                                                        {evaluation.commentaire}
                                                    </p>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                            {sortedEvaluations?.length === 0 && (
                                <div className="text-center py-12 text-gray-500">
                                    Aucune évaluation trouvée
                                </div>
                            )}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-between px-6 py-4 border-t">
                                <div className="text-sm text-gray-700">
                                    Affichage <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> à{' '}
                                    <span className="font-medium">{Math.min(currentPage * itemsPerPage, sortedEvaluations.length)}</span> sur{' '}
                                    <span className="font-medium">{sortedEvaluations.length}</span> évaluations
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        className="btn-secondary"
                                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                        disabled={currentPage === 1}
                                    >
                                        Précédent
                                    </button>
                                    <div className="flex items-center gap-1">
                                        {[...Array(totalPages)].map((_, i) => (
                                            <button
                                                key={i}
                                                className={`px-3 py-1 rounded ${currentPage === i + 1 ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                                                onClick={() => setCurrentPage(i + 1)}
                                            >
                                                {i + 1}
                                            </button>
                                        ))}
                                    </div>
                                    <button
                                        className="btn-secondary"
                                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                        disabled={currentPage === totalPages}
                                    >
                                        Suivant
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
