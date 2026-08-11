import { useEffect, useRef } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ChatConversationBody } from './ChatPanel'
import type { ChatConversation } from '@/hooks/useChatConversation'

const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'

export function ChatModal({
  conversation,
  isOpen,
  onClose,
}: {
  conversation: ChatConversation
  isOpen: boolean
  onClose: () => void
}) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!isOpen) return

    document.body.style.overflow = 'hidden'
    closeButtonRef.current?.focus()

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onClose()
        return
      }
      if (e.key !== 'Tab' || !dialogRef.current) return

      const focusable = Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
      )
      if (focusable.length === 0) return

      const first = focusable[0]
      const last = focusable[focusable.length - 1]

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      ref={dialogRef}
      role='dialog'
      aria-modal='true'
      aria-labelledby='chat-modal-heading'
      className='fixed inset-0 z-50 flex flex-col bg-[var(--bg-base)] lg:hidden'
    >
      <div className='flex items-center justify-between border-b border-[var(--border-subtle)] px-4 py-3'>
        <div className='flex items-center gap-2'>
          <span
            aria-hidden='true'
            className='size-2 rounded-full bg-[var(--accent-amber)]'
          />
          <h2
            id='chat-modal-heading'
            className='text-sm font-medium text-[var(--text-primary)]'
          >
            AI Rate Analyst
          </h2>
        </div>
        <Button
          ref={closeButtonRef}
          variant='ghost'
          size='icon'
          onClick={onClose}
          aria-label='Close chat'
          className='text-[var(--text-secondary)] hover:bg-transparent hover:text-[var(--text-primary)]'
        >
          <X className='size-5' aria-hidden='true' />
        </Button>
      </div>
      <div className='flex-1 overflow-hidden'>
        <ChatConversationBody conversation={conversation} headingId='chat-modal-heading' />
      </div>
    </div>
  )
}
