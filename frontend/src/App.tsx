import './App.css'
import Home  from './pages/Home'
import Login from './pages/auth/Login'

import { 
  BrowserRouter as Router, 
  Routes, 
  Route 
} from 'react-router-dom'

import AuthProvider from './context/AuthProvider'

function App() {

  return (
    <>
      <AuthProvider>

        <Router>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </Router>      
      </AuthProvider>
    </>
  )
}

export default App
