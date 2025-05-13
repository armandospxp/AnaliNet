export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export enum Permission {
  READ = 'read',
  WRITE = 'write',
  ADMIN = 'admin',
  SUPERADMIN = 'superadmin'
}
