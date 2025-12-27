import { useEffect, useState } from 'react';
import { getProducts, deleteProduct } from '../services/api';
import Navbar from '../components/Navbar';
import AddProduct from '../components/AddProduct';
import StatsGrid from '../components/StatsGrid';
import ProductCard from '../components/ProductCard';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchProducts = async () => {
    try {
      const res = await getProducts();
      // Sort by updated_at desc usually
      setProducts(res.data.sort((a,b) => new Date(b.created_at) - new Date(a.created_at)));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if(!window.confirm("Are you sure you want to stop tracking this product? This action cannot be undone.")) return;
    try {
        await deleteProduct(id);
        // Optimistic update or refresh
        setProducts(products.filter(p => p.id !== id));
    } catch(e) {
        alert("Failed to delete product");
        fetchProducts(); // Revert on failure
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="min-h-screen bg-background pb-20 selection:bg-primary/30">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 pt-12">
        
        {/* Hero Section */}
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16 space-y-6"
        >
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight">
                Track Prices. <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">Save Big.</span>
            </h1>
            <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
                Paste a link from Amazon or Flipkart. Our intelligent bots monitor price drops 24/7 so you never miss a deal again.
            </p>
            <AddProduct onProductAdded={fetchProducts} />
        </motion.div>

        {/* Stats */}
        <StatsGrid products={products} />

        {/* Product Grid */}
        <div className="space-y-6">
             <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold tracking-tight">Your Watchlist</h3>
                <span className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm font-medium">{products.length} Items</span>
             </div>
             
             {loading ? (
                <div className="flex justify-center py-20">
                    <Loader2 className="w-12 h-12 animate-spin text-primary" />
                </div>
             ) : products.length === 0 ? (
                <div className="text-center py-32 border-2 border-dashed rounded-3xl border-muted bg-card/20">
                    <p className="text-muted-foreground text-lg">Your watchlist is empty.</p>
                    <p className="text-sm text-muted-foreground/60 mt-2">Paste a URL above to start tracking.</p>
                </div>
             ) : (
                <div className="grid grid-cols-1 gap-8">
                    {products.map(product => (
                        <ProductCard key={product.id} product={product} onDelete={() => handleDelete(product.id)} />
                    ))}
                </div>
             )}
        </div>
      </main>
    </div>
  )
}
