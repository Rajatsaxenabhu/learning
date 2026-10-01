import { GeoLoader } from '@/components/layout/GeoLoader'
import { gradientBg } from '@/features/chat/constants'
import { cn } from '@/lib/utils'

export default function Loading() {
  return (
    <div className={cn('grid h-svh place-items-center', gradientBg)}>
      <GeoLoader />
    </div>
  )
}
