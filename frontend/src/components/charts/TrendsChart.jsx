import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function TrendsChart({ data }) {
    if (!data || data.length === 0) {
        return (
            <div className="h-64 flex items-center justify-center text-gray-500">
                Aucune donnée de tendance disponible
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="satisfaction" stroke="#0ea5e9" strokeWidth={2} />
                <Line type="monotone" dataKey="contenu" stroke="#22c55e" strokeWidth={2} />
                <Line type="monotone" dataKey="logistique" stroke="#f59e0b" strokeWidth={2} />
                <Line type="monotone" dataKey="applicabilite" stroke="#8b5cf6" strokeWidth={2} />
            </LineChart>
        </ResponsiveContainer>
    );
}
