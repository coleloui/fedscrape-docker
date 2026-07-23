import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Explorer } from '@/pages/Explorer'
import { YieldCurve } from '@/pages/YieldCurve'
import { Chat } from '@/pages/Chat'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path='explorer' element={<Explorer />} />
          <Route path='yield-curve' element={<YieldCurve />} />
          <Route path='chat' element={<Chat />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
