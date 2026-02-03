import axios from 'axios'
import { supabase } from './supabase'

// Crear instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 300000 // 5 minutos para operaciones con LLM (generación de manuales puede tardar)
})

// Interceptor para agregar token de autenticación en cada request
apiClient.interceptors.request.use(
  async (config) => {
    try {
      console.log('📡 Interceptor: obteniendo sesión...', config.url)
      
      // Timeout de 3 segundos para obtener la sesión
      const sessionPromise = supabase.auth.getSession()
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout obteniendo sesión')), 3000)
      )
      
      const { data: { session } } = await Promise.race([sessionPromise, timeoutPromise])
      console.log('📡 Sesión obtenida:', session ? 'Autenticado' : 'Sin sesión')
      
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`
      }
      
      console.log('📡 Enviando petición:', config.method.toUpperCase(), config.url)
      return config
    } catch (error) {
      console.error('❌ Error en interceptor (continuando sin auth):', error.message)
      // Continuar sin autenticación si falla
      console.log('📡 Enviando petición SIN AUTH:', config.method.toUpperCase(), config.url)
      return config
    }
  },
  (error) => {
    console.error('❌ Error en interceptor request:', error)
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores de respuesta
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado, redirigir al login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
