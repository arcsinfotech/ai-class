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
            document.cookie = `access_token=${accessToken}; path=/`
        }
        if(refreshToken) {
            document.cookie = `refresh_token=${refreshToken}; path=/`
        }

        setUser(user)
    };

    const logout = async () => {
        
        const response = await fetch(`${import.meta.env.VITE_API_URL}/logout`, {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            throw new Error("Failed to logout")
        }

        setUser(null)
    }

    const verifyToken = async () => {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/verify`, {
            method: "POST",
            credentials: "include",
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data?.message || "Failed to verify session")
        }

        return data as { user: User }
    }

    const refreshSession = async () => {

        const response = await fetch(`${import.meta.env.VITE_API_URL}/refresh`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "credentials": "include",
            },
        });

        const data = await response.json();

        if (!response.ok) {
            logout()
            return false
        }

        setUser(data.user ?? null);
        return Boolean(data.user);
    }

    useEffect(() => {
        const bootstrapSession = async () => {

            try {
                const result = await verifyToken();
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
            refreshSession,
            logout,
        }),
        [user, isLoading, setSession, logout, refreshSession]
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