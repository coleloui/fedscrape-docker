import { TopBar } from '@/components/layout/TopBar'
import { RateCardsRow } from '@/components/dashboard/RateCardsRow'
import { RateTicker } from '@/components/dashboard/RateTicker'
import { HistoricalTimeline } from '@/components/dashboard/HistoricalTimeline'
import { RateOfChange } from '@/components/dashboard/RateOfChange'

function Placeholder({ title, className = '' }: { title: string; className?: string }) {
  return (
    <div className={`glass-panel flex min-h-40 items-center justify-center p-4 ${className}`}>
      <span className='text-sm text-[var(--text-muted)]'>{title}</span>
    </div>
  )
}

export function Dashboard2() {
  return (
    <div className='min-h-screen bg-[var(--bg-base)] pb-16 lg:pb-10'>
      <TopBar />

      <main className='mx-auto max-w-[1600px] px-4 py-6'>
        <RateCardsRow />

        {/* Main content: left column + right (chat) column */}
        <div className='mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[65%_1fr]'>
          <div className='flex flex-col gap-4'>
            <Placeholder title='Yield Curve Snapshot' />
            <HistoricalTimeline />
            <RateOfChange />
            <Placeholder title='Yield Curve Over Time' />
          </div>

          <div className='hidden lg:block'>
            <Placeholder title='AI Chat Panel' className='sticky top-20 min-h-[calc(100vh-6rem)]' />
          </div>
        </div>
      </main>

      {/* Mobile floating chat button */}
      <button
        className='fixed bottom-6 right-6 z-50 flex size-14 items-center justify-center rounded-full bg-[var(--accent-blue)] text-white shadow-lg lg:hidden'
        aria-label='Open AI Rate Analyst chat'
      >
        💬
      </button>

      <RateTicker />
    </div>
  )
}
