import { createContext, useContext, useEffect, useState, useMemo } from "react";

interface User {
    id: string
    username: string
    email: string
    role: string
}

interface AuthContextType {
    user: User | null
    isAuthenticated: boolean
    isLoading: boolean
    setSession: (session: {user: User, accessToken: string, refreshToken: string}) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export default function AuthProvider({children}: { children: React.ReactNode }) {

    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    const setSession = ({user, accessToken, refreshToken}: {user: User , accessToken: string, refreshToken: string}) => {

        if(accessToken) {
            localStorage.setItem("accessToken", accessToken)
        }
        if(refreshToken) {
            localStorage.setItem("refreshToken", refreshToken)
        }

        setUser(user)
    };

    const logout = () => {
        localStorage.removeItem("accessToken")
        localStorage.removeItem("refreshToken")
        setUser(null)
    }

    const verifyToken = async (token: string) => {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/verify`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                access_token: token
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data?.message || "Failed to verify session")
        }

        return data as { user: User }
    }

    const refreshSession = async () => {
        const refreshToken = localStorage.getItem("refreshToken")

        if (!refreshToken) {
            logout()
            return false
        }

        const response = await fetch(`${import.meta.env.VITE_API_URL}/refresh`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                refresh_token: refreshToken
            })
        });

        const data = await response.json();

        if (!response.ok) {
            logout()
            return false
        }

        if (data?.access_token) {
            localStorage.setItem("accessToken", data.access_token)
        }

        setUser(data.user ?? null);
        return Boolean(data.user);
    }

    useEffect(() => {
        const bootstrapSession = async () => {
            const accessToken = localStorage.getItem("accessToken");

            if (!accessToken) {
                setIsLoading(false)
                return;
            }

            try {
                const result = await verifyToken(accessToken);
                setUser(result.user);
            } catch {
                await refreshSession();
            } finally {
                setIsLoading(false)
            }
        }

        void bootstrapSession();
    }, []);

    const value = useMemo(
        () => ({
            user,
            isAuthenticated: Boolean(user),
            isLoading,
            setSession,
            logout,
        }),
        [user, isLoading, setSession, logout]
    )

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider")
    }

    return context;
}