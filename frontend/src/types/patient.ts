export interface Patient {
  id: number;
  name: string;
  document_type: string;
  document_number: string;
  birth_date: string;
  gender: string;
  email?: string;
  phone?: string;
  address?: string;
  created_at: string;
  updated_at: string;
}
