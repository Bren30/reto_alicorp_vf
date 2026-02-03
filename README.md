# 🚀 Frontend React - Content Suite

Sistema de gestión de contenido con autenticación y control de acceso basado en roles (RBAC).

---

## 📋 Requisitos Previos

- Node.js 18+ 
- npm o yarn
- Backend corriendo en `http://127.0.0.1:8000`
- Proyecto de Supabase configurado

---

## 🔧 Instalación

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de Supabase:

```env
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu-anon-key-aqui
```

**Dónde encontrar las credenciales:**
1. Ve a tu proyecto en [Supabase Dashboard](https://app.supabase.com)
2. Click en "Settings" → "API"
3. Copia:
   - `Project URL` → `VITE_SUPABASE_URL`
   - `anon public` → `VITE_SUPABASE_ANON_KEY`

### 3. Configurar Supabase (Base de Datos)

Ejecuta el script SQL en tu proyecto de Supabase:

1. Ve a SQL Editor en Supabase
2. Copia todo el contenido de `docs/SUPABASE_SETUP.sql`
3. Ejecuta el script

Esto creará:
- ✅ Tabla `user_profiles` con roles
- ✅ RLS (Row Level Security) policies
- ✅ Triggers automáticos
- ✅ Columnas de estado en `brand_manuals`

### 4. Crear usuarios de prueba

En Supabase Dashboard:

**Authentication > Users > Add user > Create new user**

#### Usuario 1: Creador
```
Email: creador@alicorp.com
Password: creador123
User Metadata (JSON):
{
  "role": "creator",
  "name": "Juan Pérez"
}
```

#### Usuario 2: Aprobador A
```
Email: aprobadorA@alicorp.com
Password: aprobadorA123
User Metadata (JSON):
{
  "role": "approver_a",
  "name": "Ana García"
}
```

#### Usuario 3: Aprobador B
```
Email: aprobadorB@alicorp.com
Password: aprobadorB123
User Metadata (JSON):
{
  "role": "approver_b",
  "name": "Carlos Rodríguez"
}
```

---

## 🚀 Ejecución

```bash
npm run dev
```

Abre http://localhost:3000

---

## 🎭 Roles y Funcionalidades

### 👨‍💻 **Creador** (Creator)
**Acceso:** Solo Módulos I y II

**Puede:**
- ✅ Generar manuales de marca (Módulo I)
- ✅ Generar contenido con RAG (Módulo II)
  - Image prompts
  - Descripciones de producto
  - Scripts de video
- ✅ Ver estado de sus contenidos

**No puede:**
- ❌ Aprobar/rechazar contenido
- ❌ Auditar imágenes

**Login:** `creador@alicorp.com` / `creador123`

---

### ✅ **Aprobador A** (First Reviewer)
**Acceso:** Solo flujo de aprobación

**Puede:**
- ✅ Ver contenido pendiente de revisión
- ✅ Aprobar contenido → pasa a Aprobador B
- ✅ Rechazar contenido → vuelve a Creador con feedback

**No puede:**
- ❌ Crear contenido
- ❌ Auditar imágenes (solo Aprobador B)

**Login:** `aprobadorA@alicorp.com` / `aprobadorA123`

---

### 🔍 **Aprobador B** (Final Auditor)
**Acceso:** Solo Módulo III (Auditoría)

**Puede:**
- ✅ Auditar imágenes contra manual de marca
- ✅ Ver resultado detallado de IA:
  - Score de cumplimiento (0-100)
  - Issues detectados
  - Recomendaciones específicas
  - Scores por categoría
- ✅ Aprobación final basada en auditoría

**No puede:**
- ❌ Crear contenido
- ❌ Hacer primera aprobación (solo Aprobador A)

**Login:** `aprobadorB@alicorp.com` / `aprobadorB123`

---

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── config/
│   │   └── supabase.js          # Configuración de Supabase
│   ├── context/
│   │   └── AuthContext.jsx      # Context de autenticación
│   ├── pages/
│   │   ├── Login.jsx            # Página de login
│   │   ├── CreatorDashboard.jsx       # Dashboard Creador
│   │   ├── ApproverADashboard.jsx     # Dashboard Aprobador A
│   │   └── ApproverBDashboard.jsx     # Dashboard Aprobador B
│   ├── App.jsx                  # Rutas y protección
│   ├── main.jsx                 # Entry point
│   └── index.css                # Estilos globales
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

---

## 🔒 Seguridad

### **Autenticación:**
- JWT tokens de Supabase
- Sesiones persistentes
- Auto-logout en token expirado

### **Autorización:**
- Row Level Security (RLS) en Supabase
- Rutas protegidas en frontend
- Validación de roles en cada request

### **Políticas RLS:**
```sql
-- Creadores solo ven sus manuales
CREATE POLICY "Creators can view own manuals"
  ON brand_manuals FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM user_profiles
    WHERE user_profiles.user_id = auth.uid()
    AND user_profiles.role = 'creator'
  ));

-- Aprobadores ven todos
CREATE POLICY "Approvers can view all manuals"
  ON brand_manuals FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM user_profiles
    WHERE user_profiles.user_id = auth.uid()
    AND user_profiles.role IN ('approver_a', 'approver_b')
  ));
```

---

## 🎨 Stack Tecnológico

- **Framework:** React 18
- **Bundler:** Vite
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **Auth:** Supabase Auth
- **Database:** Supabase (Postgres + RLS)
- **HTTP Client:** Axios
- **State Management:** React Context API

---

## 🔗 Integración con Backend

El frontend se comunica con el backend FastAPI a través del proxy de Vite:

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

**Ejemplo de llamada:**
```javascript
// En el frontend
const res = await axios.post('/api/brand-manuals/generate', data)

// Se traduce a:
// POST http://127.0.0.1:8000/brand-manuals/generate
```

---

## 🧪 Testing

### **Flujo de Testing Completo:**

1. **Login como Creador:**
   ```
   Email: creador@alicorp.com
   Password: creador123
   ```
   - Crea un manual de marca
   - Genera contenido (image prompt)
   - Ve estado "Pendiente Aprobación"

2. **Login como Aprobador A:**
   ```
   Email: aprobadorA@alicorp.com
   Password: aprobadorA123
   ```
   - Ve el manual pendiente
   - Aprueba (o rechaza con feedback)

3. **Login como Aprobador B:**
   ```
   Email: aprobadorB@alicorp.com
   Password: aprobadorB123
   ```
   - Selecciona el manual aprobado
   - Sube una imagen
   - Audita con IA
   - Ve resultado detallado

---

## 📊 Flujo de Estados

```
┌─────────────┐
│   CREADOR   │
│  Crea manual│
└──────┬──────┘
       │
       v
  Status: pending_approval
       │
       v
┌─────────────┐
│ APROBADOR A │
│   Revisa    │
└──────┬──────┘
       │
       ├─ APRUEBA → Status: approved
       │             │
       │             v
       │      ┌─────────────┐
       │      │ APROBADOR B │
       │      │ Audita img  │
       │      └──────┬──────┘
       │             │
       │             ├─ Score >= 75 → approved_final
       │             └─ Score < 75 → rejected
       │
       └─ RECHAZA → Status: rejected
                    (vuelve a Creador)
```

---

## 🐛 Troubleshooting

### Error: "Invalid supabase URL"
- Verifica que `.env` tenga las credenciales correctas
- Reinicia el servidor de desarrollo: `npm run dev`

### Error: "RLS policy violated"
- Verifica que ejecutaste el script SQL completo
- Confirma que los usuarios tienen roles asignados en `user_profiles`

### Error: "Cannot read properties of null"
- Limpia localStorage: `localStorage.clear()`
- Vuelve a hacer login

### CORS Error con backend
- Asegúrate que FastAPI tenga CORS habilitado:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

---

## 🚧 Próximas Mejoras

- [ ] Notificaciones en tiempo real (Supabase Realtime)
- [ ] Historial de aprobaciones/rechazos
- [ ] Filtros y búsqueda en dashboards
- [ ] Exportar manuales a PDF
- [ ] Dark mode
- [ ] Tests unitarios (Vitest)
- [ ] Tests E2E (Playwright)

---

## 📚 Documentación Adicional

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [React Router Docs](https://reactrouter.com)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

---

**Última actualización:** 2026-02-03  
**Versión:** 1.0.0  
**Estado:** ✅ Producción
