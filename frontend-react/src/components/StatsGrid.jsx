import { TrendingUp, ShoppingBag, CheckCircle } from 'lucide-react';

export default function StatsGrid({ products }) {
  const trackedCount = products.length;
  const inStockCount = products.filter(p => p.is_available).length;
  const totalValue = products.reduce((acc, p) => acc + (p.current_price || 0), 0);

  const stats = [
    { label: "Tracked Items", value: trackedCount, icon: ShoppingBag, color: "text-blue-500", bg: "bg-blue-500/10" },
    { label: "Total Value", value: `₹${totalValue.toLocaleString()}`, icon: TrendingUp, color: "text-green-500", bg: "bg-green-500/10" },
    { label: "In Stock", value: inStockCount, icon: CheckCircle, color: "text-orange-500", bg: "bg-orange-500/10" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      {stats.map((stat, idx) => (
        <div 
          key={idx} 
          className="relative overflow-hidden bg-card/40 backdrop-blur-xl border border-white/5 rounded-3xl p-6 hover:bg-card/60 transition-all duration-500 group"
        >
          {/* Background Glow */}
          <div className={`absolute -right-10 -top-10 w-32 h-32 rounded-full blur-3xl opacity-20 ${stat.bg.replace('/10', '')}`} />
          
          <div className="relative z-10 flex flex-col justify-between h-full space-y-4">
             <div className="flex items-center justify-between">
                <div className={`p-3 rounded-2xl ${stat.bg} ring-1 ring-white/10`}>
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                {/* Micro Chart Placeholder or Decorator */}
                <div className="flex space-x-1">
                    {[1,2,3].map(i => (
                        <div key={i} className={`w-1 rounded-full bg-current opacity-20 ${stat.color}`} style={{ height: `${Math.random() * 12 + 4}px` }} />
                    ))}
                </div>
             </div>
             <div>
                <h3 className="text-4xl font-bold tracking-tight text-foreground">{stat.value}</h3>
                <p className="text-muted-foreground text-sm font-medium mt-1 opacity-80">{stat.label}</p>
             </div>
          </div>
        </div>
      ))}
    </div>
  )
}
