import { useState } from 'react';
import { trackProduct } from '../services/api';
import { Search, Plus, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function AddProduct({ onProductAdded }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    try {
      await trackProduct(url);
      setUrl('');
      if (onProductAdded) onProductAdded();
    } catch (err) {
      console.error(err);
      alert('Failed to add product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto my-8"
    >
      <form onSubmit={handleSubmit} className="relative group">
        
        {/* Glowing border effect */}
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl opacity-20 group-focus-within:opacity-100 transition duration-1000 group-focus-within:duration-200 blur-sm"></div>
        
        <div className="relative flex items-center bg-black rounded-2xl p-2 border border-white/10 shadow-2xl">
            <div className="pl-4 pr-3 text-muted-foreground group-focus-within:text-white transition-colors">
              <Search className="h-5 w-5" />
            </div>
            <input
              type="text"
              className="w-full bg-transparent border-none focus:ring-0 text-lg py-3 text-white placeholder:text-muted-foreground/40 font-medium"
              placeholder="Paste Amazon or Flipkart URL..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-white hover:bg-gray-100 text-black px-6 py-3 rounded-xl font-bold transition-all flex items-center gap-2 transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Plus className="w-5 h-5" />
                  <span className="hidden sm:inline">Track</span>
                </>
              )}
            </button>
        </div>
      </form>
    </motion.div>
  );
}
