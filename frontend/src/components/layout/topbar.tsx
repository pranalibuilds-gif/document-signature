"use client"

import { Bell, Search, UserCircle } from "lucide-react"

export function Topbar() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-8">
      <div className="flex w-96 items-center gap-2 rounded-lg bg-muted px-3 py-1.5">
        <Search className="h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search documents..."
          className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
        />
      </div>

      <div className="flex items-center gap-4">
        <button className="rounded-full p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">
          <Bell size={20} />
        </button>
        <div className="h-8 w-[1px] bg-border" />
        <button className="flex items-center gap-2 rounded-full py-1 pl-1 pr-3 transition-colors hover:bg-muted">
          <UserCircle size={28} className="text-muted-foreground" />
          <div className="text-left">
            <p className="text-xs font-semibold text-primary leading-tight">Admin User</p>
            <p className="text-[10px] text-muted-foreground leading-tight">admin@example.com</p>
          </div>
        </button>
      </div>
    </header>
  )
}
