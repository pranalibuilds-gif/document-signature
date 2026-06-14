"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { PenTool, Loader2 } from "lucide-react"
import api from "@/lib/api"
import { cn } from "@/lib/utils"

export default function RegisterPage() {
  const [regRole, setRegRole] = useState<"USER" | "ADMIN">("USER")
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
  })
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await api.post("/auth/register", { ...formData, role: regRole })
      router.push("/login?registered=true")
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail[0]?.msg || "Invalid data provided.")
      } else if (typeof detail === "string") {
        setError(detail)
      } else {
        setError("Registration failed. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.id]: e.target.value }))
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md space-y-8">
        <div className="flex flex-col items-center text-center">
          <div className="rounded-xl bg-accent p-3 text-accent-foreground mb-4">
            <PenTool size={32} />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Get started</h1>
          <p className="text-muted-foreground mt-2">Create your account to start signing documents</p>
        </div>

        <Card className="border-border/50 shadow-lg overflow-hidden">
          <div className="flex border-b">
            <button
              type="button"
              onClick={() => setRegRole("USER")}
              className={cn(
                "flex-1 py-3 text-[10px] font-bold uppercase tracking-wider transition-colors",
                regRole === "USER" ? "bg-accent/5 text-accent border-b-2 border-accent" : "text-muted-foreground hover:bg-stone-50"
              )}
            >
              Signer Account
            </button>
            <button
              type="button"
              onClick={() => setRegRole("ADMIN")}
              className={cn(
                "flex-1 py-3 text-[10px] font-bold uppercase tracking-wider transition-colors",
                regRole === "ADMIN" ? "bg-primary/5 text-primary border-b-2 border-primary" : "text-muted-foreground hover:bg-stone-50"
              )}
            >
              Admin Account
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <CardHeader className="space-y-1">
              <CardTitle className="text-xl">Create Account</CardTitle>
              <CardDescription>
                Enter your details to register as a {regRole === "ADMIN" ? "system admin" : "document signer"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    placeholder="John"
                    required
                    value={formData.first_name}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    placeholder="Doe"
                    required
                    value={formData.last_name}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  disabled={isLoading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full h-11 btn-accent" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Account
              </Button>
              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link href="/login" className="text-accent hover:underline font-medium">
                  Sign in
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  )
}
