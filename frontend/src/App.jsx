import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ROLES } from './config/supabase'

// Pages
import Login from './pages/Login'
import CreatorDashboard from './pages/CreatorDashboard'
import ApproverADashboard from './pages/ApproverADashboard'
import ApproverBDashboard from './pages/ApproverBDashboard'

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, userRole, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Cargando...</div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(userRole)) {
    return <Navigate to="/" replace />
  }

  return children
}

// Home redirect based on role
const HomeRedirect = () => {
  const { userRole } = useAuth()

  switch (userRole) {
    case ROLES.CREATOR:
      return <Navigate to="/creator" replace />
    case ROLES.APPROVER_A:
      return <Navigate to="/approver-a" replace />
    case ROLES.APPROVER_B:
      return <Navigate to="/approver-b" replace />
    default:
      return <Navigate to="/login" replace />
  }
}

function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomeRedirect />
            </ProtectedRoute>
          }
        />

        <Route
          path="/creator"
          element={
            <ProtectedRoute allowedRoles={[ROLES.CREATOR]}>
              <CreatorDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/approver-a"
          element={
            <ProtectedRoute allowedRoles={[ROLES.APPROVER_A]}>
              <ApproverADashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/approver-b"
          element={
            <ProtectedRoute allowedRoles={[ROLES.APPROVER_B]}>
              <ApproverBDashboard />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App
