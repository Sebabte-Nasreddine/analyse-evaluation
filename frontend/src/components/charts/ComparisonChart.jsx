import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ComparisonChart({ data }) {
    const chartData = [
        {
            name: 'Critères',
            Satisfaction: parseFloat(data?.avg_satisfaction || 0),
            Contenu: parseFloat(data?.avg_contenu || 0),
            Logistique: parseFloat(data?.avg_logistique || 0),
            Applicabilité: parseFloat(data?.avg_applicabilite || 0),
        }
    ];


    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 5]} ticks={[0, 1, 2, 3, 4, 5]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Satisfaction" fill="#10b981" radius={[8, 8, 0, 0]} />
                <Bar dataKey="Contenu" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                <Bar dataKey="Logistique" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                <Bar dataKey="Applicabilité" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
        </ResponsiveContainer>
    );
}
