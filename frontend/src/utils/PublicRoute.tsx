import { useAuth } from '../context/AuthProvider'
import { Navigate, Outlet } from 'react-router-dom'

export default function PublicRoute() {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
        return <div>Loading session...</div>
    }

    if (isAuthenticated) {
        return <Navigate to="/" replace/>
    }

    return <Outlet />
}