import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Alert,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  CardHeader,
  Switch,
  FormControlLabel,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Database as DatabaseIcon,
  Print as PrintIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { Navigate } from 'react-router-dom';

interface SystemConfig {
  laboratory: {
    name: string;
    code: string;
    address: string;
    phone: string;
    email: string;
    logo_url?: string;
    website?: string;
  };
  report: {
    header_title: string;
    header_subtitle?: string;
    footer_text: string;
    show_logo: boolean;
    logo_position: 'left' | 'center' | 'right';
    include_digital_signature: boolean;
    include_barcode: boolean;
    custom_css?: string;
  };
  database: {
    host: string;
    port: number;
    name: string;
    backup_enabled: boolean;
    backup_schedule: string;
    backup_retention_days: number;
    last_backup?: string;
  };
}

export const SystemConfiguration: React.FC = () => {
  const { user } = useAuth();
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [logoFile, setLogoFile] = useState<File | null>(null);

  // Verificar si el usuario es administrador
  if (!user || !user.permissions.includes('MANAGE_DATABASE')) {
    return <Navigate to="/unauthorized" replace />;
  }

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/admin/system-config');
      setConfig(response.data);
    } catch (error) {
      setError('Error al cargar la configuración del sistema');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    if (!config) return;

    try {
      setIsLoading(true);
      const formData = new FormData();
      formData.append('config', JSON.stringify(config));
      if (logoFile) {
        formData.append('logo', logoFile);
      }

      await api.put('/admin/system-config', formData);
      setSuccess('Configuración guardada exitosamente');
      loadConfig(); // Recargar para obtener los últimos cambios
    } catch (error) {
      setError('Error al guardar la configuración');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackupNow = async () => {
    try {
      setIsLoading(true);
      await api.post('/admin/database/backup');
      setSuccess('Backup iniciado exitosamente');
      loadConfig(); // Recargar para obtener la última fecha de backup
    } catch (error) {
      setError('Error al iniciar el backup');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setLogoFile(file);
      // Crear preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setConfig(prev => prev ? {
          ...prev,
          laboratory: {
            ...prev.laboratory,
            logo_url: reader.result as string
          }
        } : null);
      };
      reader.readAsDataURL(file);
    }
  };

  if (!config) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">Cargando configuración...</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5">Configuración del Sistema</Typography>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveConfig}
            disabled={isLoading}
          >
            Guardar Cambios
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Información del Laboratorio */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Información del Laboratorio" />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Nombre del Laboratorio"
                      value={config.laboratory.name}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        laboratory: { ...prev!.laboratory, name: e.target.value }
                      }))}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Código"
                      value={config.laboratory.code}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        laboratory: { ...prev!.laboratory, code: e.target.value }
                      }))}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Dirección"
                      value={config.laboratory.address}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        laboratory: { ...prev!.laboratory, address: e.target.value }
                      }))}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Teléfono"
                      value={config.laboratory.phone}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        laboratory: { ...prev!.laboratory, phone: e.target.value }
                      }))}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={config.laboratory.email}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        laboratory: { ...prev!.laboratory, email: e.target.value }
                      }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<UploadIcon />}
                      fullWidth
                    >
                      Subir Logo
                      <input
                        type="file"
                        hidden
                        accept="image/*"
                        onChange={handleLogoUpload}
                      />
                    </Button>
                    {config.laboratory.logo_url && (
                      <Box sx={{ mt: 2, textAlign: 'center' }}>
                        <img
                          src={config.laboratory.logo_url}
                          alt="Logo del laboratorio"
                          style={{ maxHeight: 100 }}
                        />
                      </Box>
                    )}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Configuración de Reportes */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader
                title="Configuración de Reportes"
                action={
                  <IconButton color="primary">
                    <PrintIcon />
                  </IconButton>
                }
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Título del Encabezado"
                      value={config.report.header_title}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        report: { ...prev!.report, header_title: e.target.value }
                      }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Subtítulo del Encabezado"
                      value={config.report.header_subtitle}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        report: { ...prev!.report, header_subtitle: e.target.value }
                      }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Texto del Pie de Página"
                      value={config.report.footer_text}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        report: { ...prev!.report, footer_text: e.target.value }
                      }))}
                      multiline
                      rows={2}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Posición del Logo</InputLabel>
                      <Select
                        value={config.report.logo_position}
                        label="Posición del Logo"
                        onChange={(e) => setConfig(prev => ({
                          ...prev!,
                          report: { ...prev!.report, logo_position: e.target.value as 'left' | 'center' | 'right' }
                        }))}
                      >
                        <MenuItem value="left">Izquierda</MenuItem>
                        <MenuItem value="center">Centro</MenuItem>
                        <MenuItem value="right">Derecha</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.report.include_digital_signature}
                          onChange={(e) => setConfig(prev => ({
                            ...prev!,
                            report: { ...prev!.report, include_digital_signature: e.target.checked }
                          }))}
                        />
                      }
                      label="Incluir Firma Digital"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.report.include_barcode}
                          onChange={(e) => setConfig(prev => ({
                            ...prev!,
                            report: { ...prev!.report, include_barcode: e.target.checked }
                          }))}
                        />
                      }
                      label="Incluir Código de Barras"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Configuración de Base de Datos */}
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title="Configuración de Base de Datos"
                action={
                  <Tooltip title="Esta configuración es crítica para el sistema">
                    <WarningIcon color="warning" />
                  </Tooltip>
                }
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Host"
                      value={config.database.host}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        database: { ...prev!.database, host: e.target.value }
                      }))}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Puerto"
                      type="number"
                      value={config.database.port}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        database: { ...prev!.database, port: parseInt(e.target.value) }
                      }))}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Nombre de Base de Datos"
                      value={config.database.name}
                      onChange={(e) => setConfig(prev => ({
                        ...prev!,
                        database: { ...prev!.database, name: e.target.value }
                      }))}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.database.backup_enabled}
                          onChange={(e) => setConfig(prev => ({
                            ...prev!,
                            database: { ...prev!.database, backup_enabled: e.target.checked }
                          }))}
                        />
                      }
                      label="Habilitar Backups Automáticos"
                    />
                  </Grid>
                  {config.database.backup_enabled && (
                    <>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Programación de Backup"
                          value={config.database.backup_schedule}
                          onChange={(e) => setConfig(prev => ({
                            ...prev!,
                            database: { ...prev!.database, backup_schedule: e.target.value }
                          }))}
                          helperText="Formato cron (ej: 0 0 * * *)"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Días de Retención"
                          type="number"
                          value={config.database.backup_retention_days}
                          onChange={(e) => setConfig(prev => ({
                            ...prev!,
                            database: { ...prev!.database, backup_retention_days: parseInt(e.target.value) }
                          }))}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Button
                          fullWidth
                          variant="outlined"
                          startIcon={<RefreshIcon />}
                          onClick={handleBackupNow}
                          disabled={isLoading}
                        >
                          Ejecutar Backup Ahora
                        </Button>
                        {config.database.last_backup && (
                          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                            Último backup: {new Date(config.database.last_backup).toLocaleString()}
                          </Typography>
                        )}
                      </Grid>
                    </>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};
