import React from 'react';

export default function ThemeCloud({ themes }) {
    if (!themes || themes.length === 0) {
        return (
            <div className="h-64 flex items-center justify-center text-gray-500">
                Aucun thème disponible
            </div>
        );
    }

    // Calculer les tailles basées sur la fréquence
    const maxFrequency = Math.max(...themes.map(t => t.frequency));
    const minSize = 14;
    const maxSize = 32;

    const getSize = (frequency) => {
        const normalized = frequency / maxFrequency;
        return minSize + (maxSize - minSize) * normalized;
    };

    const getColor = (index) => {
        const colors = [
            'text-primary-600',
            'text-success-600',
            'text-warning-600',
            'text-purple-600',
            'text-pink-600',
            'text-indigo-600',
        ];
        return colors[index % colors.length];
    };

    return (
        <div className="flex flex-wrap gap-4 p-6 justify-center items-center min-h-[200px]">
            {themes.map((theme, index) => (
                <span
                    key={index}
                    className={`font-semibold cursor-pointer hover:opacity-75 transition-opacity ${getColor(index)}`}
                    style={{ fontSize: `${getSize(theme.frequency)}px` }}
                    title={`Fréquence: ${theme.frequency}`}
                >
                    {theme.theme_name}
                </span>
            ))}
        </div>
    );
}
