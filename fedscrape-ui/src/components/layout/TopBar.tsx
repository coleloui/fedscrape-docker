import { format } from 'date-fns'

export function TopBar() {
  return (
    <header className='glass-panel sticky top-0 z-40 rounded-none border-x-0 border-t-0'>
      <div className='mx-auto flex max-w-[1600px] items-center gap-4 px-4 py-3'>
        <span className='font-mono text-sm font-semibold text-[var(--text-primary)]'>
          FedRate
        </span>

        <div className='flex items-center gap-2 text-xs text-[var(--text-secondary)]'>
          <span className='relative flex size-2'>
            <span className='absolute inline-flex size-full animate-ping rounded-full bg-[var(--accent-green)] opacity-75' />
            <span className='relative inline-flex size-2 rounded-full bg-[var(--accent-green)]' />
          </span>
          <span>Live</span>
          <span className='hidden sm:inline'>
            · {format(new Date(), 'MMM d, yyyy')}
          </span>
        </div>

        <a
          href='https://ko-fi.com/fedrate'
          target='_blank'
          rel='noopener noreferrer'
          className='ml-auto whitespace-nowrap rounded-md border border-white/10 px-3 py-1.5 text-sm text-[var(--text-secondary)] transition-colors duration-200 hover:border-[var(--accent-blue)] hover:text-[var(--text-primary)]'
        >
          ☕<span className='hidden sm:inline'> Support</span>
        </a>
      </div>
    </header>
  )
}
