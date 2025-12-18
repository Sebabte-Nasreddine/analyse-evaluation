import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import AnalysisPage from './pages/AnalysisPage';

import ClustersPage from './pages/ClustersPage';
import InsightsPage from './pages/InsightsPage';

// Configuration React Query
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1,
            staleTime: 5 * 60 * 1000, // 5 minutes
        },
    },
});

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Router>
                <Layout>
                    <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/upload" element={<UploadPage />} />
                        <Route path="/analysis" element={<AnalysisPage />} />

                        <Route path="/clusters" element={<ClustersPage />} />
                        <Route path="/insights" element={<InsightsPage />} />
                    </Routes>
                </Layout>
            </Router>
        </QueryClientProvider>
    );
}

export default App;
