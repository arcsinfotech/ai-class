import { useAuth } from "../context/AuthProvider"

export default function Home() {
  
  const { user, logout } = useAuth()

  return (
    <div>
      <h1>Hello {user?.username}</h1>
      <p>Email: {user?.email}</p>
      <p>Role: {user?.role}</p>

      <button onClick={logout}>Logout</button>
    </div>
  )
}