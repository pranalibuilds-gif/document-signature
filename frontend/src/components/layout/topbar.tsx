"use client"

import { Bell, Search, UserCircle, Menu } from "lucide-react"
import { useAuthStore } from "@/store/use-auth-store"

export function Topbar({ onMenuClick }: { onMenuClick?: () => void }) {
  const { user } = useAuthStore()

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-4 md:px-8 shrink-0">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 -ml-2 text-muted-foreground hover:text-foreground"
        >
          <Menu size={24} />
        </button>

        <div className="hidden sm:flex w-64 lg:w-96 items-center gap-2 rounded-lg bg-muted px-3 py-1.5">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-4">
        <button className="rounded-full p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">
          <Bell size={20} />
        </button>
        <div className="h-8 w-[1px] bg-border" />
        <button className="flex items-center gap-2 rounded-full py-1 pl-1 pr-1 md:pr-3 transition-colors hover:bg-muted min-w-0">
          <UserCircle size={28} className="text-muted-foreground shrink-0" />
          <div className="text-left hidden xs:block">
            <p className="text-xs font-semibold text-primary leading-tight truncate max-w-[100px]">
              {user?.first_name || "User"}
            </p>
            <p className="text-[10px] text-muted-foreground leading-tight truncate max-w-[100px]">
              {user?.email || "Account"}
            </p>
          </div>
        </button>
      </div>
    </header>
  )
}
