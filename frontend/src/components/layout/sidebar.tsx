"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  FileText,
  Settings,
  ShieldCheck,
  Users,
  LogOut,
  PenTool,
  X,
  History
} from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Signers", href: "/signers", icon: Users },
  { name: "Settings", href: "/settings", icon: Settings },
]

const adminNavigation = [
  { name: "Admin Overview", href: "/admin", icon: ShieldCheck, exact: true },
  { name: "User Management", href: "/admin/users", icon: Users },
  { name: "Audit Trail", href: "/admin/audit", icon: History },
]

export function Sidebar({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-full flex-col border-r bg-card relative">
      <div className="flex h-16 items-center justify-between px-6 shrink-0">
        <Link href="/" className="flex items-center gap-2">
          <div className="rounded-lg bg-accent p-1.5 text-accent-foreground">
            <PenTool size={20} />
          </div>
          <span className="text-xl font-bold tracking-tight text-primary">
            DocuSign <span className="text-accent">Mini</span>
          </span>
        </Link>
        <button
          onClick={onClose}
          className="lg:hidden p-2 -mr-2 text-muted-foreground hover:text-foreground"
        >
          <X size={20} />
        </button>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href))
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={onClose}
              className={cn(
                "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent/10 text-accent"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive ? "text-accent" : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              {item.name}
            </Link>
          )
        })}

        <div className="pt-6 pb-2">
          <p className="px-3 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/40">
            System Administration
          </p>
        </div>

        {adminNavigation.map((item) => {
          const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href)
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={onClose}
              className={cn(
                "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent/10 text-accent"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive ? "text-accent" : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="border-t p-4">
        <button className="flex w-full items-center rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-destructive/5 hover:text-destructive">
          <LogOut className="mr-3 h-5 w-5 flex-shrink-0" />
          Sign Out
        </button>
      </div>
    </div>
  )
}
