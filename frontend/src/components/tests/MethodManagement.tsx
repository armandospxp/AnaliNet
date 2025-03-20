import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Method {
  id: number;
  code: string;
  name: string;
  description: string;
  technique: string;
  equipment_id?: number;
  equipment_name?: string;
  protocol?: string;
  calibration_info?: string;
  validation_rules?: ValidationRule[];
}

interface ValidationRule {
  id: number;
  type: 'RANGE' | 'PRECISION' | 'ACCURACY' | 'LINEARITY';
  min_value?: number;
  max_value?: number;
  target_value?: number;
  tolerance?: number;
  description: string;
}

export const MethodManagement: React.FC = () => {
  const [methods, setMethods] = useState<Method[]>([]);
  const [selectedMethod, setSelectedMethod] = useState<Method | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadMethods();
  }, []);

  const loadMethods = async () => {
    try {
      const response = await api.get('/methods');
      setMethods(response.data);
    } catch (error) {
      setError('Error al cargar los métodos');
    }
  };

  const handleSaveMethod = async (methodData: Partial<Method>) => {
    try {
      if (selectedMethod?.id) {
        await api.put(`/methods/${selectedMethod.id}`, methodData);
      } else {
        await api.post('/methods', methodData);
      }
      loadMethods();
      setIsDialogOpen(false);
      setSelectedMethod(null);
    } catch (error) {
      setError('Error al guardar el método');
    }
  };

  const handleDeleteMethod = async (id: number) => {
    try {
      await api.delete(`/methods/${id}`);
      loadMethods();
    } catch (error) {
      setError('Error al eliminar el método');
    }
  };

  const MethodDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<Method>>(
      selectedMethod || {
        code: '',
        name: '',
        description: '',
        technique: '',
        protocol: '',
        calibration_info: '',
        validation_rules: [],
      }
    );

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    };

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      handleSaveMethod(formData);
    };

    const ValidationRuleCard: React.FC<{ rule: ValidationRule }> = ({ rule }) => (
      <Card variant="outlined" sx={{ mb: 1 }}>
        <CardContent>
          <Typography variant="subtitle2" color="primary">
            {rule.type}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {rule.description}
          </Typography>
          {rule.type === 'RANGE' && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">
                Rango: {rule.min_value} - {rule.max_value}
              </Typography>
            </Box>
          )}
          {rule.type === 'PRECISION' && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">
                Tolerancia: ±{rule.tolerance}%
              </Typography>
            </Box>
          )}
          {(rule.type === 'ACCURACY' || rule.type === 'LINEARITY') && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">
                Valor objetivo: {rule.target_value}
                {rule.tolerance && ` (±${rule.tolerance}%)`}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedMethod ? 'Editar Método' : 'Nuevo Método'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Código"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nombre"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Descripción"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  multiline
                  rows={3}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Técnica"
                  name="technique"
                  value={formData.technique}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Protocolo"
                  name="protocol"
                  value={formData.protocol}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Información de Calibración"
                  name="calibration_info"
                  value={formData.calibration_info}
                  onChange={handleChange}
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>

            {formData.validation_rules && formData.validation_rules.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>
                  Reglas de Validación
                </Typography>
                {formData.validation_rules.map((rule, index) => (
                  <ValidationRuleCard key={index} rule={rule} />
                ))}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" color="primary">
              Guardar
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5">Gestión de Métodos</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedMethod(null);
              setIsDialogOpen(true);
            }}
          >
            Nuevo Método
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Código</TableCell>
                <TableCell>Nombre</TableCell>
                <TableCell>Técnica</TableCell>
                <TableCell>Equipo</TableCell>
                <TableCell>Validación</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {methods.map((method) => (
                <TableRow key={method.id}>
                  <TableCell>{method.code}</TableCell>
                  <TableCell>{method.name}</TableCell>
                  <TableCell>{method.technique}</TableCell>
                  <TableCell>
                    {method.equipment_name && (
                      <Chip
                        icon={<ScienceIcon />}
                        label={method.equipment_name}
                        size="small"
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${method.validation_rules?.length || 0} reglas`}
                      size="small"
                      color={method.validation_rules?.length ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedMethod(method);
                        setIsDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteMethod(method.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <MethodDialog />
      </Paper>
    </Box>
  );
};
