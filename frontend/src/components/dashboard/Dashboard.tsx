import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Assessment,
  People,
  Science,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAuth } from '../../hooks/useAuth';
import { api } from '../../services/api';

interface DashboardStats {
  todayPatients: number;
  todayTests: number;
  pendingValidation: number;
  criticalResults: number;
  testsByCategory: {
    category: string;
    count: number;
  }[];
  recentResults: {
    patientName: string;
    testName: string;
    status: string;
    timestamp: string;
  }[];
}

const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}> = ({ title, value, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Grid container spacing={2} alignItems="center">
        <Grid item>
          <Box sx={{ color }}>{icon}</Box>
        </Grid>
        <Grid item xs>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          <Typography variant="h4" component="div" sx={{ mt: 1 }}>
            {value}
          </Typography>
        </Grid>
      </Grid>
    </CardContent>
  </Card>
);

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/statistics/daily');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    };

    fetchStats();
    // Actualizar cada 5 minutos
    const interval = setInterval(fetchStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return <div>Cargando...</div>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Estadísticas principales */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pacientes Hoy"
            value={stats.todayPatients}
            icon={<People fontSize="large" />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Análisis Realizados"
            value={stats.todayTests}
            icon={<Science fontSize="large" />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pendientes Validación"
            value={stats.pendingValidation}
            icon={<Assessment fontSize="large" />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resultados Críticos"
            value={stats.criticalResults}
            icon={<Warning fontSize="large" />}
            color="#d32f2f"
          />
        </Grid>

        {/* Gráfico de análisis por categoría */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Análisis por Categoría
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={stats.testsByCategory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Resultados recientes */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Resultados Recientes
            </Typography>
            <List>
              {stats.recentResults.map((result, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemText
                      primary={result.patientName}
                      secondary={
                        <>
                          <Typography component="span" variant="body2" color="text.primary">
                            {result.testName}
                          </Typography>
                          {' — '}{result.timestamp}
                          <Box
                            component="span"
                            sx={{
                              ml: 1,
                              color: result.status === 'validated' ? 'success.main' : 'warning.main',
                              display: 'inline-flex',
                              alignItems: 'center',
                            }}
                          >
                            {result.status === 'validated' ? (
                              <CheckCircle fontSize="small" />
                            ) : (
                              <Warning fontSize="small" />
                            )}
                          </Box>
                        </>
                      }
                    />
                  </ListItem>
                  {index < stats.recentResults.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};
