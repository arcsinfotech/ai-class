import { useEffect, useState } from 'react';

interface User {
    id: string
    username: string
    email: string
    role: string
    created_at: Date
    updated_at: Date
}

export default function Users() {

    const [users, setUsers] = useState<User[]>([]);
    const [offset, setOffset] = useState(0);
    const [limit, setLimit] = useState(10);

    useEffect( () => {
        const fetchUsers = async () => {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/users?offset=${offset}&limit=${limit}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `${localStorage.getItem("accessToken")}`
                }
            })
    
            const data = await response.json();
    
            if (data.users) {
                setUsers(data.users);
            }
        }

        void fetchUsers();
    }, [offset]);

    return (
     <>
     <h1>Users</h1>
     <ul>
        {users.map((user) => (
            <li key={user.id}>{user.username}</li>
        ))}
     </ul>
     <button onClick={() => setOffset(offset - limit)} disabled={offset === 0}>Previous</button>
     <button onClick={() => setOffset(offset + limit)} disabled={users.length < limit}>Next</button>
     </>   
    )    
}