import { client } from './generated/client.gen'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://fed-scrape-api.up.railway.app'

client.setConfig({
  baseUrl: API_BASE_URL,
  throwOnError: true,
})

export { client }
