import { useState, useEffect } from 'react';
import { ExternalLink, RefreshCw, Bell, BellRing, Trash2, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { getPriceHistory, getAnalysis, refreshProduct, setAlert } from '../services/api';
import PriceChart from './PriceChart';
import BuyGauge from './BuyGauge';

export default function ProductCard({ product }) {
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Alert State
  const [targetPrice, setTargetPrice] = useState(Math.round(product.current_price * 0.95));
  const [alertOpen, setAlertOpen] = useState(false);

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
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-card border rounded-3xl overflow-hidden shadow-lg mb-6 group hover:border-primary/30 transition-all duration-300"
    >
      <div className="flex flex-col md:flex-row">
         {/* Image Section - Elegant Gradient Background */}
         <div className="w-full md:w-1/3 bg-white p-8 flex items-center justify-center relative md:border-r border-border/50">
            <div className="absolute inset-0 bg-gradient-to-br from-gray-100 to-white opacity-50" />
            <img 
                src={product.image_url || `https://placehold.co/400x300/png?text=${encodeURIComponent(product.name.substring(0,20))}`} 
                alt={product.name} 
                className="max-h-48 w-auto object-contain z-10 mix-blend-multiply transition-transform duration-500 group-hover:scale-110" 
            />
            {discount > 5 && (
                <div className="absolute top-4 left-4 bg-green-600 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg z-20 flex items-center gap-1">
                    <TrendingDown className="w-3 h-3" />
                    {discount}% OFF
                </div>
            )}
         </div>

         {/* Content Section */}
         <div className="flex-1 p-6 flex flex-col justify-between bg-card/50">
            <div>
                <div className="flex justify-between items-start mb-3">
                    <span className={`text-[10px] font-bold px-3 py-1 rounded-md uppercase tracking-wider border-b-2 shadow-sm ${
                        product.platform.toLowerCase().includes('amazon') 
                            ? 'bg-[#232F3E] text-white border-[#FF9900]' 
                            : product.platform.toLowerCase().includes('flipkart')
                                ? 'bg-[#2874f0] text-white border-[#FFE500]'
                                : 'bg-secondary/50 text-secondary-foreground border-border'
                    }`}>
                        {product.platform}
                    </span>
                    <button 
                        onClick={handleRefresh} 
                        className={`p-2 rounded-full hover:bg-secondary transition-all text-muted-foreground hover:text-foreground ${refreshing ? 'animate-spin text-primary' : ''}`}
                        title="Refresh Price"
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                </div>
                
                <h2 className="text-xl font-bold leading-tight line-clamp-2 mb-2 text-foreground/90 group-hover:text-primary transition-colors" title={product.name}>
                    {product.name}
                </h2>
                


                <div className="flex items-baseline gap-3 mb-6">
                    <span className="text-4xl font-bold text-foreground tracking-tight">₹{product.current_price?.toLocaleString()}</span>
                    {discount > 0 && (
                        <span className="text-muted-foreground line-through text-lg decoration-red-500/50 decoration-2">₹{Math.round(effectiveMax).toLocaleString()}</span>
                    )}
                </div>
            </div>

            <div className="flex gap-3 mt-auto relative z-20">
                <a 
                    href={product.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-600 bg-[length:200%_auto] hover:bg-right transition-all duration-500 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/40 active:scale-95 group/btn"
                >
                    Buy Now <ExternalLink className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                </a>
                <button 
                    onClick={() => setAlertOpen(!alertOpen)}
                    className={`px-6 py-3 rounded-xl transition-all border flex items-center justify-center gap-2 font-medium shadow-sm hover:shadow-md active:scale-95 ${alertOpen ? 'bg-secondary border-primary/50 text-primary' : 'bg-background border-border hover:bg-secondary/50 hover:border-primary/30'}`}
                >
                    {alertOpen ? <BellRing className="w-4 h-4" /> : <Bell className="w-4 h-4" />}
                    <span>Set Alert</span>
                </button>
            </div>
            
            {/* Alert Input Drawer */}
            {alertOpen && (
                <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    className="mt-4 p-4 bg-secondary/30 rounded-xl border border-border overflow-hidden"
                >
                    <label className="text-xs font-semibold text-muted-foreground mb-2 block">Trigger Alert at Price (₹)</label>
                    <div className="flex gap-2">
                        <input 
                            type="number" 
                            className="bg-background border ring-offset-background placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-lg px-3 py-2 flex-1 text-sm outline-none"
                            value={targetPrice}
                            onChange={e => setTargetPrice(e.target.value)}
                        />
                        <button onClick={handleSetAlert} className="bg-foreground text-background hover:bg-foreground/90 px-4 rounded-lg text-sm font-medium transition-colors">Set</button>
                    </div>
                </motion.div>
            )}
         </div>
      </div>

      {/* Analytics Footer (Gauge & Graph) */}
      <div className="border-t border-border bg-secondary/10 p-6 grid grid-cols-1 lg:grid-cols-2 gap-8 backdrop-blur-sm">
          <div className="space-y-4">
            {/* Gauge Component */}
            <BuyGauge 
                current={product.current_price} 
                min={analysis?.min_price_30_day || product.current_price} 
                max={analysis?.max_price_30_day} 
                avg={analysis?.avg_30_day}
            />
          </div>
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest pl-2 border-l-2 border-primary">Price History (30 Days)</h4>
            <div className="h-32 w-full">
                <PriceChart data={history} />
            </div>
          </div>
      </div>
    </motion.div>
  )
}
