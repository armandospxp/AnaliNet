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
  Autocomplete,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Analysis {
  id: number;
  code: string;
  name: string;
  category: string;
  sample_type_id: number;
  sample_type: string;
  sample_instructions: string;
  determinations: Determination[];
}

interface Determination {
  id: number;
  code: string;
  name: string;
  result_type: 'NUMERIC' | 'CATEGORICAL' | 'TEXT';
  unit_id: number;
  unit: string;
  decimal_places?: number;
  reference_ranges: ReferenceRange[];
}

interface ReferenceRange {
  min_value?: number;
  max_value?: number;
  min_critical?: number;
  max_critical?: number;
  text_value?: string;
  gender?: 'M' | 'F';
  min_age?: number;
  max_age?: number;
}

interface SampleType {
  id: number;
  name: string;
  code: string;
}

export const AnalysisManagement: React.FC = () => {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [sampleTypes, setSampleTypes] = useState<SampleType[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadAnalyses();
    loadSampleTypes();
  }, []);

  const loadAnalyses = async () => {
    try {
      const response = await api.get('/analyses');
      setAnalyses(response.data);
    } catch (error) {
      setError('Error al cargar los análisis');
    }
  };

  const loadSampleTypes = async () => {
    try {
      const response = await api.get('/sample-types');
      setSampleTypes(response.data);
    } catch (error) {
      setError('Error al cargar los tipos de muestra');
    }
  };

  const handleSaveAnalysis = async (analysisData: Partial<Analysis>) => {
    try {
      if (selectedAnalysis?.id) {
        await api.put(`/analyses/${selectedAnalysis.id}`, analysisData);
      } else {
        await api.post('/analyses', analysisData);
      }
      loadAnalyses();
      setIsDialogOpen(false);
      setSelectedAnalysis(null);
    } catch (error) {
      setError('Error al guardar el análisis');
    }
  };

  const handleDeleteAnalysis = async (id: number) => {
    try {
      await api.delete(`/analyses/${id}`);
      loadAnalyses();
    } catch (error) {
      setError('Error al eliminar el análisis');
    }
  };

  const AnalysisDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<Analysis>>(
      selectedAnalysis || {
        code: '',
        name: '',
        category: '',
        sample_type_id: 0,
        sample_instructions: '',
        determinations: [],
      }
    );

    const categories = [
      'Hematología',
      'Bioquímica',
      'Inmunología',
      'Microbiología',
      'Uroanálisis',
      'Coagulación',
      'Serología',
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
      handleSaveAnalysis(formData);
    };

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedAnalysis ? 'Editar Análisis' : 'Nuevo Análisis'}
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
                  <InputLabel>Categoría</InputLabel>
                  <Select
                    name="category"
                    value={formData.category}
                    label="Categoría"
                    onChange={(e) => handleChange(e as any)}
                  >
                    {categories.map((category) => (
                      <MenuItem key={category} value={category}>
                        {category}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Tipo de Muestra</InputLabel>
                  <Select
                    name="sample_type_id"
                    value={formData.sample_type_id}
                    label="Tipo de Muestra"
                    onChange={(e) => handleChange(e as any)}
                  >
                    {sampleTypes.map((type) => (
                      <MenuItem key={type.id} value={type.id}>
                        {type.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Instrucciones de Toma de Muestra"
                  name="sample_instructions"
                  value={formData.sample_instructions}
                  onChange={handleChange}
                  required
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
          <Typography variant="h5">Gestión de Análisis</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedAnalysis(null);
              setIsDialogOpen(true);
            }}
          >
            Nuevo Análisis
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
                <TableCell>Categoría</TableCell>
                <TableCell>Tipo de Muestra</TableCell>
                <TableCell>Determinaciones</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analyses.map((analysis) => (
                <TableRow key={analysis.id}>
                  <TableCell>{analysis.code}</TableCell>
                  <TableCell>{analysis.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={analysis.category}
                      size="small"
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>{analysis.sample_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${analysis.determinations.length} determinaciones`}
                      size="small"
                      icon={<ScienceIcon />}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedAnalysis(analysis);
                        setIsDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteAnalysis(analysis.id)}
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

        <AnalysisDialog />
      </Paper>
    </Box>
  );
};
