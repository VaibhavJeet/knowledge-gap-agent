import axios from 'axios'

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
})

export const api = {
  // Gaps
  getGaps: async () => (await client.get('/gaps')).data,
  getGap: async (id: string) => (await client.get(`/gaps/${id}`)).data,
  analyzeGaps: async (data: any) => (await client.post('/gaps/analyze', data)).data,
  updateGapStatus: async (id: string, status: string) => (await client.put(`/gaps/${id}/status?status=${status}`)).data,

  // FAQs
  getFAQs: async () => (await client.get('/faqs')).data,
  getFAQ: async (id: string) => (await client.get(`/faqs/${id}`)).data,
  generateFAQs: async (data: any) => (await client.post('/faqs/generate', data)).data,
  publishFAQ: async (id: string) => (await client.post(`/faqs/${id}/publish`)).data,
  faqFeedback: async (id: string, helpful: boolean) => (await client.post(`/faqs/${id}/feedback?helpful=${helpful}`)).data,

  // Content
  getContent: async () => (await client.get('/content')).data,
  getCoverage: async () => (await client.get('/content/coverage')).data,
  getSuggestions: async (data: any) => (await client.post('/content/suggestions', null, { params: data })).data,

  // Analysis
  runAnalysis: async (data: any) => (await client.post('/analysis/run', data)).data,
  getReports: async () => (await client.get('/analysis/reports')).data,
  getReport: async (id: string) => (await client.get(`/analysis/reports/${id}`)).data,
}
