import './App.css'
import Home  from './pages/Home'
import Login from './pages/auth/Login'

import { 
  BrowserRouter as Router, 
  Routes, 
  Route 
} from 'react-router-dom'

import AuthProvider from './context/AuthProvider'
import ProtectedRoute from './utils/ProtectedRoute'
import PublicRoute from './utils/PublicRoute'
import Users from './pages/Users'

function App() {

  return (
    <>
      <AuthProvider>
        <Router>
          <Routes>

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Home />} />
            <Route path="/users" element={<Users />} />
          </Route>

          <Route element={<PublicRoute />}>
            <Route path="/login" element={<Login />} />
          </Route>
    
          </Routes>
        </Router>      
      </AuthProvider>
    </>
  )
}

export default App
