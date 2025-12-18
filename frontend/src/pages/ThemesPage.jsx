import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Tags } from 'lucide-react';
import api from '../services/api';

export default function ThemesPage() {
    const { data: themes, isLoading } = useQuery({
        queryKey: ['themes'],
        queryFn: () => api.getThemes({ top_n: 50 }),
    });

    const groupedByLanguage = themes?.reduce((acc, theme) => {
        if (!acc[theme.language]) {
            acc[theme.language] = [];
        }
        acc[theme.language].push(theme);
        return acc;
    }, {}) || {};

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Thèmes Extraits</h1>
                <p className="text-gray-600 mt-1">
                    Thèmes identifiés automatiquement par NLP à partir des commentaires
                </p>
            </div>

            {Object.entries(groupedByLanguage).map(([language, languageThemes]) => (
                <div key={language} className="card">
                    <div className="card-header">
                        <div className="flex items-center gap-2">
                            <Tags className="h-5 w-5 text-primary-600" />
                            <h2 className="text-xl font-semibold">
                                {language} - {languageThemes.length} thèmes
                            </h2>
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {languageThemes.map((theme, idx) => (
                            <div
                                key={idx}
                                className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg hover:shadow-md transition-shadow"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <h3 className="font-semibold text-gray-900 mb-1">
                                            {theme.theme_name}
                                        </h3>
                                        <div className="flex flex-wrap gap-1 mb-2">
                                            {theme.keywords?.map((keyword, i) => (
                                                <span key={i} className="badge badge-neutral text-xs">
                                                    {keyword}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="ml-3">
                                        <div className="bg-primary-600 text-white rounded-full px-3 py-1 text-sm font-bold">
                                            {theme.frequency}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}

            {themes?.length === 0 && (
                <div className="card text-center py-12 text-gray-500">
                    Aucun thème disponible. Uploadez des évaluations pour commencer l'analyse.
                </div>
            )}
        </div>
    );
}
