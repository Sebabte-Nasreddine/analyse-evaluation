import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    TrendingUp,
    Users,
    BookOpen,
    ThumbsUp,
    Languages,
    Smile,
    Meh,
    Frown
} from 'lucide-react';
import api from '../services/api';
import SentimentChart from '../components/charts/SentimentChart';
import ThemeCategories from '../components/charts/ThemeCategories';
import TrendsChart from '../components/charts/TrendsChart';

export default function DashboardPage() {
    const { data: stats, isLoading } = useQuery({
        queryKey: ['dashboardStats'],
        queryFn: api.getDashboardStats,
    });

    const { data: insights } = useQuery({
        queryKey: ['insights'],
        queryFn: () => api.getInsights({ limit: 5 }),
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    const statCards = [
        {
            label: 'Total Évaluations',
            value: stats?.total_evaluations || 0,
            icon: BookOpen,
            color: 'primary',
        },
        {
            label: 'Satisfaction Moyenne',
            value: stats?.avg_satisfaction?.toFixed(2) || '0',
            suffix: '/5',
            icon: ThumbsUp,
            color: 'success',
        },
        {
            label: 'Qualité Contenu',
            value: stats?.avg_contenu?.toFixed(2) || '0',
            suffix: '/5',
            icon: TrendingUp,
            color: 'primary',
        },
        {
            label: 'Applicabilité',
            value: stats?.avg_applicabilite?.toFixed(2) || '0',
            suffix: '/5',
            icon: Users,
            color: 'warning',
        },
    ];

    const getSentimentIcon = (sentiment) => {
        switch (sentiment) {
            case 'positive': return Smile;
            case 'negative': return Frown;
            default: return Meh;
        }
    };

    const getSentimentColor = (sentiment) => {
        switch (sentiment) {
            case 'positive': return 'text-success-600';
            case 'negative': return 'text-danger-600';
            default: return 'text-gray-600';
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600 mt-1">Vue d'ensemble des évaluations de formation</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-fade-in">
                {statCards.map((stat, idx) => {
                    const Icon = stat.icon;
                    return (
                        <div key={idx} className="stat-card hover:scale-105 transition-transform">
                            <div className="flex items-center justify-between">
                                <div className={`p-3 bg-${stat.color}-100 rounded-lg`}>
                                    <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                                </div>
                            </div>
                            <div className="mt-4">
                                <div className="stat-value">
                                    {stat.value}
                                    {stat.suffix && <span className="text-xl text-gray-500">{stat.suffix}</span>}
                                </div>
                                <div className="stat-label">{stat.label}</div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Sentiment Distribution */}
                <div className="card animate-fade-in">
                    <div className="card-header">
                        <h3 className="text-lg font-semibold">Distribution des Sentiments</h3>
                    </div>
                    <SentimentChart data={stats?.sentiment_distribution || {}} />
                </div>

                {/* Language Distribution */}
                <div className="card animate-fade-in">
                    <div className="card-header">
                        <div className="flex items-center gap-2">
                            <Languages className="h-5 w-5 text-primary-600" />
                            <h3 className="text-lg font-semibold">Distribution par Langue</h3>
                        </div>
                    </div>
                    <div className="space-y-4">
                        {Object.entries(stats?.language_distribution || {}).map(([lang, count]) => {
                            const total = Object.values(stats?.language_distribution || {}).reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;

                            return (
                                <div key={lang} className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="font-medium text-gray-700">{lang}</span>
                                        <span className="text-gray-500">{count} ({percentage}%)</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Theme Categories & Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Theme Categories */}
                <div className="lg:col-span-2 card animate-fade-in">
                    <div className="card-header">
                        <h3 className="text-lg font-semibold">Catégories de Thèmes</h3>
                        <p className="text-sm text-gray-500 mt-1">4 grandes catégories identifiées</p>
                    </div>
                    <ThemeCategories categories={stats?.theme_categories || {}} />
                </div>

                {/* Recent Insights */}
                <div className="card animate-fade-in">
                    <div className="card-header">
                        <h3 className="text-lg font-semibold">Insights Récents</h3>
                    </div>
                    <div className="space-y-3">
                        {insights?.slice(0, 5).map((insight, idx) => (
                            <div
                                key={idx}
                                className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                            >
                                <div className="flex items-start gap-2">
                                    <div className={`mt-1 ${insight.insight_type === 'alert' ? 'text-danger-500' :
                                        insight.insight_type === 'recommendation' ? 'text-success-500' :
                                            'text-primary-500'
                                        }`}>
                                        •
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900 line-clamp-1">
                                            {insight.title}
                                        </p>
                                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                                            {insight.description}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )) || (
                                <p className="text-sm text-gray-500 text-center py-4">
                                    Aucun insight disponible
                                </p>
                            )}
                    </div>
                </div>
            </div>

            {/* Formation Types */}
            <div className="card animate-fade-in">
                <div className="card-header">
                    <h3 className="text-lg font-semibold">Évaluations par Type de Formation</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(stats?.formation_types || {}).map(([type, count]) => (
                        <div key={type} className="p-4 bg-gray-50 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between">
                                <span className="font-medium text-gray-900">{type}</span>
                                <span className="text-2xl font-bold text-primary-600">{count}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
