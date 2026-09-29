import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../../context/AuthProvider"

export default function Login() {

    const navigate = useNavigate()

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const { setSession } = useAuth()


    const handleLogin = async (event: React.SubmitEvent<HTMLFormElement>) => {
        
        event?.preventDefault()
        setIsSubmitting(true)

        try {

            const response = await fetch(`${import.meta.env.VITE_API_URL}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({ email, password })
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || "Login failed")
            }

            setSession({
                user: data.user,
                accessToken: data.access_token,
                refreshToken: data.refresh_token

            })
            
            navigate("/")

        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred")
        } finally {
            setIsSubmitting(false)
        }
        

    }

    const loginWithGithub = () => {
        window.location.href = `${import.meta.env.VITE_API_URL}/auth/github`
    }
  
    return (
        <form onSubmit={handleLogin}>
            <label>
                Email
                <input 
                    type="email" 
                    value= {email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                />
            </label>

            <label >
                Password
                <input 
                    type="password" 
                    value= {password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                />
            </label>

            {error ? <p>{error}</p> : null}

            <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Logging in..." : "Login"} 
            </button>
            
            <button type="button" onClick={loginWithGithub}>Login with Github</button>
        </form>
  )
}