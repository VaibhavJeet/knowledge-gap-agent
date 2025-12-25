'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, AlertTriangle, HelpCircle, FileText, BarChart3, Settings } from 'lucide-react'

const nav = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Gaps', href: '/gaps', icon: AlertTriangle },
  { name: 'FAQs', href: '/faqs', icon: HelpCircle },
  { name: 'Content', href: '/content', icon: FileText },
  { name: 'Analysis', href: '/analysis', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white border-r flex flex-col">
      <div className="p-6 border-b">
        <h1 className="text-xl font-bold">Knowledge Gap</h1>
        <p className="text-sm text-gray-500">AI-powered analysis</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {nav.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              pathname === item.href
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  )
}
