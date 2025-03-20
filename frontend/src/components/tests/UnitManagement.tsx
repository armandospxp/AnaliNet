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
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Functions as MathIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Unit {
  id: number;
  name: string;
  symbol: string;
  type: string;
  base_unit_id?: number;
  base_unit?: string;
  conversion_factor?: number;
  description?: string;
  si_unit: boolean;
}

interface ConversionRule {
  from_unit_id: number;
  to_unit_id: number;
  factor: number;
  operation: 'multiply' | 'divide' | 'add' | 'subtract';
}

export const UnitManagement: React.FC = () => {
  const [units, setUnits] = useState<Unit[]>([]);
  const [selectedUnit, setSelectedUnit] = useState<Unit | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadUnits();
  }, []);

  const loadUnits = async () => {
    try {
      const response = await api.get('/units');
      setUnits(response.data);
    } catch (error) {
      setError('Error al cargar las unidades');
    }
  };

  const handleSaveUnit = async (unitData: Partial<Unit>) => {
    try {
      if (selectedUnit?.id) {
        await api.put(`/units/${selectedUnit.id}`, unitData);
      } else {
        await api.post('/units', unitData);
      }
      loadUnits();
      setIsDialogOpen(false);
      setSelectedUnit(null);
    } catch (error) {
      setError('Error al guardar la unidad');
    }
  };

  const handleDeleteUnit = async (id: number) => {
    try {
      await api.delete(`/units/${id}`);
      loadUnits();
    } catch (error) {
      setError('Error al eliminar la unidad');
    }
  };

  const UnitDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<Unit>>(
      selectedUnit || {
        name: '',
        symbol: '',
        type: '',
        description: '',
        si_unit: false,
      }
    );

    const unitTypes = [
      'Concentración',
      'Volumen',
      'Masa',
      'Tiempo',
      'Temperatura',
      'Ratio',
      'Conteo',
      'Porcentaje',
    ];

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    };

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      handleSaveUnit(formData);
    };

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedUnit ? 'Editar Unidad' : 'Nueva Unidad'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
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
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Símbolo"
                  name="symbol"
                  value={formData.symbol}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Tipo</InputLabel>
                  <Select
                    name="type"
                    value={formData.type}
                    label="Tipo"
                    onChange={(e) => handleChange(e as any)}
                  >
                    {unitTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Unidad Base</InputLabel>
                  <Select
                    name="base_unit_id"
                    value={formData.base_unit_id || ''}
                    label="Unidad Base"
                    onChange={(e) => handleChange(e as any)}
                  >
                    <MenuItem value="">
                      <em>Ninguna</em>
                    </MenuItem>
                    {units
                      .filter(u => u.si_unit && u.type === formData.type)
                      .map((unit) => (
                        <MenuItem key={unit.id} value={unit.id}>
                          {unit.name} ({unit.symbol})
                        </MenuItem>
                      ))}
                  </Select>
                </FormControl>
              </Grid>
              {formData.base_unit_id && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Factor de Conversión"
                    name="conversion_factor"
                    value={formData.conversion_factor}
                    onChange={handleChange}
                    required
                  />
                </Grid>
              )}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Descripción"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>
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
          <Typography variant="h5">Gestión de Unidades</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedUnit(null);
              setIsDialogOpen(true);
            }}
          >
            Nueva Unidad
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
                <TableCell>Símbolo</TableCell>
                <TableCell>Nombre</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Base</TableCell>
                <TableCell>Factor</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {units.map((unit) => (
                <TableRow key={unit.id}>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {unit.symbol}
                    </Typography>
                  </TableCell>
                  <TableCell>{unit.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={unit.type}
                      size="small"
                      color={unit.si_unit ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    {unit.base_unit && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <MathIcon fontSize="small" />
                        <Typography variant="body2" fontFamily="monospace">
                          {unit.base_unit}
                        </Typography>
                      </Box>
                    )}
                  </TableCell>
                  <TableCell>
                    {unit.conversion_factor && (
                      <Typography variant="body2">
                        × {unit.conversion_factor}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedUnit(unit);
                        setIsDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteUnit(unit.id)}
                      color="error"
                      disabled={unit.si_unit}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <UnitDialog />
      </Paper>
    </Box>
  );
};
