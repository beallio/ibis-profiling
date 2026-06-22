import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const NumericHistogram = ({ bins, counts, height = 60, showTooltip = true }) => {
  const { theme } = useContext(ThemeContext);
  if (!counts || counts.length === 0) return <div className={`h-full w-full ${theme.bgCardAlt} rounded-lg flex items-center justify-center text-xs ${theme.textSub}`}>No chart data</div>;
  
  // Ensure all counts are numbers and filter out any weirdness
  const numericCounts = counts.map(c => Number(c) || 0);
  const max = Math.max(...numericCounts, 1);
  
  return (
    <div className={`flex items-end gap-0.5 w-full ${theme.bgCardAlt} p-2 rounded-lg`} style={{ height }}>
      {numericCounts.map((c, i) => {
        let binLabel = bins?.[i];
        if (binLabel !== undefined && !String(binLabel).includes('[') && !Number.isNaN(Number(binLabel))) {
          binLabel = Number(binLabel) % 1 !== 0 ? Number(binLabel).toFixed(2) : binLabel;
        }

        return (
          <div 
            key={i} 
            className="bg-blue-500/60 hover:bg-blue-400 transition-all duration-200 rounded-t-sm flex-1 relative group"
            style={{ height: `${(c / max) * 100}%` }}
          >
            {showTooltip && (
              <div className={`absolute bottom-full mb-2 left-1/2 -translate-x-1/2 ${theme.bgCard} border ${theme.border} ${theme.textPrimary} text-[10px] px-2 py-1 rounded hidden group-hover:block whitespace-nowrap z-10 pointer-events-none shadow-xl`}>
                <div className={`${theme.textMuted} mb-0.5`}>{binLabel ? `Bin: ${binLabel}` : 'Value'}</div>
                <div className="font-mono text-blue-300">{c.toLocaleString()} count</div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
