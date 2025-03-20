import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  Print as PrintIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Print,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Printer {
  id: number;
  name: string;
  type: 'report' | 'barcode' | 'ticket';
  protocol: 'raw' | 'cups' | 'windows' | 'network';
  network_address?: string;
  port?: number;
  queue_name?: string;
  is_default: boolean;
  paper_width: number;
  paper_height: number;
  dpi: number;
}

export const PrinterSettings: React.FC = () => {
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [selectedPrinter, setSelectedPrinter] = useState<Printer | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [testPrintStatus, setTestPrintStatus] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadPrinters();
  }, []);

  const loadPrinters = async () => {
    try {
      const response = await api.get('/printers');
      setPrinters(response.data);
    } catch (error) {
      setError('Error al cargar las impresoras');
    }
  };

  const handleSavePrinter = async (printer: Partial<Printer>) => {
    try {
      if (selectedPrinter?.id) {
        await api.put(`/printers/${selectedPrinter.id}`, printer);
      } else {
        await api.post('/printers', printer);
      }
      loadPrinters();
      setIsDialogOpen(false);
      setSelectedPrinter(null);
    } catch (error) {
      setError('Error al guardar la impresora');
    }
  };

  const handleDeletePrinter = async (id: number) => {
    try {
      await api.delete(`/printers/${id}`);
      loadPrinters();
    } catch (error) {
      setError('Error al eliminar la impresora');
    }
  };

  const handleTestPrint = async (printer: Printer) => {
    try {
      setTestPrintStatus('Imprimiendo prueba...');
      await api.post(`/printers/${printer.id}/test`);
      setTestPrintStatus('Prueba enviada correctamente');
    } catch (error) {
      setTestPrintStatus('Error al imprimir prueba');
    }
  };

  const PrinterDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<Printer>>(
      selectedPrinter || {
        name: '',
        type: 'report',
        protocol: 'network',
        is_default: false,
        paper_width: 210,
        paper_height: 297,
        dpi: 203,
      }
    );

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
      const { name, value } = e.target;
      setFormData(prev => ({
        ...prev,
        [name as string]: value,
      }));
    };

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      handleSavePrinter(formData);
    };

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedPrinter ? 'Editar Impresora' : 'Nueva Impresora'}
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
                <FormControl fullWidth required>
                  <InputLabel>Tipo</InputLabel>
                  <Select
                    name="type"
                    value={formData.type}
                    label="Tipo"
                    onChange={handleChange}
                  >
                    <MenuItem value="report">Reportes</MenuItem>
                    <MenuItem value="barcode">Códigos de Barra</MenuItem>
                    <MenuItem value="ticket">Tickets</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Protocolo</InputLabel>
                  <Select
                    name="protocol"
                    value={formData.protocol}
                    label="Protocolo"
                    onChange={handleChange}
                  >
                    <MenuItem value="network">Red (TCP/IP)</MenuItem>
                    <MenuItem value="windows">Windows</MenuItem>
                    <MenuItem value="cups">CUPS</MenuItem>
                    <MenuItem value="raw">RAW</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              {formData.protocol === 'network' && (
                <>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Dirección IP"
                      name="network_address"
                      value={formData.network_address}
                      onChange={handleChange}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Puerto"
                      name="port"
                      type="number"
                      value={formData.port}
                      onChange={handleChange}
                      required
                    />
                  </Grid>
                </>
              )}
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Cola de Impresión"
                  name="queue_name"
                  value={formData.queue_name}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Ancho del Papel (mm)"
                  name="paper_width"
                  type="number"
                  value={formData.paper_width}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Alto del Papel (mm)"
                  name="paper_height"
                  type="number"
                  value={formData.paper_height}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="DPI"
                  name="dpi"
                  type="number"
                  value={formData.dpi}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_default}
                      onChange={(e) => handleChange({
                        target: { name: 'is_default', value: e.target.checked }
                      } as any)}
                      name="is_default"
                    />
                  }
                  label="Impresora Predeterminada"
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
          <Typography variant="h5">Configuración de Impresoras</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedPrinter(null);
              setIsDialogOpen(true);
            }}
          >
            Nueva Impresora
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {testPrintStatus && (
          <Alert 
            severity={testPrintStatus.includes('Error') ? 'error' : 'success'}
            sx={{ mb: 2 }}
            onClose={() => setTestPrintStatus('')}
          >
            {testPrintStatus}
          </Alert>
        )}

        <Grid container spacing={3}>
          {printers.map((printer) => (
            <Grid item xs={12} md={6} key={printer.id}>
              <Paper
                elevation={3}
                sx={{
                  p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  height: '100%',
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {printer.name}
                    {printer.is_default && (
                      <Typography
                        component="span"
                        sx={{
                          ml: 1,
                          fontSize: '0.8rem',
                          color: 'primary.main',
                        }}
                      >
                        (Predeterminada)
                      </Typography>
                    )}
                  </Typography>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleTestPrint(printer)}
                      title="Imprimir prueba"
                    >
                      <Print />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedPrinter(printer);
                        setIsDialogOpen(true);
                      }}
                    >
                      <PrintIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeletePrinter(printer.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Tipo: {printer.type === 'report' ? 'Reportes' : printer.type === 'barcode' ? 'Códigos de Barra' : 'Tickets'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Protocolo: {printer.protocol.toUpperCase()}
                </Typography>
                {printer.network_address && (
                  <Typography variant="body2" color="text.secondary">
                    IP: {printer.network_address}:{printer.port}
                  </Typography>
                )}
                <Typography variant="body2" color="text.secondary">
                  Papel: {printer.paper_width}x{printer.paper_height}mm ({printer.dpi} DPI)
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <PrinterDialog />
      </Paper>
    </Box>
  );
};
