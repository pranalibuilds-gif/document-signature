import { cn } from "@/lib/utils"

interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "default" | "tight" | "full"
}

export function PageContainer({
  children,
  className,
  size = "default",
  ...props
}: PageContainerProps) {
  const sizes = {
    default: "max-w-7xl",
    tight: "max-w-4xl",
    full: "max-w-full px-6",
  }

  return (
    <div
      className={cn(
        "mx-auto w-full px-4 sm:px-6 lg:px-8 py-8",
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
