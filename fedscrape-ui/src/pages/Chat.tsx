import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { DisclaimerBanner } from '@/components/chat/DisclaimerBanner'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { chatChatPost } from '@/api/generated'
import type { Message } from '@/types/rates'

const WELCOME_MESSAGE: Message = {
  role: 'assistant',
  content:
    'Welcome to FedScrape. I can answer questions about Federal Reserve ' +
    'H.15 interest rate data including current rates, historical trends, ' +
    'yield curve analysis, and rate comparisons. Please note: all ' +
    'information is for educational purposes only and does not constitute ' +
    'financial advice. Use any information at your own risk.',
}

const STARTER_PROMPTS = [
  'What is the current Federal Funds rate?',
  'Is the yield curve currently inverted?',
  'How have 10-year Treasury yields trended over the past year?',
  'What was the average Fed Funds rate in 2024?',
]

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE])
  const [toolCallsByIndex, setToolCallsByIndex] = useState<
    Record<number, number>
  >({})
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const mutation = useMutation({
    mutationFn: async (nextMessages: Message[]) =>
      (await chatChatPost({ body: { messages: nextMessages } })).data,
  })

  function sendMessage(content: string) {
    if (!content.trim() || mutation.isPending) return
    const nextMessages: Message[] = [
      ...messages,
      { role: 'user', content },
    ]
    setMessages(nextMessages)
    setInput('')

    mutation.mutate(nextMessages, {
      onSuccess: response => {
        if (!response) return
        setMessages(current => {
          const updated: Message[] = [
            ...current,
            { role: 'assistant', content: response.message },
          ]
          setToolCallsByIndex(prev => ({
            ...prev,
            [updated.length - 1]: response.tool_calls_made,
          }))
          return updated
        })
      },
      onError: () => {
        setMessages(current => [
          ...current,
          {
            role: 'assistant',
            content:
              'Sorry, something went wrong reaching the chat service. Please try again.',
          },
        ])
      },
    })
  }

  const hasUserMessages = messages.some(m => m.role === 'user')

  return (
    <div className='flex h-[calc(100vh-8.5rem)] flex-col gap-4'>
      <DisclaimerBanner />

      <Card className='flex flex-1 flex-col overflow-hidden border-border bg-card p-0'>
        <div className='flex-1 space-y-3 overflow-y-auto p-4'>
          {messages.map((message, i) => (
            <ChatMessage
              key={i}
              message={message}
              toolCallsMade={toolCallsByIndex[i]}
            />
          ))}
          {mutation.isPending && (
            <div className='flex justify-start'>
              <div className='rounded-lg bg-card px-4 py-2.5 text-sm text-muted-foreground'>
                Thinking…
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>

        {!hasUserMessages && (
          <div className='flex flex-wrap gap-2 border-t border-border p-4'>
            {STARTER_PROMPTS.map(prompt => (
              <Button
                key={prompt}
                variant='outline'
                size='sm'
                className='text-xs'
                onClick={() => sendMessage(prompt)}
              >
                {prompt}
              </Button>
            ))}
          </div>
        )}

        <form
          className='flex gap-2 border-t border-border p-4'
          onSubmit={e => {
            e.preventDefault()
            sendMessage(input)
          }}
        >
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder='Ask about Fed rate data…'
            disabled={mutation.isPending}
          />
          <Button type='submit' disabled={mutation.isPending || !input.trim()}>
            <Send className='size-4' />
          </Button>
        </form>
      </Card>
    </div>
  )
}
