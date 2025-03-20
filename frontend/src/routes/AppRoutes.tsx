import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { LoginPage } from '../components/auth/LoginPage';
import { Dashboard } from '../components/dashboard/Dashboard';
import { AnalysisOrderForm } from '../components/orders/AnalysisOrderForm';
import { ResultsGrid } from '../components/results/ResultsGrid';
import { ReportsPage } from '../components/reports/ReportsPage';
import { useAuth } from '../hooks/useAuth';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  return user ? <>{children}</> : <Navigate to="/login" />;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/" element={
        <PrivateRoute>
          <MainLayout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/orders" element={<AnalysisOrderForm />} />
              <Route path="/results" element={<ResultsGrid orderId={0} />} />
              <Route path="/reports" element={<ReportsPage />} />
            </Routes>
          </MainLayout>
        </PrivateRoute>
      } />
    </Routes>
  );
};
