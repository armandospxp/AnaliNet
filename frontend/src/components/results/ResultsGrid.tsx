import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  CheckCircle as ValidateIcon,
  History as HistoryIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { api } from '../../services/api';
import { Permission } from '../../types/auth';

interface Result {
  id: number;
  determination_id: number;
  determination_name: string;
  value: string;
  unit: string;
  reference_range: string;
  is_critical: boolean;
  is_validated: boolean;
  validator_id?: number;
  validation_date?: string;
}

interface HistoricalResult {
  value: string;
  unit: string;
  date: string;
  is_critical: boolean;
}

interface ResultsGridProps {
  orderId: number;
}

export const ResultsGrid: React.FC<ResultsGridProps> = ({ orderId }) => {
  const { user } = useAuth();
  const [results, setResults] = useState<Result[]>([]);
  const [historicalResults, setHistoricalResults] = useState<Record<number, HistoricalResult[]>>({});
  const [selectedDetermination, setSelectedDetermination] = useState<number | null>(null);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const canValidate = user?.permissions.includes(Permission.VALIDATE_RESULTS);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await api.get(`/orders/${orderId}/results`);
        setResults(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching results:', error);
        setLoading(false);
      }
    };

    fetchResults();
  }, [orderId]);

  const fetchHistoricalResults = async (determinationId: number) => {
    if (historicalResults[determinationId]) {
      setSelectedDetermination(determinationId);
      setIsHistoryModalOpen(true);
      return;
    }

    try {
      const response = await api.get(`/patients/${results[0].patient_id}/historical-results/${determinationId}`);
      setHistoricalResults(prev => ({
        ...prev,
        [determinationId]: response.data.slice(-3) // Últimos 3 resultados
      }));
      setSelectedDetermination(determinationId);
      setIsHistoryModalOpen(true);
    } catch (error) {
      console.error('Error fetching historical results:', error);
    }
  };

  const handleResultChange = async (resultId: number, value: string) => {
    try {
      await api.patch(`/results/${resultId}`, { value });
      setResults(prev =>
        prev.map(r =>
          r.id === resultId ? { ...r, value } : r
        )
      );
    } catch (error) {
      console.error('Error updating result:', error);
    }
  };

  const handleValidateResult = async (resultId: number) => {
    try {
      await api.post(`/results/${resultId}/validate`);
      setResults(prev =>
        prev.map(r =>
          r.id === resultId
            ? { ...r, is_validated: true, validator_id: user?.id, validation_date: new Date().toISOString() }
            : r
        )
      );
    } catch (error) {
      console.error('Error validating result:', error);
    }
  };

  const handleValidateAll = async () => {
    try {
      await api.post(`/orders/${orderId}/validate-all`);
      setResults(prev =>
        prev.map(r => ({
          ...r,
          is_validated: true,
          validator_id: user?.id,
          validation_date: new Date().toISOString()
        }))
      );
    } catch (error) {
      console.error('Error validating all results:', error);
    }
  };

  if (loading) {
    return <Typography>Cargando resultados...</Typography>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5">Carga de Resultados</Typography>
            {canValidate && (
              <Button
                variant="contained"
                color="primary"
                onClick={handleValidateAll}
                disabled={results.every(r => r.is_validated)}
              >
                Validar Todos
              </Button>
            )}
          </Box>
        </Grid>

        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Determinación</TableCell>
                  <TableCell>Resultado</TableCell>
                  <TableCell>Unidad</TableCell>
                  <TableCell>Rango de Referencia</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((result) => (
                  <TableRow
                    key={result.id}
                    sx={{
                      backgroundColor: result.is_critical ? 'error.light' : 'inherit'
                    }}
                  >
                    <TableCell>{result.determination_name}</TableCell>
                    <TableCell>
                      <TextField
                        size="small"
                        value={result.value}
                        onChange={(e) => handleResultChange(result.id, e.target.value)}
                        disabled={result.is_validated}
                      />
                    </TableCell>
                    <TableCell>{result.unit}</TableCell>
                    <TableCell>{result.reference_range}</TableCell>
                    <TableCell>
                      {result.is_validated ? (
                        <Chip
                          label="Validado"
                          color="success"
                          size="small"
                          icon={<ValidateIcon />}
                        />
                      ) : result.is_critical ? (
                        <Chip
                          label="Crítico"
                          color="error"
                          size="small"
                          icon={<WarningIcon />}
                        />
                      ) : (
                        <Chip
                          label="Pendiente"
                          color="warning"
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex' }}>
                        <Tooltip title="Ver Histórico">
                          <IconButton
                            size="small"
                            onClick={() => fetchHistoricalResults(result.determination_id)}
                          >
                            <HistoryIcon />
                          </IconButton>
                        </Tooltip>
                        {canValidate && !result.is_validated && (
                          <Tooltip title="Validar">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleValidateResult(result.id)}
                            >
                              <ValidateIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>

      {/* Modal de Histórico */}
      <Dialog
        open={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Histórico de Resultados
          {selectedDetermination && ` - ${results.find(r => r.determination_id === selectedDetermination)?.determination_name}`}
        </DialogTitle>
        <DialogContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Resultado</TableCell>
                  <TableCell>Unidad</TableCell>
                  <TableCell>Estado</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {selectedDetermination &&
                  historicalResults[selectedDetermination]?.map((result, index) => (
                    <TableRow
                      key={index}
                      sx={{
                        backgroundColor: result.is_critical ? 'error.light' : 'inherit'
                      }}
                    >
                      <TableCell>{new Date(result.date).toLocaleDateString()}</TableCell>
                      <TableCell>{result.value}</TableCell>
                      <TableCell>{result.unit}</TableCell>
                      <TableCell>
                        {result.is_critical ? (
                          <Chip
                            label="Crítico"
                            color="error"
                            size="small"
                            icon={<WarningIcon />}
                          />
                        ) : (
                          <Chip
                            label="Normal"
                            color="success"
                            size="small"
                          />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsHistoryModalOpen(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
