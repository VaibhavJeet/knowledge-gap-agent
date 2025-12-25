'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, Search, Play, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'

export default function GapsPage() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState('')

  const { data: gaps, isLoading } = useQuery({ queryKey: ['gaps'], queryFn: () => api.getGaps() })

  const analyzeMutation = useMutation({
    mutationFn: (data: { search_queries: any[]; support_tickets: any[] }) => api.analyzeGaps(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['gaps'] }),
  })

  const filteredGaps = gaps?.filter((g: any) =>
    g.title.toLowerCase().includes(filter.toLowerCase()) ||
    g.topic.toLowerCase().includes(filter.toLowerCase())
  ) || []

  const priorityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Knowledge Gaps</h1>
        <button
          onClick={() => analyzeMutation.mutate({ search_queries: [], support_tickets: [] })}
          disabled={analyzeMutation.isPending}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {analyzeMutation.isPending ? <Loader2 className="animate-spin h-5 w-5" /> : <Play className="h-5 w-5" />}
          Run Analysis
        </button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Filter gaps..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg"
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="animate-spin h-8 w-8 text-gray-400" /></div>
      ) : filteredGaps.length === 0 ? (
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">No gaps found. Run analysis to detect gaps.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredGaps.map((gap: any) => (
            <div key={gap.id} className="bg-white border rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 text-xs rounded border ${priorityColors[gap.priority]}`}>
                      {gap.priority}
                    </span>
                    <span className="text-sm text-gray-500">{gap.topic}</span>
                  </div>
                  <h3 className="text-lg font-semibold">{gap.title}</h3>
                  <p className="text-gray-600 mt-1">{gap.description}</p>
                  {gap.impact_score > 0 && (
                    <p className="text-sm text-gray-500 mt-2">Impact Score: {(gap.impact_score * 100).toFixed(0)}%</p>
                  )}
                </div>
                <span className={`px-3 py-1 text-sm rounded-full ${gap.status === 'resolved' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {gap.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
