import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  IconButton,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Card,
  CardContent,
  CardActions,
  Chip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  Fingerprint as SignatureIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface BiochemistProfile {
  id: number;
  user_id: number;
  user: {
    username: string;
    email: string;
    full_name: string;
  };
  registration_number: string;
  digital_signature?: string;
  signature_image?: string;
  professional_license: string;
  specialties: string[];
}

export const BiochemistProfiles: React.FC = () => {
  const [profiles, setProfiles] = useState<BiochemistProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<BiochemistProfile | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');
  const [signatureFile, setSignatureFile] = useState<File | null>(null);
  const [digitalCertFile, setDigitalCertFile] = useState<File | null>(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const response = await api.get('/biochemist-profiles');
      setProfiles(response.data);
    } catch (error) {
      setError('Error al cargar los perfiles');
    }
  };

  const handleSaveProfile = async (formData: FormData) => {
    try {
      if (selectedProfile?.id) {
        await api.put(`/biochemist-profiles/${selectedProfile.id}`, formData);
      } else {
        await api.post('/biochemist-profiles', formData);
      }
      loadProfiles();
      setIsDialogOpen(false);
      setSelectedProfile(null);
    } catch (error) {
      setError('Error al guardar el perfil');
    }
  };

  const handleDeleteProfile = async (id: number) => {
    try {
      await api.delete(`/biochemist-profiles/${id}`);
      loadProfiles();
    } catch (error) {
      setError('Error al eliminar el perfil');
    }
  };

  const ProfileDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<BiochemistProfile>>(
      selectedProfile || {
        registration_number: '',
        professional_license: '',
        specialties: [],
      }
    );

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      const submitData = new FormData();
      
      Object.entries(formData).forEach(([key, value]) => {
        if (key === 'specialties') {
          submitData.append(key, JSON.stringify(value));
        } else {
          submitData.append(key, value as string);
        }
      });

      if (signatureFile) {
        submitData.append('signature_image', signatureFile);
      }
      if (digitalCertFile) {
        submitData.append('digital_signature', digitalCertFile);
      }

      handleSaveProfile(submitData);
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>, type: 'signature' | 'certificate') => {
      const file = event.target.files?.[0];
      if (file) {
        if (type === 'signature') {
          setSignatureFile(file);
        } else {
          setDigitalCertFile(file);
        }
      }
    };

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedProfile ? 'Editar Perfil de Bioquímico' : 'Nuevo Perfil de Bioquímico'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Número de Registro"
                  name="registration_number"
                  value={formData.registration_number}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    registration_number: e.target.value
                  }))}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Licencia Profesional"
                  name="professional_license"
                  value={formData.professional_license}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    professional_license: e.target.value
                  }))}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Especialidades"
                  name="specialties"
                  value={formData.specialties?.join(', ')}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    specialties: e.target.value.split(',').map(s => s.trim())
                  }))}
                  helperText="Separar especialidades con comas"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<UploadIcon />}
                  fullWidth
                >
                  Subir Firma Escaneada
                  <input
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={(e) => handleFileChange(e, 'signature')}
                  />
                </Button>
                {signatureFile && (
                  <Typography variant="caption" display="block">
                    Archivo seleccionado: {signatureFile.name}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<SignatureIcon />}
                  fullWidth
                >
                  Subir Certificado Digital
                  <input
                    type="file"
                    hidden
                    accept=".p12,.pfx"
                    onChange={(e) => handleFileChange(e, 'certificate')}
                  />
                </Button>
                {digitalCertFile && (
                  <Typography variant="caption" display="block">
                    Archivo seleccionado: {digitalCertFile.name}
                  </Typography>
                )}
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
          <Typography variant="h5">Perfiles de Bioquímicos</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedProfile(null);
              setIsDialogOpen(true);
            }}
          >
            Nuevo Perfil
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {profiles.map((profile) => (
            <Grid item xs={12} md={6} key={profile.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                      {profile.user.full_name.charAt(0)}
                    </Avatar>
                    <Box>
                      <Typography variant="h6">
                        {profile.user.full_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Registro: {profile.registration_number}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Licencia: {profile.professional_license}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    {profile.specialties.map((specialty, index) => (
                      <Chip
                        key={index}
                        label={specialty}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    {profile.signature_image && (
                      <Chip
                        size="small"
                        icon={<UploadIcon />}
                        label="Firma Escaneada"
                        color="success"
                      />
                    )}
                    {profile.digital_signature && (
                      <Chip
                        size="small"
                        icon={<SignatureIcon />}
                        label="Firma Digital"
                        color="success"
                      />
                    )}
                  </Box>
                </CardContent>
                <CardActions>
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedProfile(profile);
                      setIsDialogOpen(true);
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteProfile(profile.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        <ProfileDialog />
      </Paper>
    </Box>
  );
};
