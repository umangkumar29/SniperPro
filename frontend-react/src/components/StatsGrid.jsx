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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {stats.map((stat, idx) => (
        <div key={idx} className="bg-card border rounded-2xl p-6 flex items-center justify-between shadow-sm hover:shadow-md transition-shadow">
          <div>
            <p className="text-muted-foreground text-sm font-medium">{stat.label}</p>
            <h3 className="text-2xl font-bold mt-1">{stat.value}</h3>
          </div>
          <div className={`p-3 rounded-xl ${stat.bg}`}>
            <stat.icon className={`w-6 h-6 ${stat.color}`} />
          </div>
        </div>
      ))}
    </div>
  )
}
