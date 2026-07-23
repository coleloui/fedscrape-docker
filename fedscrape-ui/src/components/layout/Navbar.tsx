import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/explorer', label: 'Explorer' },
  { to: '/yield-curve', label: 'Yield Curve' },
  { to: '/chat', label: 'Chat' },
]

export function Navbar() {
  return (
    <header className='border-b border-border bg-background'>
      <div className='mx-auto flex max-w-6xl items-center gap-6 px-4 py-3'>
        <span className='font-mono text-sm font-semibold text-foreground'>
          FedScrape
        </span>
        <nav className='flex gap-1'>
          {links.map(link => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) =>
                cn(
                  'rounded-md px-3 py-1.5 text-sm transition-colors',
                  isActive
                    ? 'bg-card text-primary'
                    : 'text-muted-foreground hover:bg-card hover:text-foreground',
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
