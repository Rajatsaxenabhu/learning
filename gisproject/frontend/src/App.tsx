import { BrowserRouter, Route, Routes } from 'react-router'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { useTheme } from '@/lib/theme'
import Home from '@/pages/Home'
import AppPage from '@/pages/AppPage'

function App() {
  const { theme } = useTheme()
  return (
    <BrowserRouter>
      <ToastContainer theme={theme} position="top-right" />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/app" element={<AppPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
