import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { Message } from '@/types/rates'

export function ChatMessage({
  message,
  toolCallsMade,
}: {
  message: Message
  toolCallsMade?: number
}) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-2.5 text-sm',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-card text-card-foreground',
        )}
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
        {!isUser && toolCallsMade != null && toolCallsMade > 0 && (
          <Badge variant='secondary' className='mt-2 text-xs font-normal'>
            Used {toolCallsMade} tool{toolCallsMade === 1 ? '' : 's'}
          </Badge>
        )}
      </div>
    </div>
  )
}
