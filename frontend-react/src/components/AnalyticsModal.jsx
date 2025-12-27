import { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, TrendingDown, Minus, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts';

import { createPortal } from 'react-dom';

export default function AnalyticsModal({ isOpen, onClose, product, history, analysis }) {
  if (!isOpen) return null;
  if (typeof document === 'undefined') return null;

  /* Time Range State */
  const [timeRange, setTimeRange] = useState('30D');

  /* Filter Logic */
  const getFilteredData = () => {
      if (!history || history.length === 0) return [];
      const now = new Date();
      /* Sort history by date first to ensure correct slicing */
      const sorted = [...history].sort((a,b) => new Date(a.scraped_at) - new Date(b.scraped_at));
      
      let cutoffDate = new Date();
      if (timeRange === '7D') cutoffDate.setDate(now.getDate() - 7);
      if (timeRange === '30D') cutoffDate.setDate(now.getDate() - 30);
      if (timeRange === '3M') cutoffDate.setMonth(now.getMonth() - 3);
      if (timeRange === '1Y') cutoffDate.setFullYear(now.getFullYear() - 1);

      return sorted.filter(item => new Date(item.scraped_at) >= cutoffDate);
  };
   
  const filteredHistory = getFilteredData();


  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-popover border border-border p-4 rounded-xl shadow-xl">
          <p className="font-medium text-popover-foreground mb-2">{label}</p>
          <div className="flex items-center gap-2 text-sm">
             <div className="w-2 h-2 rounded-full bg-primary" />
             <span className="text-muted-foreground">Price:</span>
             <span className="font-bold text-foreground">₹{payload[0].value.toLocaleString()}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return createPortal(
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-6"
        onClick={onClose}
      >
        <motion.div 
          initial={{ scale: 0.95, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-[#09090b] border border-white/10 rounded-3xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl relative overflow-hidden ring-1 ring-white/10"
        >
          {/* Header */}
          <div className="flex-none bg-[#09090b] p-6 border-b border-white/10 flex justify-between items-start z-10">
            <div>
                 <h2 className="text-xl md:text-2xl font-bold leading-tight pr-8 text-white">{product.name}</h2>
                 <p className="text-zinc-400 text-sm mt-1 font-mono">ID: {product.id} • Platform: <span className="uppercase">{product.platform}</span></p>
            </div>
            <button 
                onClick={onClose}
                className="p-2 hover:bg-white/10 rounded-full transition-colors text-white"
            >
                <X className="w-6 h-6" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="p-6 md:p-8 space-y-8">
             
             {/* Key Metrics Grid */}
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard 
                    label="Current Price" 
                    value={`₹${product.current_price.toLocaleString()}`} 
                    subtext="Just now"
                    icon={TrendingUp} // Placeholder
                    trend="neutral"
                />
                <MetricCard 
                    label="Lowest (30 Days)" 
                    value={`₹${analysis?.min_price_30_day?.toLocaleString() || '-'}`} 
                    subtext={analysis?.min_price_30_day ? `${Math.round(((product.current_price - analysis.min_price_30_day)/analysis.min_price_30_day)*100)}% from low` : ''}
                    icon={TrendingDown}
                    trend="down"
                    color="text-green-500"
                />
                <MetricCard 
                    label="Highest (30 Days)" 
                    value={`₹${analysis?.max_price_30_day?.toLocaleString() || '-'}`} 
                    subtext="Peak price"
                    icon={TrendingUp}
                    trend="up"
                    color="text-red-500"
                />
             </div>

             {/* Main Chart Section */}
             <div className="bg-white/5 rounded-3xl p-6 border border-white/10">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-bold flex items-center gap-2 text-white">
                        <Calendar className="w-5 h-5 text-primary" />
                        Price History Trend
                    </h3>
                    <div className="flex gap-2">
                         {['7D', '30D', '3M', '1Y'].map(t => (
                             <button 
                                key={t} 
                                onClick={() => setTimeRange(t)}
                                className={`px-3 py-1 text-xs rounded-full font-medium transition-colors ${timeRange === t ? 'bg-primary text-primary-foreground' : 'bg-white/10 hover:bg-white/20 text-white'}`}
                             >
                                {t}
                             </button>
                         ))}
                    </div>
                </div>
                
                <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={filteredHistory}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                            <XAxis 
                                dataKey="scraped_at" 
                                tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, {month:'short', day:'numeric'})}
                                stroke="#9ca3af"
                                fontSize={12}
                                tickMargin={10}
                            />
                            <YAxis 
                                stroke="#9ca3af"
                                fontSize={12}
                                tickFormatter={(val) => `₹${val/1000}k`}
                                domain={['auto', 'auto']} /* Auto scale Y-axis */
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area 
                                type="monotone" 
                                dataKey="price" 
                                stroke="#8b5cf6" 
                                strokeWidth={3}
                                fillOpacity={0.2} 
                                fill="#8b5cf6" 
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
             </div>

             {/* Recommendation Banner */}
             <div className={`rounded-xl p-4 border border-l-4 ${analysis?.is_fake_sale ? 'bg-red-500/10 border-red-500' : 'bg-green-500/10 border-green-500'} flex items-start gap-4`}>
                 <div className={`p-2 rounded-full ${analysis?.is_fake_sale ? 'bg-red-500/20 text-red-500' : 'bg-green-500/20 text-green-500'}`}>
                    {analysis?.is_fake_sale ? <X className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />}
                 </div>
                 <div>
                    <h4 className={`font-bold text-lg ${analysis?.is_fake_sale ? 'text-red-500' : 'text-green-500'}`}>
                        {analysis?.recommendation || 'Analysis Unavailable'}
                    </h4>
                    <p className="text-zinc-400 text-sm mt-1">
                        {analysis?.is_fake_sale 
                            ? "This appears to be a Fake Sale! The price was raised recently just to show a discount." 
                            : "This is a great time to buy! Prices are historically low."}
                    </p>
                 </div>
             </div>

            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  );
}

function MetricCard({ label, value, subtext, icon: Icon, color = "text-primary" }) {
    return (
        <div className="bg-secondary/20 p-5 rounded-2xl border border-border/50">
            <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-medium text-muted-foreground">{label}</span>
                <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div className="text-2xl font-bold tracking-tight">{value}</div>
            <p className="text-xs text-muted-foreground mt-1">{subtext}</p>
        </div>
    )
}
