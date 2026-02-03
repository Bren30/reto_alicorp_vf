import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import apiClient from '../config/axios'
import { STATUS } from '../config/supabase'

export default function ApproverADashboard() {
  const { user, signOut } = useAuth()
  const [pendingContent, setPendingContent] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchPendingContent()
  }, [])

  const fetchPendingContent = async () => {
    try {
      // En producción, filtrarías por status: pending_approval
      const res = await apiClient.get('/brand-manuals')
      setPendingContent(res.data)
    } catch (error) {
      console.error('Error fetching content:', error)
    }
  }

  const handleApprove = async (manualId) => {
    if (!confirm('¿Aprobar este manual de marca?')) return

    setLoading(true)
    try {
      // TODO: Endpoint para aprobar
      alert('✅ Manual aprobado. Ahora pasa al Aprobador B para auditoría de imagen.')
      fetchPendingContent()
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async (manualId) => {
    const reason = prompt('¿Por qué rechazas este contenido?')
    if (!reason) return

    setLoading(true)
    try {
      // TODO: Endpoint para rechazar
      alert('❌ Manual rechazado. El creador recibirá tu feedback.')
      fetchPendingContent()
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
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
                ✅ Dashboard - Aprobador A
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
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pendientes</p>
                <p className="text-2xl font-semibold text-gray-900">{pendingContent.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Aprobados</p>
                <p className="text-2xl font-semibold text-gray-900">0</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-red-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Rechazados</p>
                <p className="text-2xl font-semibold text-gray-900">0</p>
              </div>
            </div>
          </div>
        </div>

        {/* Pending Content */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">
              Contenido Pendiente de Revisión ({pendingContent.length})
            </h2>
          </div>
          <div className="p-6">
            {pendingContent.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="mt-2 text-gray-500">No hay contenido pendiente de revisión</p>
              </div>
            ) : (
              <div className="space-y-6">
                {pendingContent.map((manual) => (
                  <div
                    key={manual.id}
                    className="border rounded-lg p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {manual.name}
                        </h3>
                        <p className="text-gray-600 mb-3">{manual.description}</p>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Tipo:</span>{' '}
                            <span className="text-gray-600">{manual.product_type}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Tono:</span>{' '}
                            <span className="text-gray-600">{manual.tone}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Target:</span>{' '}
                            <span className="text-gray-600">{manual.target_audience}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Creado:</span>{' '}
                            <span className="text-gray-600">
                              {new Date(manual.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      <span className="ml-4 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                        ⏳ Pendiente
                      </span>
                    </div>

                    {/* Manual Preview */}
                    {manual.full_manual && (
                      <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">Vista Previa del Manual:</h4>
                        <div className="text-sm text-gray-700 space-y-2">
                          <div>
                            <span className="font-medium">Valores:</span>{' '}
                            {manual.full_manual.identidad_marca?.valores?.join(', ')}
                          </div>
                          <div>
                            <span className="font-medium">Colores:</span>{' '}
                            {manual.full_manual.elementos_visuales?.colores_principales?.join(', ')}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-3 justify-end">
                      <button
                        onClick={() => handleReject(manual.id)}
                        disabled={loading}
                        className="px-6 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 font-medium disabled:opacity-50"
                      >
                        ❌ Rechazar
                      </button>
                      <button
                        onClick={() => handleApprove(manual.id)}
                        disabled={loading}
                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium disabled:opacity-50"
                      >
                        ✅ Aprobar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-900 mb-2">
            ℹ️ Permisos de Aprobador A
          </h3>
          <ul className="text-sm text-green-800 space-y-1">
            <li>✅ Revisar manuales de marca y contenido generado</li>
            <li>✅ Aprobar contenido (pasa al Aprobador B para auditoría)</li>
            <li>✅ Rechazar contenido (vuelve al Creador con feedback)</li>
            <li>❌ No puedes crear contenido (solo Creadores)</li>
            <li>❌ No puedes auditar imágenes (solo Aprobador B)</li>
          </ul>
        </div>
      </main>
    </div>
  )
}
