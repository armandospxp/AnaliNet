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
  Checkbox,
  ListItemText,
  OutlinedInput,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';
import { Permission } from '../../types/auth';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  permissions: Permission[];
  is_active: boolean;
}

const ROLES = [
  'Administrador',
  'Gestor de Software',
  'Bioquímico',
  'Técnico de Laboratorio',
  'Recepcionista',
];

const PERMISSIONS: Record<string, Permission[]> = {
  'Administrador': [
    Permission.MANAGE_USERS,
    Permission.MANAGE_ROLES,
    Permission.MANAGE_SYSTEM,
    Permission.MANAGE_DATABASE,
    Permission.MANAGE_EQUIPMENT,
    Permission.MANAGE_TESTS,
    Permission.VALIDATE_RESULTS,
    Permission.ENTER_RESULTS,
    Permission.MANAGE_PATIENTS,
    Permission.CREATE_ORDERS,
  ],
  'Gestor de Software': [
    Permission.MANAGE_USERS,
    Permission.MANAGE_ROLES,
    Permission.MANAGE_SYSTEM,
    Permission.MANAGE_EQUIPMENT,
    Permission.MANAGE_TESTS,
    Permission.VALIDATE_RESULTS,
    Permission.ENTER_RESULTS,
    Permission.MANAGE_PATIENTS,
    Permission.CREATE_ORDERS,
  ],
  'Bioquímico': [
    Permission.MANAGE_TESTS,
    Permission.VALIDATE_RESULTS,
    Permission.ENTER_RESULTS,
    Permission.VIEW_RESULTS,
  ],
  'Técnico de Laboratorio': [
    Permission.ENTER_RESULTS,
    Permission.VIEW_RESULTS,
  ],
  'Recepcionista': [
    Permission.MANAGE_PATIENTS,
    Permission.CREATE_ORDERS,
    Permission.VIEW_RESULTS,
  ],
};

export const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      setError('Error al cargar los usuarios');
    }
  };

  const handleSaveUser = async (userData: Partial<User>) => {
    try {
      if (selectedUser?.id) {
        await api.put(`/users/${selectedUser.id}`, userData);
      } else {
        await api.post('/users', userData);
      }
      loadUsers();
      setIsDialogOpen(false);
      setSelectedUser(null);
    } catch (error) {
      setError('Error al guardar el usuario');
    }
  };

  const handleDeleteUser = async (id: number) => {
    try {
      await api.delete(`/users/${id}`);
      loadUsers();
    } catch (error) {
      setError('Error al eliminar el usuario');
    }
  };

  const UserDialog: React.FC = () => {
    const [formData, setFormData] = useState<Partial<User>>(
      selectedUser || {
        username: '',
        email: '',
        full_name: '',
        role: '',
        permissions: [],
        is_active: true,
      }
    );
    const [password, setPassword] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    };

    const handleRoleChange = (event: React.ChangeEvent<{ value: unknown }>) => {
      const role = event.target.value as string;
      setFormData(prev => ({
        ...prev,
        role,
        permissions: PERMISSIONS[role] || [],
      }));
    };

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      const userData = {
        ...formData,
        ...(password && { password }),
      };
      handleSaveUser(userData);
    };

    return (
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {selectedUser ? 'Editar Usuario' : 'Nuevo Usuario'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nombre de Usuario"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Correo Electrónico"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Nombre Completo"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                />
              </Grid>
              {!selectedUser && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Contraseña"
                    name="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required={!selectedUser}
                  />
                </Grid>
              )}
              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>Rol</InputLabel>
                  <Select
                    value={formData.role}
                    label="Rol"
                    onChange={handleRoleChange}
                  >
                    {ROLES.map((role) => (
                      <MenuItem key={role} value={role}>
                        {role}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Permisos</InputLabel>
                  <Select
                    multiple
                    value={formData.permissions}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      permissions: e.target.value as Permission[],
                    }))}
                    input={<OutlinedInput label="Permisos" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(selected as Permission[]).map((value) => (
                          <Chip key={value} label={value} size="small" />
                        ))}
                      </Box>
                    )}
                  >
                    {Object.values(Permission).map((permission) => (
                      <MenuItem key={permission} value={permission}>
                        <Checkbox checked={formData.permissions?.includes(permission)} />
                        <ListItemText primary={permission} />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
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
          <Typography variant="h5">Gestión de Usuarios</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedUser(null);
              setIsDialogOpen(true);
            }}
          >
            Nuevo Usuario
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Usuario</TableCell>
                <TableCell>Nombre Completo</TableCell>
                <TableCell>Correo</TableCell>
                <TableCell>Rol</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.full_name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Chip
                      icon={<SecurityIcon />}
                      label={user.role}
                      size="small"
                      color={
                        user.role === 'Administrador' ? 'error' :
                        user.role === 'Gestor de Software' ? 'warning' :
                        user.role === 'Bioquímico' ? 'success' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_active ? 'Activo' : 'Inactivo'}
                      color={user.is_active ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedUser(user);
                        setIsDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteUser(user.id)}
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

        <UserDialog />
      </Paper>
    </Box>
  );
};
