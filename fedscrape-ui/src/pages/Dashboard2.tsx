import { useState } from 'react'
import { MessageCircle } from 'lucide-react'
import { TopBar } from '@/components/layout/TopBar'
import { RateCardsRow } from '@/components/dashboard/RateCardsRow'
import { HistoricalTimeline } from '@/components/dashboard/HistoricalTimeline'
import { RateOfChange } from '@/components/dashboard/RateOfChange'
import { YieldCurveSnapshot } from '@/components/dashboard/YieldCurveSnapshot'
import { YieldCurveOverTime } from '@/components/dashboard/YieldCurveOverTime'
import { ChatPanel } from '@/components/dashboard/ChatPanel'
import { ChatModal } from '@/components/dashboard/ChatModal'
import { Button } from '@/components/ui/button'
import { useChatConversation } from '@/hooks/useChatConversation'

export function Dashboard2() {
  const conversation = useChatConversation()
  const [isChatOpen, setIsChatOpen] = useState(false)

  return (
    <div className='min-h-screen bg-[var(--bg-base)] pb-16 lg:pb-10 rounded-none'>
      <TopBar />

      <main className='mx-auto max-w-[1600px] px-4 py-6'>
        <RateCardsRow />

        {/* Main content: left column + right (chat) column */}
        <div className='mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[65%_1fr]'>
          <div className='flex flex-col gap-4'>
            <YieldCurveSnapshot />
            <HistoricalTimeline />
            <RateOfChange />
            <YieldCurveOverTime />
          </div>

          <div className='hidden lg:block'>
            <div className='sticky top-20 h-[calc(100vh-6rem)]'>
              <ChatPanel conversation={conversation} />
            </div>
          </div>
        </div>
      </main>

      <Button
        onClick={() => setIsChatOpen(true)}
        size='icon'
        aria-label='Open AI Rate Analyst chat'
        className='fixed bottom-6 right-6 z-50 size-14 rounded-full bg-[var(--accent-blue)] text-white shadow-lg hover:bg-[var(--accent-blue)]/80 lg:hidden'
      >
        <MessageCircle className='size-6' aria-hidden='true' />
      </Button>

      <ChatModal
        conversation={conversation}
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />

    </div>
  )
}
