import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard2 } from '@/pages/Dashboard2'
import { Dashboard } from '@/pages/Dashboard'
import { Explorer } from '@/pages/Explorer'
import { YieldCurve } from '@/pages/YieldCurve'
import { Chat } from '@/pages/Chat'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* New single-page terminal layout — no shared Layout/Navbar shell. */}
        <Route index element={<Dashboard2 />} />

        {/* Old multi-page routes, kept temporarily for comparison during
            the redesign rollout — remove in a follow-up PR. */}
        <Route element={<Layout />}>
          <Route path='dashboard' element={<Dashboard />} />
          <Route path='explorer' element={<Explorer />} />
          <Route path='yield-curve' element={<YieldCurve />} />
          <Route path='chat' element={<Chat />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
