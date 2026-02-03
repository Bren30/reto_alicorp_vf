-- ================================================
-- SETUP DE AUTENTICACIÓN Y ROLES EN SUPABASE
-- ================================================

-- 1. CREAR TABLA DE PERFILES DE USUARIO
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  role TEXT NOT NULL CHECK (role IN ('creator', 'approver_a', 'approver_b')),
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);

-- 2. HABILITAR ROW LEVEL SECURITY (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Los usuarios pueden ver su propio perfil
CREATE POLICY "Users can view own profile"
  ON user_profiles
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Los usuarios pueden actualizar su propio perfil
CREATE POLICY "Users can update own profile"
  ON user_profiles
  FOR UPDATE
  USING (auth.uid() = user_id);

-- 3. FUNCIÓN PARA CREAR PERFIL AUTOMÁTICAMENTE AL REGISTRARSE
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (user_id, role, name)
  VALUES (
    NEW.id, 
    COALESCE(NEW.raw_user_meta_data->>'role', 'creator'),
    COALESCE(NEW.raw_user_meta_data->>'name', NEW.email)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para crear perfil automáticamente
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 4. AGREGAR COLUMNAS NECESARIAS A BRAND_MANUALS (si no existen)
ALTER TABLE brand_manuals 
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES auth.users(id);

ALTER TABLE brand_manuals 
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending_approval' 
CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected'));

ALTER TABLE brand_manuals 
ADD COLUMN IF NOT EXISTS approved_by_a UUID REFERENCES auth.users(id);

ALTER TABLE brand_manuals 
ADD COLUMN IF NOT EXISTS approved_by_b UUID REFERENCES auth.users(id);

ALTER TABLE brand_manuals 
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- 5. RLS PARA BRAND_MANUALS
ALTER TABLE brand_manuals ENABLE ROW LEVEL SECURITY;

-- Policy: Creadores pueden ver sus propios manuales
CREATE POLICY "Creators can view own manuals"
  ON brand_manuals
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_profiles.user_id = auth.uid()
      AND user_profiles.role = 'creator'
    )
  );

-- Policy: Aprobadores pueden ver todos los manuales
CREATE POLICY "Approvers can view all manuals"
  ON brand_manuals
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_profiles.user_id = auth.uid()
      AND user_profiles.role IN ('approver_a', 'approver_b')
    )
  );

-- Policy: Creadores pueden insertar manuales
CREATE POLICY "Creators can insert manuals"
  ON brand_manuals
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_profiles.user_id = auth.uid()
      AND user_profiles.role = 'creator'
    )
  );

-- Policy: Aprobador A puede actualizar (aprobar/rechazar)
CREATE POLICY "Approver A can update manuals"
  ON brand_manuals
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_profiles.user_id = auth.uid()
      AND user_profiles.role = 'approver_a'
    )
  );

-- 6. CREAR USUARIOS DE PRUEBA (ejecutar en consola SQL de Supabase)
-- Nota: Los passwords deben cambiarse en producción

-- Usuario Creador
-- Email: creador@alicorp.com
-- Password: creador123
-- Ejecutar en la consola de Supabase Auth o usar la UI

-- Usuario Aprobador A
-- Email: aprobadorA@alicorp.com
-- Password: aprobadorA123

-- Usuario Aprobador B
-- Email: aprobadorB@alicorp.com
-- Password: aprobadorB123

-- ================================================
-- INSTRUCCIONES PARA CREAR USUARIOS EN SUPABASE UI:
-- ================================================
-- 1. Ve a Authentication > Users en tu dashboard de Supabase
-- 2. Click en "Add user" > "Create new user"
-- 3. Para cada usuario:
--    a) Email: creador@alicorp.com
--    b) Password: creador123
--    c) User Metadata (JSON):
--       {
--         "role": "creator",
--         "name": "Juan Pérez"
--       }
-- 4. Repetir para aprobadorA y aprobadorB

-- ================================================
-- VERIFICACIÓN
-- ================================================

-- Verificar que los usuarios tengan perfiles
SELECT 
  u.email,
  p.role,
  p.name
FROM auth.users u
LEFT JOIN user_profiles p ON p.user_id = u.id;

-- Ver manuales con información de aprobadores
SELECT 
  bm.id,
  bm.name,
  bm.status,
  u1.email as created_by,
  u2.email as approved_by_a,
  u3.email as approved_by_b
FROM brand_manuals bm
LEFT JOIN auth.users u1 ON bm.created_by = u1.id
LEFT JOIN auth.users u2 ON bm.approved_by_a = u2.id
LEFT JOIN auth.users u3 ON bm.approved_by_b = u3.id;
