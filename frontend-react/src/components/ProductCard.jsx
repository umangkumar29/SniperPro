import { useState, useEffect } from 'react';
import { ExternalLink, RefreshCw, Bell, BellRing, Trash2, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { getPriceHistory, getAnalysis, refreshProduct, setAlert } from '../services/api';
import AnalyticsModal from './AnalyticsModal';
import { BarChart3 } from 'lucide-react';

export default function ProductCard({ product, onDelete }) {
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Alert State
  const [targetPrice, setTargetPrice] = useState(Math.round(product.current_price * 0.95));
  const [alertOpen, setAlertOpen] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  useEffect(() => {
    loadData();
  }, [product.id]);

  const loadData = async () => {
    try {
      const histData = await getPriceHistory(product.id);
      setHistory(histData.data);
      const analysisData = await getAnalysis(product.id);
      setAnalysis(analysisData.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshProduct(product.id);
      // Wait a bit or poll? For now just reload data after 2s
      setTimeout(loadData, 2000);
    } catch (e) { console.error(e) }
    setRefreshing(false);
  };
  
  const handleSetAlert = async () => {
      try {
          await setAlert({
              product_id: product.id,
              target_price: parseFloat(targetPrice),
              contact_method: 'telegram',
              contact_value: 'default'
          });
          alert(`✅ Alert set for ₹${targetPrice}`);
          setAlertOpen(false);
      } catch(e) {
          alert('Failed to set alert');
      }
  };

  // Logic for MRP and Discount display
  const effectiveMax = analysis?.highest_price && analysis.highest_price > product.current_price 
                        ? analysis.highest_price 
                        : product.current_price * 1.25;
  const discount = Math.round(((effectiveMax - product.current_price) / effectiveMax) * 100);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      layout
      className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-3xl overflow-hidden hover:border-primary/20 transition-all duration-300 group"
    >
      <div className="flex flex-col md:flex-row">
        
        {/* COL 1: Image & Platform (Left) */}
        <div className="w-full md:w-1/3 xl:w-1/4 bg-white p-6 flex flex-col items-center justify-center relative min-h-[220px]">
            {/* Discount Badge */}
            {discount > 5 && (
                <div className="absolute top-3 left-3 bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow-sm z-10">
                    -{discount}%
                </div>
            )}
            
            {/* Image */}
            <div className="relative w-full aspect-square flex items-center justify-center p-4">
                 <img 
                    src={product.image_url || `https://placehold.co/400x300/png?text=${encodeURIComponent(product.name.substring(0,20))}`} 
                    alt={product.name} 
                    className="max-h-full max-w-full object-contain mix-blend-multiply transition-transform duration-500 group-hover:scale-105" 
                />
            </div>

            {/* Platform Badge (Bottom Center) */}
            <div className={`absolute bottom-3 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider border whitespace-nowrap shadow-sm ${
                product.platform.toLowerCase().includes('amazon') 
                    ? 'bg-[#232F3E] text-white border-[#FF9900]' 
                    : product.platform.toLowerCase().includes('flipkart')
                        ? 'bg-[#2874f0] text-white border-[#FFE500]'
                        : 'bg-secondary text-secondary-foreground border-border'
            }`}>
                {product.platform}
            </div>
        </div>

        {/* COL 2: Info & Actions (Right) */}
        <div className="flex-1 p-6 lg:p-8 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-border/50 bg-gradient-to-b from-transparent to-secondary/5">
            <div>
                <div className="flex justify-between items-start gap-4">
                     <h2 className="text-xl md:text-2xl font-bold leading-tight line-clamp-2 mb-2 text-foreground/90 tracking-tight" title={product.name}>
                        {product.name}
                     </h2>
                     
                     <div className="flex items-center gap-1 shrink-0">
                        <button 
                            onClick={handleRefresh} 
                            disabled={refreshing}
                            className={`p-2 rounded-full hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground ${refreshing ? 'animate-spin text-primary' : ''}`}
                            title="Refresh Price"
                        >
                            <RefreshCw className="w-5 h-5" />
                        </button>
                        <button 
                            onClick={onDelete} 
                            className="p-2 rounded-full hover:bg-red-500/10 transition-colors text-muted-foreground hover:text-red-500"
                            title="Stop Tracking"
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>
                     </div>
                </div>

                <div className="mt-6 flex flex-wrap items-baseline gap-4">
                    <span className="text-5xl font-extrabold text-foreground tracking-tighter">₹{product.current_price?.toLocaleString()}</span>
                    {discount > 0 && (
                        <div className="flex flex-col items-start leading-none gap-1">
                            <span className="text-sm text-muted-foreground line-through decoration-red-500/40 decoration-2">₹{Math.round(effectiveMax).toLocaleString()}</span>
                            <span className="text-xs text-emerald-500 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full">Save ₹{Math.round(effectiveMax - product.current_price).toLocaleString()}</span>
                        </div>
                    )}
                </div>

                {/* Quick Stats Row */}
                <div className="flex gap-4 mt-6 text-sm text-muted-foreground/80">
                     <div className="flex items-center gap-2 bg-secondary/30 px-3 py-1.5 rounded-lg">
                        <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                        Low: <span className="font-mono font-medium text-foreground">₹{analysis?.min_price_30_day?.toLocaleString() || '-'}</span>
                     </div>
                     <div className="flex items-center gap-2 bg-secondary/30 px-3 py-1.5 rounded-lg">
                        <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                        Avg: <span className="font-mono font-medium text-foreground">₹{analysis?.avg_30_day?.toLocaleString() || '-'}</span>
                     </div>
                </div>
            </div>

            <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <a 
                    href={product.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="flex-1 bg-white hover:bg-gray-100 text-black font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 shadow-xl hover:shadow-2xl hover:-translate-y-0.5 transition-all text-base group/btn"
                >
                    Buy Now <ExternalLink className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                </a>
                
                <div className="flex gap-2">
                    <button 
                        onClick={() => setShowAnalytics(true)}
                        className="px-5 py-3.5 rounded-xl font-medium border border-border bg-secondary/20 hover:bg-secondary/50 transition-all flex items-center gap-2 text-sm backdrop-blur-sm"
                    >
                        <BarChart3 className="w-4 h-4" /> 
                        <span className="hidden sm:inline">Trends</span>
                    </button>
                    
                    <button 
                        onClick={() => setAlertOpen(!alertOpen)}
                        className={`px-5 py-3.5 rounded-xl font-medium border transition-all flex items-center gap-2 text-sm ${alertOpen ? 'bg-indigo-500/10 border-indigo-500 text-indigo-400' : 'bg-background border-border hover:bg-secondary'}`}
                    >
                        {alertOpen ? <BellRing className="w-4 h-4" /> : <Bell className="w-4 h-4" />}
                        <span className="hidden sm:inline">{targetPrice ? 'Edit' : 'Set'} Alert</span>
                    </button>
                </div>
            </div>
            
             {/* Alert Drawer Inline */}
            {alertOpen && (
                <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    className="mt-4 p-4 bg-indigo-500/5 rounded-xl border border-indigo-500/20"
                >
                    <label className="text-xs font-bold text-indigo-400 mb-2 block uppercase tracking-wider">Target Price Alert</label>
                    <div className="flex gap-2">
                         <div className="relative flex-1">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">₹</span>
                            <input 
                                type="number" 
                                className="bg-background border border-border rounded-lg pl-7 pr-3 py-2 text-sm w-full focus:ring-2 focus:ring-indigo-500/50 outline-none"
                                value={targetPrice}
                                onChange={e => setTargetPrice(e.target.value)}
                            />
                         </div>
                        <button onClick={handleSetAlert} className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold px-4 rounded-lg transition-colors">Save</button>
                    </div>
                </motion.div>
            )}
        </div>
      </div>
      
      {/* Modal Portal */}
      <AnalyticsModal 
        isOpen={showAnalytics} 
        onClose={() => setShowAnalytics(false)} 
        product={product} 
        history={history} 
        analysis={analysis}
      />
    </motion.div>
  )
}
