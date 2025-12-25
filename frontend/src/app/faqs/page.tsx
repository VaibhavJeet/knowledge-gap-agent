'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { HelpCircle, Loader2, Check, ThumbsUp, ThumbsDown } from 'lucide-react'
import { api } from '@/lib/api'

export default function FAQsPage() {
  const queryClient = useQueryClient()
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data: faqs, isLoading } = useQuery({ queryKey: ['faqs'], queryFn: () => api.getFAQs() })

  const publishMutation = useMutation({
    mutationFn: (id: string) => api.publishFAQ(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['faqs'] }),
  })

  const generateMutation = useMutation({
    mutationFn: () => api.generateFAQs({ support_tickets: [], search_queries: [] }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['faqs'] }),
  })

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    pending_review: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-blue-100 text-blue-800',
    published: 'bg-green-100 text-green-800',
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">FAQs</h1>
        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {generateMutation.isPending ? <Loader2 className="animate-spin h-5 w-5" /> : <HelpCircle className="h-5 w-5" />}
          Generate FAQs
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="animate-spin h-8 w-8 text-gray-400" /></div>
      ) : faqs?.length === 0 ? (
        <div className="text-center py-12">
          <HelpCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">No FAQs yet. Generate FAQs from support data.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {faqs?.map((faq: any) => (
            <div key={faq.id} className="bg-white border rounded-lg overflow-hidden">
              <div
                className="p-4 cursor-pointer hover:bg-gray-50 flex justify-between items-start"
                onClick={() => setExpandedId(expandedId === faq.id ? null : faq.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 text-xs rounded ${statusColors[faq.status]}`}>{faq.status.replace('_', ' ')}</span>
                    <span className="text-sm text-gray-500">{faq.category}</span>
                  </div>
                  <h3 className="font-medium">{faq.question}</h3>
                </div>
                {faq.status === 'pending_review' && (
                  <button
                    onClick={(e) => { e.stopPropagation(); publishMutation.mutate(faq.id); }}
                    className="flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                  >
                    <Check className="h-4 w-4" /> Publish
                  </button>
                )}
              </div>
              {expandedId === faq.id && (
                <div className="p-4 bg-gray-50 border-t">
                  <p className="text-gray-700 whitespace-pre-wrap">{faq.answer}</p>
                  <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1"><ThumbsUp className="h-4 w-4" /> {faq.helpful_count}</span>
                    <span className="flex items-center gap-1"><ThumbsDown className="h-4 w-4" /> {faq.not_helpful_count}</span>
                    <span>Confidence: {(faq.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
