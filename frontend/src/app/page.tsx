export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 text-center">
      <header className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight text-primary sm:text-6xl">
          DocuSign <span className="text-accent">Mini</span>
        </h1>
        <p className="mt-6 text-lg leading-8 text-muted-foreground max-w-2xl">
          The simple, secure, and professional way to sign and manage your documents.
          Built for reliability. Designed for clarity.
        </p>
      </header>

      <div className="flex gap-4">
        <a href="/login" className="btn-primary px-8 py-3 text-base">
          Sign In
        </a>
        <a href="/register" className="btn-accent px-8 py-3 text-base">
          Get Started
        </a>
      </div>

      <footer className="mt-16 text-sm text-muted-foreground">
        © 2024 DocuSign Mini. All rights reserved.
      </footer>
    </div>
  );
}
