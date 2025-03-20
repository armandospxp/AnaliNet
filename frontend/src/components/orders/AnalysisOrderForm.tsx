import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Typography,
  Autocomplete,
  Dialog,
  IconButton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import {
  Add as AddIcon,
  PersonAdd as PersonAddIcon,
  LocalHospital as DoctorIcon,
} from '@mui/icons-material';
import { NewPatientModal } from './NewPatientModal';
import { NewDoctorModal } from './NewDoctorModal';
import { api } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';

interface Patient {
  id: number;
  full_name: string;
  document_number: string;
}

interface Doctor {
  id: number;
  full_name: string;
  registration_number: string;
}

interface AnalysisType {
  id: number;
  name: string;
  code: string;
  category: string;
  sample_type: string;
}

export const AnalysisOrderForm: React.FC = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [analysisTypes, setAnalysisTypes] = useState<AnalysisType[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [selectedAnalyses, setSelectedAnalyses] = useState<AnalysisType[]>([]);
  const [isNewPatientModalOpen, setIsNewPatientModalOpen] = useState(false);
  const [isNewDoctorModalOpen, setIsNewDoctorModalOpen] = useState(false);
  const [priority, setPriority] = useState('normal');
  const [observations, setObservations] = useState('');

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [patientsRes, doctorsRes, analysisRes] = await Promise.all([
          api.get('/patients'),
          api.get('/doctors'),
          api.get('/analysis-types')
        ]);
        setPatients(patientsRes.data);
        setDoctors(doctorsRes.data);
        setAnalysisTypes(analysisRes.data);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };

    fetchInitialData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPatient || selectedAnalyses.length === 0) {
      return;
    }

    try {
      const orderData = {
        patient_id: selectedPatient.id,
        doctor_id: selectedDoctor?.id,
        analyses: selectedAnalyses.map(a => a.id),
        priority,
        observations,
        created_by: user?.id
      };

      await api.post('/orders', orderData);
      // Resetear formulario o redirigir
    } catch (error) {
      console.error('Error creating order:', error);
    }
  };

  const handlePatientCreated = (newPatient: Patient) => {
    setPatients(prev => [...prev, newPatient]);
    setSelectedPatient(newPatient);
    setIsNewPatientModalOpen(false);
  };

  const handleDoctorCreated = (newDoctor: Doctor) => {
    setDoctors(prev => [...prev, newDoctor]);
    setSelectedDoctor(newDoctor);
    setIsNewDoctorModalOpen(false);
  };

  const handlePriorityChange = (event: SelectChangeEvent) => {
    setPriority(event.target.value);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Nuevo Pedido de Análisis
        </Typography>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Selección de Paciente */}
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <Autocomplete
                  fullWidth
                  options={patients}
                  getOptionLabel={(option) => `${option.full_name} - ${option.document_number}`}
                  value={selectedPatient}
                  onChange={(_, newValue) => setSelectedPatient(newValue)}
                  renderInput={(params) => (
                    <TextField {...params} label="Paciente" required />
                  )}
                  sx={{ mr: 1 }}
                />
                <IconButton 
                  color="primary"
                  onClick={() => setIsNewPatientModalOpen(true)}
                  sx={{ mt: 1 }}
                >
                  <PersonAddIcon />
                </IconButton>
              </Box>
            </Grid>

            {/* Selección de Médico */}
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <Autocomplete
                  fullWidth
                  options={doctors}
                  getOptionLabel={(option) => `${option.full_name} - ${option.registration_number}`}
                  value={selectedDoctor}
                  onChange={(_, newValue) => setSelectedDoctor(newValue)}
                  renderInput={(params) => (
                    <TextField {...params} label="Médico Solicitante" />
                  )}
                  sx={{ mr: 1 }}
                />
                <IconButton 
                  color="primary"
                  onClick={() => setIsNewDoctorModalOpen(true)}
                  sx={{ mt: 1 }}
                >
                  <DoctorIcon />
                </IconButton>
              </Box>
            </Grid>

            {/* Selección de Análisis */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={analysisTypes}
                getOptionLabel={(option) => `${option.name} (${option.code})`}
                value={selectedAnalyses}
                onChange={(_, newValue) => setSelectedAnalyses(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Análisis Solicitados"
                    required
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option.name}
                      {...getTagProps({ index })}
                      color="primary"
                    />
                  ))
                }
              />
            </Grid>

            {/* Prioridad */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Prioridad</InputLabel>
                <Select
                  value={priority}
                  label="Prioridad"
                  onChange={handlePriorityChange}
                >
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="urgent">Urgente</MenuItem>
                  <MenuItem value="critical">Crítico</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Observaciones */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Observaciones"
                value={observations}
                onChange={(e) => setObservations(e.target.value)}
              />
            </Grid>

            {/* Botón de envío */}
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                disabled={!selectedPatient || selectedAnalyses.length === 0}
              >
                Crear Pedido
              </Button>
            </Grid>
          </Grid>
        </form>

        {/* Modal para nuevo paciente */}
        <NewPatientModal
          open={isNewPatientModalOpen}
          onClose={() => setIsNewPatientModalOpen(false)}
          onPatientCreated={handlePatientCreated}
        />

        {/* Modal para nuevo médico */}
        <NewDoctorModal
          open={isNewDoctorModalOpen}
          onClose={() => setIsNewDoctorModalOpen(false)}
          onDoctorCreated={handleDoctorCreated}
        />
      </Paper>
    </Box>
  );
};
