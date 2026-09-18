import { ArrowLeft } from 'lucide-react'
import { Link } from 'react-router'
import { Button } from '@/components/ui/button'

export default function AppPage() {
  return (
    <div className="dark flex min-h-svh flex-col items-center justify-center gap-4 bg-background text-foreground">
      <h1 className="text-2xl font-semibold">Workspace coming soon</h1>
      <p className="text-muted-foreground">The chat and map view will live here.</p>
      <Button variant="outline" render={<Link to="/" />}>
        <ArrowLeft /> Back home
      </Button>
    </div>
  )
}
