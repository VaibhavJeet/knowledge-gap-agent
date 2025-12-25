'use client'

import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, HelpCircle, FileText, TrendingUp } from 'lucide-react'
import { api } from '@/lib/api'
import Link from 'next/link'

export default function DashboardPage() {
  const { data: gaps } = useQuery({ queryKey: ['gaps'], queryFn: () => api.getGaps() })
  const { data: faqs } = useQuery({ queryKey: ['faqs'], queryFn: () => api.getFAQs() })
  const { data: reports } = useQuery({ queryKey: ['reports'], queryFn: () => api.getReports() })

  const criticalGaps = gaps?.filter((g: any) => g.priority === 'critical') || []
  const pendingFAQs = faqs?.filter((f: any) => f.status === 'pending_review') || []

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Knowledge Gap Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Gaps" value={gaps?.length || 0} icon={<AlertTriangle />} color="bg-orange-500" />
        <StatCard title="Critical Gaps" value={criticalGaps.length} icon={<AlertTriangle />} color="bg-red-500" />
        <StatCard title="FAQs Generated" value={faqs?.length || 0} icon={<HelpCircle />} color="bg-blue-500" />
        <StatCard title="Pending Review" value={pendingFAQs.length} icon={<FileText />} color="bg-yellow-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex justify-between mb-4">
            <h2 className="text-xl font-semibold">Critical Gaps</h2>
            <Link href="/gaps" className="text-blue-600 hover:underline">View all</Link>
          </div>
          {criticalGaps.length === 0 ? (
            <p className="text-gray-500">No critical gaps</p>
          ) : (
            <div className="space-y-3">
              {criticalGaps.slice(0, 5).map((gap: any) => (
                <div key={gap.id} className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
                  <p className="font-medium">{gap.title}</p>
                  <p className="text-sm text-gray-600">{gap.topic}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex justify-between mb-4">
            <h2 className="text-xl font-semibold">FAQs Pending Review</h2>
            <Link href="/faqs" className="text-blue-600 hover:underline">View all</Link>
          </div>
          {pendingFAQs.length === 0 ? (
            <p className="text-gray-500">No FAQs pending review</p>
          ) : (
            <div className="space-y-3">
              {pendingFAQs.slice(0, 5).map((faq: any) => (
                <div key={faq.id} className="p-3 bg-yellow-50 rounded border">
                  <p className="font-medium">{faq.question}</p>
                  <p className="text-sm text-gray-600">{faq.category}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }: { title: string; value: number; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center gap-4">
        <div className={`${color} text-white p-3 rounded-lg`}>{icon}</div>
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  )
}
