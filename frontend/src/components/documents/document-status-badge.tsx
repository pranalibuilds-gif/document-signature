import { Badge } from "@/components/ui/badge"

type DocumentStatus = "DRAFT" | "PENDING" | "PARTIALLY_SIGNED" | "COMPLETED" | "REJECTED" | "EXPIRED" | "CANCELED"

export function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  switch (status) {
    case "DRAFT":
      return <Badge variant="secondary">Draft</Badge>
    case "PENDING":
      return <Badge variant="accent">Pending</Badge>
    case "PARTIALLY_SIGNED":
      return <Badge variant="accent">Partially Signed</Badge>
    case "COMPLETED":
      return <Badge variant="success">Completed</Badge>
    case "REJECTED":
      return <Badge variant="destructive">Rejected</Badge>
    case "EXPIRED":
      return <Badge variant="outline" className="opacity-60">Expired</Badge>
    case "CANCELED":
      return <Badge variant="outline" className="opacity-60">Canceled</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}
