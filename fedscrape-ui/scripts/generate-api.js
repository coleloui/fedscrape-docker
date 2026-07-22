#!/usr/bin/env node

import { createClient } from '@hey-api/openapi-ts'

const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000'
const input = `${API_BASE_URL}/openapi.json`
const output = 'src/api/generated'

console.log(`Generating API client from ${input}...`)

try {
  await createClient({
    input,
    output,
    plugins: [
      { name: '@hey-api/client-fetch', throwOnError: true },
      { name: '@hey-api/typescript' },
      { name: '@hey-api/sdk', throwOnError: true },
    ],
  })
  console.log(`Generated API client at ${output}`)
} catch (error) {
  console.error(`Failed to generate API client: ${error.message}`)
  console.error(`Make sure the backend is running and reachable at: ${API_BASE_URL}`)
  process.exit(1)
}
