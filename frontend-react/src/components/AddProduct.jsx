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
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
        </div>
        <input
          type="text"
          className="w-full pl-11 pr-32 py-4 bg-card border rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-lg placeholder:text-muted-foreground/50"
          placeholder="Paste Amazon or Flipkart URL to track..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="absolute right-2 top-2 bottom-2 bg-primary hover:bg-primary/90 text-primary-foreground px-6 rounded-xl font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <Plus className="w-5 h-5" />
              Track
            </>
          )}
        </button>
      </form>
    </motion.div>
  );
}
