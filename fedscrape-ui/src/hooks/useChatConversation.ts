import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { chatChatPost } from '@/api/generated'
import type { Message } from '@/types/rates'

export interface ChatConversation {
  messages: Message[]
  toolCallsByIndex: Record<number, number>
  input: string
  setInput: (value: string) => void
  sendMessage: (content: string) => void
  isPending: boolean
}

export function useChatConversation(): ChatConversation {
  const [messages, setMessages] = useState<Message[]>([])
  const [toolCallsByIndex, setToolCallsByIndex] = useState<Record<number, number>>({})
  const [input, setInput] = useState('')

  const mutation = useMutation({
    mutationFn: async (nextMessages: Message[]) =>
      (await chatChatPost({ body: { messages: nextMessages } })).data,
  })

  function sendMessage(content: string) {
    if (!content.trim() || mutation.isPending) return
    const nextMessages: Message[] = [...messages, { role: 'user', content }]
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

  return {
    messages,
    toolCallsByIndex,
    input,
    setInput,
    sendMessage,
    isPending: mutation.isPending,
  }
}
