import { createClient } from '@supabase/supabase-js'

// Reemplaza con tus credenciales de Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://tu-proyecto.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'tu-anon-key'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Roles disponibles
export const ROLES = {
  CREATOR: 'creator',
  APPROVER_A: 'approver_a',
  APPROVER_B: 'approver_b'
}

// Estados de contenido
export const STATUS = {
  DRAFT: 'draft',
  PENDING_APPROVAL: 'pending_approval',
  APPROVED: 'approved',
  REJECTED: 'rejected'
}
