import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import { api } from '../../services/api';
import { Patient } from '../../types/patient';

interface NewPatientModalProps {
  open: boolean;
  onClose: () => void;
  onPatientCreated: (patient: Patient) => void;
}

export const NewPatientModal: React.FC<NewPatientModalProps> = ({
  open,
  onClose,
  onPatientCreated,
}) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    document_number: '',
    birth_date: '',
    gender: '',
    city: '',
    neighborhood: '',
    department: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name as string]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      // Primero crear la ubicación
      const locationResponse = await api.post('/locations/', {
        city: formData.city,
        neighborhood: formData.neighborhood,
        department: formData.department,
      });

      // Luego crear el paciente con el ID de la ubicación
      const patientResponse = await api.post('/patients/', {
        first_name: formData.first_name,
        last_name: formData.last_name,
        document_number: formData.document_number,
        birth_date: formData.birth_date,
        gender: formData.gender,
        location_id: locationResponse.data.id,
      });

      onPatientCreated(patientResponse.data);
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error al crear el paciente');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Nuevo Paciente</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Nombre"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Apellido"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Nº Documento"
                name="document_number"
                value={formData.document_number}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                type="date"
                label="Fecha de Nacimiento"
                name="birth_date"
                value={formData.birth_date}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Sexo</InputLabel>
                <Select
                  name="gender"
                  value={formData.gender}
                  label="Sexo"
                  onChange={handleChange}
                >
                  <MenuItem value="M">Masculino</MenuItem>
                  <MenuItem value="F">Femenino</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Ciudad"
                name="city"
                value={formData.city}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Barrio"
                name="neighborhood"
                value={formData.neighborhood}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Departamento"
                name="department"
                value={formData.department}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancelar</Button>
          <Button type="submit" variant="contained" color="primary">
            Guardar
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
