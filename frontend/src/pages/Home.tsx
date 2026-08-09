import { useAuth } from "../context/AuthProvider"
import { useNavigate } from "react-router-dom"

export default function Home() {
  
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <div>
      <h1>Hello {user?.username}</h1>
      <p>Email: {user?.email}</p>
      <p>Role: {user?.role}</p>

      <button onClick={handleLogout}>Logout</button>
    </div>
  )
}