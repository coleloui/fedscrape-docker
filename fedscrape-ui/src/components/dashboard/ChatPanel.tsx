import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import type { ChatConversation } from '@/hooks/useChatConversation'

const STARTER_PROMPTS = [
  'What is the current Federal Funds rate?',
  'Is the yield curve currently inverted?',
  'How have 10Y yields trended this year?',
  'What was the average Fed Funds rate in 2024?',
]

function TypingIndicator() {
  return (
    <div role='status' className='flex justify-start'>
      <span className='sr-only'>AI Rate Analyst is typing a response</span>
      <div
        aria-hidden='true'
        className='flex items-center gap-1 rounded-lg bg-[var(--chat-assistant-bubble)] px-4 py-3'
      >
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className='size-1.5 animate-pulse rounded-full bg-[var(--text-secondary)]'
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  )
}

export function ChatConversationBody({
  conversation,
  headingId,
}: {
  conversation: ChatConversation
  headingId: string
}) {
  const { messages, toolCallsByIndex, input, setInput, sendMessage, isPending } =
    conversation
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isPending])

  return (
    <div className='flex min-h-0 flex-1 flex-col'>
      <p className='px-4 pt-3 text-xs italic text-[var(--accent-amber)] opacity-70'>
        For informational purposes only. Not financial advice. Use any
        information at your own risk.
      </p>

      <div
        role='log'
        aria-label='Chat conversation'
        aria-live='polite'
        className='flex-1 space-y-3 overflow-y-auto p-4'
      >
        {messages.length === 0 && (
          <div className='flex flex-col gap-2'>
            <p className='text-xs text-[var(--text-secondary)]'>Try asking:</p>
            {STARTER_PROMPTS.map(prompt => (
              <Button
                key={prompt}
                variant='outline'
                onClick={() => sendMessage(prompt)}
                className='h-auto justify-start whitespace-normal border-[var(--border-subtle)] bg-transparent px-3 py-2 text-left text-xs font-normal text-[var(--text-secondary)] hover:border-[var(--accent-amber)] hover:bg-transparent hover:text-[var(--text-primary)]'
              >
                {prompt}
              </Button>
            ))}
          </div>
        )}

        {messages.map((message, i) => {
          const isUser = message.role === 'user'
          const toolCalls = toolCallsByIndex[i]
          return (
            <div key={i} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-sm rounded-lg px-4 py-2.5 text-sm ${
                  isUser
                    ? 'bg-[var(--chat-user-bubble)] text-white'
                    : 'bg-[var(--chat-assistant-bubble)] text-[var(--text-primary)]'
                }`}
              >
                {isUser ? (
                  <p className='whitespace-pre-wrap'>{message.content}</p>
                ) : (
                  <div className='prose prose-sm prose-invert max-w-none prose-p:my-2 prose-headings:my-3 prose-table:my-2'>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                )}
                {!isUser && toolCalls != null && toolCalls > 0 && (
                  <Badge
                    variant='secondary'
                    className='mt-2 bg-[var(--text-muted)] text-[10px] font-normal text-[var(--text-primary)]'
                  >
                    Used {toolCalls} tool{toolCalls === 1 ? '' : 's'}
                  </Badge>
                )}
              </div>
            </div>
          )
        })}

        {isPending && <TypingIndicator />}
        <div ref={scrollRef} />
      </div>

      <form
        className='flex gap-2 border-t border-[var(--border-subtle)] p-3'
        onSubmit={e => {
          e.preventDefault()
          sendMessage(input)
        }}
      >
        <label htmlFor={`${headingId}-input`} className='sr-only'>
          Ask about Fed rate data
        </label>
        <Input
          id={`${headingId}-input`}
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder='Ask about Fed rate data…'
          disabled={isPending}
          className='h-9 flex-1 border-[var(--border-subtle)] bg-[var(--bg-surface)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus-visible:border-[var(--accent-amber)] focus-visible:ring-[var(--accent-amber)]/50'
        />
        <Button
          type='submit'
          size='icon'
          disabled={isPending || !input.trim()}
          aria-label='Send message'
          className='size-9 shrink-0 bg-[var(--accent-amber)] text-black hover:bg-[var(--accent-amber)]/80'
        >
          <Send className='size-4' aria-hidden='true' />
        </Button>
      </form>
    </div>
  )
}

export function ChatPanel({ conversation }: { conversation: ChatConversation }) {
  return (
    <section
      aria-labelledby='chat-heading'
      className='glass-panel flex h-full flex-col overflow-hidden'
    >
      <div className='flex items-center gap-2 border-b border-[var(--border-subtle)] px-4 py-3'>
        <span
          aria-hidden='true'
          className='size-2 rounded-full bg-[var(--accent-amber)]'
        />
        <h2 id='chat-heading' className='text-sm font-medium text-[var(--text-primary)]'>
          AI Rate Analyst
        </h2>
      </div>
      <ChatConversationBody conversation={conversation} headingId='chat-heading' />
    </section>
  )
}
