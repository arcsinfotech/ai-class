import { createContext, useContext, useEffect, useState, useMemo } from "react";

interface User {
    id: string
    username: string
    email: string
    role: string
}

interface AuthContextType {
    user: User | null
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

    const value = useMemo(
        () => ({
            user,
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