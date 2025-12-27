import { Crosshair } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="border-b bg-card/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Crosshair className="w-6 h-6 text-primary" />
          </div>
          <span className="font-bold text-xl tracking-tight">Price-Drop Sniper <span className="text-primary">Pro</span></span>
        </div>
        <div className="flex items-center gap-4">
             <div className="text-sm text-muted-foreground bg-secondary px-3 py-1 rounded-full">v2.0</div>
        </div>
      </div>
    </nav>
  )
}
