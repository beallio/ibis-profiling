import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const CategoricalChart = ({ bins, counts, limit = 10 }) => {
  const { theme } = useContext(ThemeContext);
  if (!bins || !counts || counts.length === 0) return <div className={`p-4 text-center text-xs ${theme.textSub}`}>No data distribution data</div>;
  const max = Math.max(...counts);
  const displayLimit = limit;
  const topBins = bins.slice(0, displayLimit);
  const topCounts = counts.slice(0, displayLimit);

  return (
    <div className={`space-y-3 ${theme.bgCardAlt} p-4 rounded-xl border ${theme.borderAlt}`}>
      {topBins.map((bin, i) => (
        <div key={i} className="flex items-center gap-3 text-xs">
          <div className={`w-24 truncate ${theme.textMuted} font-medium text-right`} title={String(bin)}>
            {String(bin)}
          </div>
          <div className={`flex-1 h-5 ${theme.bgMain} rounded overflow-hidden relative group border ${theme.border}`}>
            <div 
              className="h-full bg-blue-500/50 group-hover:bg-blue-400/80 transition-all rounded-r"
              style={{ width: `${(topCounts[i] / (max || 1)) * 100}%` }}
            />
          </div>
          <div className={`w-12 font-mono ${theme.textSecondary} text-right`}>{topCounts[i].toLocaleString()}</div>
        </div>
      ))}
      {bins.length > displayLimit && (
        <div className={`text-center text-[10px] ${theme.textSub} mt-4 border-t ${theme.borderAlt} pt-2`}>
          Showing top {displayLimit} of {bins.length} distinct categories
        </div>
      )}
    </div>
  );
};
