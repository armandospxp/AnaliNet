import React, { useState } from 'react';
import {
  Box,
  Paper,
  Grid,
  Typography,
  Tabs,
  Tab,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  DatePicker,
} from '@mui/x-date-pickers';
import {
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Print as PrintIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export const ReportsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [reportType, setReportType] = useState('');
  const [category, setCategory] = useState('');
  const [format, setFormat] = useState('pdf');
  const [loading, setLoading] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleGenerateReport = async () => {
    if (!startDate || !endDate) return;

    setLoading(true);
    try {
      const response = await api.post('/reports/generate', {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        report_type: reportType,
        category,
        format,
      }, { responseType: 'blob' });

      // Crear URL para descargar el archivo
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `reporte_${new Date().toISOString()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Reportes
      </Typography>

      <Paper sx={{ width: '100%', mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Análisis" />
          <Tab label="Pacientes" />
          <Tab label="Estadísticas" />
        </Tabs>

        {/* Reportes de Análisis */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <DatePicker
                label="Fecha Inicio"
                value={startDate}
                onChange={(date) => setStartDate(date)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <DatePicker
                label="Fecha Fin"
                value={endDate}
                onChange={(date) => setEndDate(date)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Categoría</InputLabel>
                <Select
                  value={category}
                  label="Categoría"
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <MenuItem value="hematology">Hematología</MenuItem>
                  <MenuItem value="biochemistry">Bioquímica</MenuItem>
                  <MenuItem value="immunology">Inmunología</MenuItem>
                  <MenuItem value="microbiology">Microbiología</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PdfIcon />}
                  onClick={() => {
                    setFormat('pdf');
                    handleGenerateReport();
                  }}
                  disabled={loading}
                >
                  Generar PDF
                </Button>
                <Button
                  variant="contained"
                  startIcon={<ExcelIcon />}
                  onClick={() => {
                    setFormat('xlsx');
                    handleGenerateReport();
                  }}
                  disabled={loading}
                >
                  Exportar Excel
                </Button>
                <Button
                  variant="contained"
                  startIcon={<PrintIcon />}
                  onClick={() => window.print()}
                >
                  Imprimir
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Reportes de Pacientes */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <DatePicker
                label="Fecha Inicio"
                value={startDate}
                onChange={(date) => setStartDate(date)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <DatePicker
                label="Fecha Fin"
                value={endDate}
                onChange={(date) => setEndDate(date)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Reporte</InputLabel>
                <Select
                  value={reportType}
                  label="Tipo de Reporte"
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <MenuItem value="new_patients">Nuevos Pacientes</MenuItem>
                  <MenuItem value="patient_history">Historial de Pacientes</MenuItem>
                  <MenuItem value="critical_results">Resultados Críticos</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PdfIcon />}
                  onClick={() => {
                    setFormat('pdf');
                    handleGenerateReport();
                  }}
                  disabled={loading}
                >
                  Generar PDF
                </Button>
                <Button
                  variant="contained"
                  startIcon={<ExcelIcon />}
                  onClick={() => {
                    setFormat('xlsx');
                    handleGenerateReport();
                  }}
                  disabled={loading}
                >
                  Exportar Excel
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Estadísticas */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Análisis por Categoría
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Categoría</TableCell>
                          <TableCell align="right">Cantidad</TableCell>
                          <TableCell align="right">%</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {/* Datos de ejemplo - Reemplazar con datos reales */}
                        <TableRow>
                          <TableCell>Hematología</TableCell>
                          <TableCell align="right">150</TableCell>
                          <TableCell align="right">30%</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Bioquímica</TableCell>
                          <TableCell align="right">200</TableCell>
                          <TableCell align="right">40%</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Resultados Críticos
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Determinación</TableCell>
                          <TableCell align="right">Cantidad</TableCell>
                          <TableCell align="right">%</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {/* Datos de ejemplo - Reemplazar con datos reales */}
                        <TableRow>
                          <TableCell>Glucosa</TableCell>
                          <TableCell align="right">15</TableCell>
                          <TableCell align="right">10%</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Hemoglobina</TableCell>
                          <TableCell align="right">8</TableCell>
                          <TableCell align="right">5%</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Box>
  );
};
