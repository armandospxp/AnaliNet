import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Print as PrintIcon,
  LocalPrintshop as PrinterIcon,
  Refresh as ReprintIcon,
  QrCode as BarcodeIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';

interface BarcodeData {
  orderId: number;
  patientName: string;
  sampleType: string;
  analysisCode: string;
  analysisName: string;
  containerType: string;
  barcodeContent: string;
  printed: boolean;
  printDate?: string;
}

interface Printer {
  id: number;
  name: string;
  type: 'barcode' | 'ticket';
}

export const BarcodeGenerator: React.FC = () => {
  const [barcodes, setBarcodes] = useState<BarcodeData[]>([]);
  const [selectedPrinter, setSelectedPrinter] = useState<number | null>(null);
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [error, setError] = useState<string>('');
  const [isPrinting, setIsPrinting] = useState(false);
  const [showPrinterDialog, setShowPrinterDialog] = useState(false);

  const loadPrinters = async () => {
    try {
      const response = await api.get('/printers?type=barcode');
      setPrinters(response.data);
      // Establecer impresora por defecto si existe
      const defaultPrinter = response.data.find((p: Printer) => p.type === 'barcode');
      if (defaultPrinter) {
        setSelectedPrinter(defaultPrinter.id);
      }
    } catch (error) {
      setError('Error al cargar las impresoras');
    }
  };

  const handlePrintBarcodes = async (barcodeIds: number[]) => {
    if (!selectedPrinter) {
      setShowPrinterDialog(true);
      return;
    }

    setIsPrinting(true);
    try {
      await api.post('/print/barcodes', {
        printer_id: selectedPrinter,
        barcode_ids: barcodeIds,
      });

      // Actualizar estado de impresión
      setBarcodes(prev =>
        prev.map(barcode =>
          barcodeIds.includes(barcode.orderId)
            ? { ...barcode, printed: true, printDate: new Date().toISOString() }
            : barcode
        )
      );
    } catch (error) {
      setError('Error al imprimir los códigos de barras');
    } finally {
      setIsPrinting(false);
    }
  };

  const handleGenerateBarcode = async (orderId: number) => {
    try {
      const response = await api.post(`/orders/${orderId}/barcodes`);
      setBarcodes(prev => [...prev, ...response.data]);
    } catch (error) {
      setError('Error al generar los códigos de barras');
    }
  };

  const PrinterSelectionDialog: React.FC = () => (
    <Dialog open={showPrinterDialog} onClose={() => setShowPrinterDialog(false)}>
      <DialogTitle>Seleccionar Impresora</DialogTitle>
      <DialogContent>
        <FormControl fullWidth sx={{ mt: 2 }}>
          <InputLabel>Impresora</InputLabel>
          <Select
            value={selectedPrinter || ''}
            label="Impresora"
            onChange={(e) => setSelectedPrinter(e.target.value as number)}
          >
            {printers.map((printer) => (
              <MenuItem key={printer.id} value={printer.id}>
                {printer.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowPrinterDialog(false)}>Cancelar</Button>
        <Button
          onClick={() => {
            setShowPrinterDialog(false);
            if (selectedPrinter) {
              handlePrintBarcodes(barcodes.filter(b => !b.printed).map(b => b.orderId));
            }
          }}
          variant="contained"
          disabled={!selectedPrinter}
        >
          Confirmar
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5">Generación de Códigos de Barras</Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<PrinterIcon />}
              onClick={() => setShowPrinterDialog(true)}
            >
              Seleccionar Impresora
            </Button>
            <Button
              variant="contained"
              startIcon={<PrintIcon />}
              onClick={() => handlePrintBarcodes(barcodes.filter(b => !b.printed).map(b => b.orderId))}
              disabled={!selectedPrinter || isPrinting || barcodes.every(b => b.printed)}
            >
              Imprimir Pendientes
            </Button>
          </Box>
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
                <TableCell>Orden</TableCell>
                <TableCell>Paciente</TableCell>
                <TableCell>Muestra</TableCell>
                <TableCell>Análisis</TableCell>
                <TableCell>Contenedor</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {barcodes.map((barcode) => (
                <TableRow key={`${barcode.orderId}-${barcode.analysisCode}`}>
                  <TableCell>{barcode.orderId}</TableCell>
                  <TableCell>{barcode.patientName}</TableCell>
                  <TableCell>{barcode.sampleType}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BarcodeIcon fontSize="small" />
                      {barcode.analysisName}
                      <Typography variant="caption" color="text.secondary">
                        ({barcode.analysisCode})
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{barcode.containerType}</TableCell>
                  <TableCell>
                    <Chip
                      label={barcode.printed ? 'Impreso' : 'Pendiente'}
                      color={barcode.printed ? 'success' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handlePrintBarcodes([barcode.orderId])}
                      disabled={isPrinting || !selectedPrinter}
                      title={barcode.printed ? 'Reimprimir' : 'Imprimir'}
                    >
                      {barcode.printed ? <ReprintIcon /> : <PrintIcon />}
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <PrinterSelectionDialog />
      </Paper>
    </Box>
  );
};
