import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import apiClient from '../config/axios'

export default function CreatorDashboard() {
  const { user, signOut } = useAuth()
  const [manuals, setManuals] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showContentModal, setShowContentModal] = useState(false)
  const [selectedManual, setSelectedManual] = useState(null)

  useEffect(() => {
    fetchManuals()
  }, [])

  const fetchManuals = async () => {
    try {
      const res = await apiClient.get('/brand-manuals')
      setManuals(res.data)
    } catch (error) {
      console.error('Error fetching manuals:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                🎨 Dashboard - Creador
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={signOut}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Action Buttons */}
        <div className="mb-8 flex gap-4">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-sm"
          >
            + Nuevo Manual de Marca
          </button>
          <button
            onClick={() => {
              if (manuals.length > 0) {
                setSelectedManual(manuals[0])
                setShowContentModal(true)
              } else {
                alert('Primero crea un manual de marca')
              }
            }}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium shadow-sm"
          >
            + Generar Contenido
          </button>
        </div>

        {/* Manuals List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">
              Mis Manuales de Marca
            </h2>
          </div>
          <div className="p-6">
            {manuals.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No tienes manuales creados. ¡Crea tu primer manual!
              </p>
            ) : (
              <div className="grid gap-4">
                {manuals.map((manual) => (
                  <div
                    key={manual.id}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">
                          {manual.name}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {manual.description}
                        </p>
                        <div className="flex gap-4 mt-3 text-sm text-gray-500">
                          <span>Tipo: {manual.product_type}</span>
                          <span>Tono: {manual.tone}</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-2">
                          Creado: {new Date(manual.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex flex-col gap-2">
                        <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                          ⏳ Pendiente Aprobación
                        </span>
                        <button
                          onClick={() => {
                            setSelectedManual(manual)
                            setShowContentModal(true)
                          }}
                          className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
                        >
                          Generar Contenido
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">
            ℹ️ Permisos de Creador
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✅ Módulo I: Crear manuales de marca con IA</li>
            <li>✅ Módulo II: Generar contenido (image prompts, descripciones, scripts)</li>
            <li>❌ No puedes aprobar contenido (solo Aprobadores)</li>
            <li>❌ No puedes auditar imágenes (solo Aprobador B)</li>
          </ul>
        </div>
      </main>

      {/* Create Manual Modal */}
      {showCreateModal && (
        <CreateManualModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            fetchManuals()
          }}
        />
      )}

      {/* Generate Content Modal */}
      {showContentModal && selectedManual && (
        <GenerateContentModal
          manual={selectedManual}
          onClose={() => setShowContentModal(false)}
        />
      )}
    </div>
  )
}

// Create Manual Modal Component
function CreateManualModal({ onClose, onSuccess }) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    product_type: '',
    tone: '',
    target_audience: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await apiClient.post('/brand-manuals/generate', formData)
      alert('✅ Manual generado exitosamente')
      onSuccess()
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold mb-4">Crear Manual de Marca</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nombre del Producto</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="Ej: Quinua Crunch"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Descripción</label>
            <textarea
              required
              rows="3"
              className="w-full px-3 py-2 border rounded-lg"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe el producto..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Tipo de Producto</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg"
              value={formData.product_type}
              onChange={(e) => setFormData({...formData, product_type: e.target.value})}
              placeholder="Ej: snack saludable"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Tono de Comunicación</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg"
              value={formData.tone}
              onChange={(e) => setFormData({...formData, tone: e.target.value})}
              placeholder="Ej: divertido, cercano, profesional"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Público Objetivo</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg"
              value={formData.target_audience}
              onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
              placeholder="Ej: Gen Z y Millennials 18-35 años"
            />
          </div>
          <div className="flex gap-3 justify-end pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Generando...' : 'Generar Manual'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Generate Content Modal Component
function GenerateContentModal({ manual, onClose }) {
  const [contentType, setContentType] = useState('image_prompt')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setResult(null)

    try {
      const res = await apiClient.post('/content/generate', {
        manual_id: manual.id,
        content_type: contentType
      })
      setResult(res.data.generated_text)
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Generar Contenido - {manual.name}</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Tipo de Contenido</label>
          <select
            value={contentType}
            onChange={(e) => setContentType(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg"
          >
            <option value="image_prompt">Image Prompt</option>
            <option value="product_description">Descripción de Producto</option>
            <option value="video_script">Script de Video</option>
          </select>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 mb-4"
        >
          {loading ? 'Generando...' : 'Generar Contenido'}
        </button>

        {result && (
          <div className="bg-gray-50 border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Contenido Generado:</h3>
            <p className="text-sm whitespace-pre-wrap">{result}</p>
          </div>
        )}

        <div className="flex justify-end pt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}
