import { useAuth } from '../context/AuthProvider'
import { Navigate, Outlet } from 'react-router-dom'

export default function ProtectedRoute() {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
        return <div>Loading session...</div>
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace/>
    }

    return <Outlet />

}