import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function PriceChart({ data }) {
  if (!data || data.length === 0) return (
    <div className="h-full flex flex-col items-center justify-center text-xs text-muted-foreground border border-dashed rounded-lg bg-secondary/10">
        <span>No history data yet</span>
        <span className="opacity-50 text-[10px]">Check back later</span>
    </div>
  );

  // Format data for chart
  const chartData = data.map(d => ({
    rawDate: new Date(d.date),
    date: new Date(d.date).toLocaleDateString(undefined, {month:'short', day:'numeric'}),
    fullDate: new Date(d.date).toLocaleString(),
    price: d.price
  })).reverse(); // Recharts expects chronological order

  // Calculate domain padding to avoid misleading graphs
  const minPrice = Math.min(...chartData.map(d => d.price));
  const maxPrice = Math.max(...chartData.map(d => d.price));
  const padding = (maxPrice - minPrice) * 0.1; // 10% padding

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
          </linearGradient>
        </defs>
        
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.4} />
        
        <XAxis 
            dataKey="date" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
            minTickGap={30}
        />
        
        <YAxis 
            dataKey="price" 
            domain={[Math.floor(minPrice - padding), Math.ceil(maxPrice + padding)]} 
            axisLine={false} 
            tickLine={false} 
            allowDecimals={false}
            tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
            tickFormatter={(value) => `₹${Math.round(value).toLocaleString()}`}
        />

        <Tooltip 
            content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                return (
                    <div className="bg-popover border border-border shadow-xl rounded-lg p-3 text-xs">
                        <p className="text-muted-foreground mb-1">{payload[0].payload.fullDate}</p>
                        <p className="font-bold text-foreground text-sm">
                            ₹{payload[0].value.toLocaleString()}
                        </p>
                    </div>
                );
                }
                return null;
            }}
        />
        
        <Area 
            type="monotone" 
            dataKey="price" 
            stroke="hsl(var(--primary))" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorPrice)" 
            isAnimationActive={true}
            animationDuration={1500}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
