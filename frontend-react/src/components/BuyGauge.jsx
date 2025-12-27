import { motion } from 'framer-motion';

export default function BuyGauge({ current, min, max, avg }) {
  // If we don't have enough data, show neutral
  // Check if we have enough data (min != max)
  if (!min || !max || min === max) {
      return (
          <div className="w-full">
               <div className="h-3 rounded-full w-full bg-gradient-to-r from-green-500/20 to-green-500/50 relative overflow-hidden ring-1 ring-green-500/20">
                    <div className="absolute inset-0 bg-green-500/10" />
               </div>
               <div className="mt-4 flex justify-between items-center text-xs text-green-600 font-medium px-1">
                   <span>Initial Price Set</span>
                   <span>Tracking Started...</span>
               </div>
               <div className="mt-2 text-xs text-muted-foreground grid grid-cols-2 gap-2">
                    <div>
                        <span className="block text-[10px] uppercase tracking-wider opacity-70">Current</span>
                        <span className="font-mono font-medium text-foreground">₹{current?.toLocaleString()}</span>
                    </div>
                </div>
          </div>
      )
  }
  // Calculate position
  // Lower price = Higher quality = Green (Right side)
  // Logic: 
  // Max Price (Bad) --- Min Price (Good)
  // We map [Max, Min] -> [0%, 100%]
  
  let percent = ((max - current) / (max - min)) * 100;
  
  // Clamp
  if (percent < 0) percent = 0;
  if (percent > 100) percent = 100;

  return (
    <div className="w-full">
        <div className="flex justify-between text-xs font-bold mb-2 text-muted-foreground uppercase px-1">
            <span className="text-red-500">Skip</span>
            <span className="text-yellow-500">Wait</span>
            <span className="text-blue-500">Okay</span>
            <span className="text-green-500">Buy</span>
        </div>
        
        {/* The Bar */}
        <div className="relative h-3 rounded-full w-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 shadow-inner ring-1 ring-white/10">
            {/* The Pointer */}
            <motion.div 
                initial={{ left: '50%' }}
                animate={{ left: `${percent}%` }}
                transition={{ type: 'spring', stiffness: 60, damping: 15 }}
                className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-6 h-6 bg-white dark:bg-zinc-900 border-[3px] border-white dark:border-zinc-700 rounded-full shadow-lg z-10 flex items-center justify-center cursor-help"
                title={`Score: ${Math.round(percent)}/100`}
            >
                <div className="w-1.5 h-1.5 bg-foreground rounded-full"></div>
            </motion.div>
        </div>
        
        <div className="mt-4 text-xs text-muted-foreground grid grid-cols-2 gap-2">
            <div>
                <span className="block text-[10px] uppercase tracking-wider opacity-70">Lowest (30d)</span>
                <span className="font-mono font-medium text-foreground">₹{min?.toLocaleString()}</span>
            </div>
            <div className="text-right">
                <span className="block text-[10px] uppercase tracking-wider opacity-70">Highest (30d)</span>
                <span className="font-mono font-medium text-foreground">₹{max?.toLocaleString()}</span>
            </div>
        </div>
    </div>
  )
}
