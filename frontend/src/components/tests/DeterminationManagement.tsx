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
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as NormalIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Determination {
  id: number;
  code: string;
  name: string;
  result_type: 'NUMERIC' | 'CATEGORICAL' | 'TEXT';
  unit_id: number;
  unit: string;
  decimal_places?: number;
  method_id: number;
  method: string;
  reference_ranges: ReferenceRange[];
  categorical_values?: string[];
}

interface ReferenceRange {
  id: number;
  min_value?: number;
  max_value?: number;
  min_critical?: number;
  max_critical?: number;
  text_value?: string;
  gender?: 'M' | 'F';
  min_age?: number;
  max_age?: number;
  alert_level: 'NORMAL' | 'WARNING' | 'CRITICAL';
}

interface Unit {
  id: number;
  name: string;
  symbol: string;
  type: string;
}

interface Method {
  id: number;
  name: string;
  code: string;
  description: string;
}

export const DeterminationManagement: React.FC = () => {
  const [determinations, setDeterminations] = useState<Determination[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [methods, setMethods] = useState<Method[]>([]);
  const [selectedDetermination, setSelectedDetermination] = useState<Determination | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isRangeDialogOpen, setIsRangeDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadDeterminations();
    loadUnits();
    loadMethods();
  }, []);

  const loadDeterminations = async () => {
    try {
      const response = await api.get('/determinations');
      setDeterminations(response.data);
    } catch (error) {
      setError('Error al cargar las determinaciones');
    }
  };

  const loadUnits = async () => {
    try {
      const response = await api.get('/units');
      setUnits(response.data);
    } catch (error) {
      setError('Error al cargar las unidades');
    }
  };

  const loadMethods = async () => {
    try {
      const response = await api.get('/methods');
      setMethods(response.data);
    } catch (error) {
      setError('Error al cargar los métodos');
    }
  };

  const handleSaveDetermination = async (determinationData: Partial<Determination>) => {
    try {
      if (selectedDetermination?.id) {
        await api.put(`/determinations/${selectedDetermination.id}`, determinationData);
      } else {
        await api.post('/determinations', determinationData);
      }
      loadDeterminations();
      setIsDialogOpen(false);
      setSelectedDetermination(null);
    } catch (error) {
      setError('Error al guardar la determinación');
    }
  };

  const handleDeleteDetermination = async (id: number) => {
    try {
      await api.delete(`/determinations/${id}`);
      loadDeterminations();
    } catch (error) {
      setError('Error al eliminar la determinación');
    }
  };

  const DeterminationDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<Determination>>(
      selectedDetermination || {
        code: '',
        name: '',
        result_type: 'NUMERIC',
        unit_id: 0,
        decimal_places: 2,
        method_id: 0,
        reference_ranges: [],
        categorical_values: [],
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
      handleSaveDetermination(formData);
    };

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedDetermination ? 'Editar Determinación' : 'Nueva Determinación'}
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
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Tipo de Resultado</InputLabel>
                  <Select
                    name="result_type"
                    value={formData.result_type}
                    label="Tipo de Resultado"
                    onChange={(e) => handleChange(e as any)}
                  >
                    <MenuItem value="NUMERIC">Numérico</MenuItem>
                    <MenuItem value="CATEGORICAL">Categórico</MenuItem>
                    <MenuItem value="TEXT">Texto</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Unidad</InputLabel>
                  <Select
                    name="unit_id"
                    value={formData.unit_id}
                    label="Unidad"
                    onChange={(e) => handleChange(e as any)}
                  >
                    {units.map((unit) => (
                      <MenuItem key={unit.id} value={unit.id}>
                        {unit.name} ({unit.symbol})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              {formData.result_type === 'NUMERIC' && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Decimales"
                    name="decimal_places"
                    value={formData.decimal_places}
                    onChange={handleChange}
                    inputProps={{ min: 0, max: 6 }}
                  />
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Método</InputLabel>
                  <Select
                    name="method_id"
                    value={formData.method_id}
                    label="Método"
                    onChange={(e) => handleChange(e as any)}
                  >
                    {methods.map((method) => (
                      <MenuItem key={method.id} value={method.id}>
                        {method.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              {formData.result_type === 'CATEGORICAL' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Valores Categóricos"
                    name="categorical_values"
                    value={formData.categorical_values?.join(', ')}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      categorical_values: e.target.value.split(',').map(v => v.trim())
                    }))}
                    helperText="Separar valores con comas"
                  />
                </Grid>
              )}
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

  const ReferenceRangeCard: React.FC<{ range: ReferenceRange }> = ({ range }) => {
    const getAlertIcon = (level: string) => {
      switch (level) {
        case 'CRITICAL':
          return <ErrorIcon color="error" />;
        case 'WARNING':
          return <WarningIcon color="warning" />;
        default:
          return <NormalIcon color="success" />;
      }
    };

    return (
      <Card variant="outlined" sx={{ mb: 1 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            {getAlertIcon(range.alert_level)}
            <Typography variant="subtitle2">
              {range.gender ? (range.gender === 'M' ? 'Masculino' : 'Femenino') : 'Ambos géneros'}
              {range.min_age !== undefined && ` - ${range.min_age} a ${range.max_age} años`}
            </Typography>
          </Box>
          <Divider sx={{ my: 1 }} />
          {range.text_value ? (
            <Typography>{range.text_value}</Typography>
          ) : (
            <Box>
              {range.min_critical !== undefined && (
                <Typography color="error.main">
                  Crítico bajo: {range.min_critical}
                </Typography>
              )}
              <Typography>
                Rango normal: {range.min_value} - {range.max_value}
              </Typography>
              {range.max_critical !== undefined && (
                <Typography color="error.main">
                  Crítico alto: {range.max_critical}
                </Typography>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5">Gestión de Determinaciones</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedDetermination(null);
              setIsDialogOpen(true);
            }}
          >
            Nueva Determinación
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
                <TableCell>Tipo</TableCell>
                <TableCell>Unidad</TableCell>
                <TableCell>Método</TableCell>
                <TableCell>Rangos</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {determinations.map((determination) => (
                <TableRow key={determination.id}>
                  <TableCell>{determination.code}</TableCell>
                  <TableCell>{determination.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={determination.result_type}
                      size="small"
                      color={
                        determination.result_type === 'NUMERIC' ? 'primary' :
                        determination.result_type === 'CATEGORICAL' ? 'secondary' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell>{determination.unit}</TableCell>
                  <TableCell>{determination.method}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${determination.reference_ranges.length} rangos`}
                      size="small"
                      onClick={() => {
                        setSelectedDetermination(determination);
                        setIsRangeDialogOpen(true);
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedDetermination(determination);
                        setIsDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteDetermination(determination.id)}
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

        <DeterminationDialog />

        <Dialog
          open={isRangeDialogOpen}
          onClose={() => setIsRangeDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            Rangos de Referencia - {selectedDetermination?.name}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {selectedDetermination?.reference_ranges.map((range) => (
                <ReferenceRangeCard key={range.id} range={range} />
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsRangeDialogOpen(false)}>Cerrar</Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Box>
  );
};
