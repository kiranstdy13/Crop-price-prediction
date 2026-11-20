import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';

import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

import FarmerDashboard from './pages/FarmerDashboard';
import PredictionPage from './pages/PredictionPage';
import PredictionResultPage from './pages/PredictionResultPage';
import MarketComparisonPage from './pages/MarketComparisonPage';
import SavedCropsPage from './pages/SavedCropsPage';
import PredictionHistoryPage from './pages/PredictionHistoryPage';
import AdminDashboard from './pages/AdminDashboard';
import LoginPage from './pages/LoginPage';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading, isAdmin } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />;
  return children;
};

function AppContent() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Navbar />
        <Routes>
          <Route path="/" element={<FarmerDashboard />} />
          <Route path="/predict" element={<PredictionPage />} />
          <Route path="/result/:id" element={<PredictionResultPage />} />
          <Route path="/compare" element={<MarketComparisonPage />} />
          <Route path="/saved" element={<SavedCropsPage />} />
          <Route path="/history" element={<PredictionHistoryPage />} />
          <Route path="/admin" element={
            <ProtectedRoute adminOnly>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <LanguageProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </LanguageProvider>
    </Router>
  );
}
