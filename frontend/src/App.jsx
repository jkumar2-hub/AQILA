import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import UploadPage   from './pages/UploadPage'
import QueryPage    from './pages/QueryPage'
import EvidencePage from './pages/EvidencePage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Default → Upload */}
        <Route index element={<Navigate to="/upload" replace />} />
        <Route path="/upload"   element={<UploadPage />} />
        <Route path="/query"    element={<QueryPage />} />
        <Route path="/evidence" element={<EvidencePage />} />
        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/upload" replace />} />
      </Route>
    </Routes>
  )
}
