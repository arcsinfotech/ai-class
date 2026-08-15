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
import Uploads from './pages/Uploads'
import Uploads2 from './pages/Uploads2'

function App() {

  return (
    <>
      <AuthProvider>
        <Router>
          <Routes>

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Home />} />
            <Route path="/users" element={<Users />} />
            <Route path="/upload" element={<Uploads />} />
            <Route path="/upload2" element={<Uploads2 />} />
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
