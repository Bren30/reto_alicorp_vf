import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import apiClient from '../config/axios'

export default function ApproverBDashboard() {
  const { user, signOut } = useAuth()
  const [manuals, setManuals] = useState([])
  const [selectedManual, setSelectedManual] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [auditResult, setAuditResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchApprovedManuals()
  }, [])

  const fetchApprovedManuals = async () => {
    try {
      // En producción, filtrarías solo los aprobados por A
      const res = await apiClient.get('/brand-manuals')
      setManuals(res.data)
      if (res.data.length > 0) {
        setSelectedManual(res.data[0])
      }
    } catch (error) {
      console.error('Error fetching manuals:', error)
    }
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImageFile(file)
      setImagePreview(URL.createObjectURL(file))
      setAuditResult(null)
    }
  }

  const handleAudit = async () => {
    if (!imageFile || !selectedManual) {
      alert('Por favor selecciona un manual y una imagen')
      return
    }

    setLoading(true)
    setAuditResult(null)

    try {
      const formData = new FormData()
      formData.append('manual_id', selectedManual.id)
      formData.append('image', imageFile)

      const res = await apiClient.post('/audit/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setAuditResult(res.data)
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-600'
    if (score >= 75) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score) => {
    if (score >= 85) return 'bg-green-100 border-green-300'
    if (score >= 75) return 'bg-yellow-100 border-yellow-300'
    return 'bg-red-100 border-red-300'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                🔍 Dashboard - Aprobador B (Auditoría)
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Manual Selection & Image Upload */}
          <div className="space-y-6">
            {/* Manual Selection */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                1. Selecciona el Manual de Marca
              </h2>
              <select
                value={selectedManual?.id || ''}
                onChange={(e) => {
                  const manual = manuals.find(m => m.id === e.target.value)
                  setSelectedManual(manual)
                  setAuditResult(null)
                }}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">-- Selecciona un manual --</option>
                {manuals.map((manual) => (
                  <option key={manual.id} value={manual.id}>
                    {manual.name}
                  </option>
                ))}
              </select>

              {selectedManual && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">{selectedManual.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{selectedManual.description}</p>
                  {selectedManual.full_manual?.elementos_visuales && (
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>
                        <span className="font-medium">Colores principales:</span>{' '}
                        {selectedManual.full_manual.elementos_visuales.colores_principales?.join(', ')}
                      </div>
                      <div>
                        <span className="font-medium">Logo tamaño mínimo:</span>{' '}
                        {selectedManual.full_manual.elementos_visuales.uso_logo?.tamano_minimo}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Image Upload */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                2. Sube la Imagen para Auditar
              </h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="cursor-pointer flex flex-col items-center"
                >
                  {imagePreview ? (
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="max-h-64 rounded-lg mb-4"
                    />
                  ) : (
                    <>
                      <svg
                        className="h-12 w-12 text-gray-400 mb-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                      <p className="text-gray-600 mb-2">
                        Click para seleccionar una imagen
                      </p>
                    </>
                  )}
                  <p className="text-sm text-gray-500">
                    PNG, JPG hasta 10MB
                  </p>
                </label>
              </div>
            </div>

            {/* Audit Button */}
            <button
              onClick={handleAudit}
              disabled={!selectedManual || !imageFile || loading}
              className="w-full px-6 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Auditando...' : '🔍 Auditar Imagen'}
            </button>
          </div>

          {/* Right Column - Audit Results */}
          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                3. Resultado de Auditoría
              </h2>

              {!auditResult && !loading && (
                <div className="text-center py-12">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400 mb-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <p className="text-gray-500">
                    Los resultados de la auditoría aparecerán aquí
                  </p>
                </div>
              )}

              {loading && (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Analizando imagen con IA...</p>
                </div>
              )}

              {auditResult && (
                <div className="space-y-6">
                  {/* Score */}
                  <div className={`rounded-lg border-2 p-6 ${getScoreBgColor(auditResult.score)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-lg font-semibold">Score de Cumplimiento</span>
                      <span className={`text-5xl font-bold ${getScoreColor(auditResult.score)}`}>
                        {auditResult.score}/100
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {auditResult.compliant ? (
                        <span className="text-green-700 font-medium">✅ Cumple con el manual</span>
                      ) : (
                        <span className="text-red-700 font-medium">❌ No cumple con el manual</span>
                      )}
                    </div>
                  </div>

                  {/* Analysis */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Análisis General:</h3>
                    <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                      {auditResult.analysis}
                    </p>
                  </div>

                  {/* Issues */}
                  {auditResult.issues && auditResult.issues.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">
                        ⚠️ Problemas Encontrados ({auditResult.issues.length}):
                      </h3>
                      <ul className="space-y-2">
                        {auditResult.issues.map((issue, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm bg-red-50 p-3 rounded">
                            <span className="text-red-600 font-bold">•</span>
                            <span className="text-red-800">{issue}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {auditResult.recommendations && auditResult.recommendations.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">
                        💡 Recomendaciones ({auditResult.recommendations.length}):
                      </h3>
                      <ul className="space-y-2">
                        {auditResult.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm bg-blue-50 p-3 rounded">
                            <span className="text-blue-600 font-bold">→</span>
                            <span className="text-blue-800">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Category Scores */}
                  {auditResult.category_scores && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Scores por Categoría:</h3>
                      <div className="space-y-3">
                        {Object.entries(auditResult.category_scores).map(([category, score]) => (
                          <div key={category}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-700 capitalize">
                                {category.replace('_', ' ')}
                              </span>
                              <span className={`font-semibold ${getScoreColor(score)}`}>
                                {score}/100
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  score >= 85 ? 'bg-green-600' :
                                  score >= 75 ? 'bg-yellow-600' :
                                  'bg-red-600'
                                }`}
                                style={{ width: `${score}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="font-semibold text-purple-900 mb-2">
            ℹ️ Permisos de Aprobador B
          </h3>
          <ul className="text-sm text-purple-800 space-y-1">
            <li>✅ Módulo III: Auditar imágenes contra manuales de marca con IA</li>
            <li>✅ Ver resultados detallados de cumplimiento (score, issues, recomendaciones)</li>
            <li>✅ Aprobación final basada en auditoría</li>
            <li>❌ No puedes crear contenido (solo Creadores)</li>
            <li>❌ No puedes hacer la primera aprobación (solo Aprobador A)</li>
          </ul>
        </div>
      </main>
    </div>
  )
}
