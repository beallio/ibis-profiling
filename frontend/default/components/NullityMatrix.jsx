import { ThemeContext } from "../theme.js";

const { useContext } = React;
const { AlertTriangle } = LucideReact;

// Sub-component for Nullity Matrix Rendering (Missingno style SVG)
export const NullityMatrix = ({ data, metadata }) => {
  const { theme } = useContext(ThemeContext);
  // Data is now a list of dicts: [ {col1: true, col2: false}, ... ]
  if (!data || !Array.isArray(data) || data.length === 0) return null;

  const columns = Object.keys(data[0]);
  const numRows = data.length;
  const numCols = columns.length;
  
  // Convert list of dicts to row-major values array for processing
  const values = data.map(row => columns.map(c => row[c]));

  const svgWidth = 1000;
  const svgHeight = 400;
  const colWidth = svgWidth / numCols;
  const rowHeight = svgHeight / numRows;

  // Determine complete (non-missing) elements per row for the sparkline
  const rowCompleteness = values.map(row => row.filter(isMissing => !isMissing).length);

  // Helper to consolidate consecutive present data blocks for efficient SVG rendering
  const getBlocks = (cIdx) => {
      const blocks = [];
      let inBlock = false;
      let start = 0;
      for (let r = 0; r < numRows; r++) {
          // 'values' has true for missing. We draw dark blocks for PRESENT data.
          const isPresent = !values[r][cIdx];
          if (isPresent && !inBlock) {
              inBlock = true;
              start = r;
          } else if (!isPresent && inBlock) {
              inBlock = false;
              blocks.push({ start, end: r - 1 });
          }
      }
      if (inBlock) {
          blocks.push({ start, end: numRows - 1 });
      }
      return blocks;
  };

  const sparklinePoints = rowCompleteness.map((count, rIdx) => 
     `${(count / numCols) * 100},${rIdx * rowHeight + rowHeight / 2}`
  ).join(' ');
  const sparkPoly = `0,${rowHeight / 2} ${sparklinePoints} 0,${(numRows - 1) * rowHeight + rowHeight / 2}`;

  return (
    <div className={`mt-12 pt-8 border-t ${theme.border}`}>
      <h3 className={`font-bold text-xl mb-2 ${theme.textPrimary}`}>Nullity Matrix</h3>
      
      {metadata?.truncated && (
        <div className="mb-4 text-amber-400 text-sm font-medium flex items-center gap-2">
          <AlertTriangle size={16} />
          Displaying first {metadata.limit} columns out of {metadata.original_count} total.
        </div>
      )}

      <p className={`text-sm ${theme.textSub} mb-6`}>Dense visualization of data completeness (first {numRows} rows). Gaps indicate missing data.</p>

      <div className="flex gap-4 items-end" style={{ minWidth: `${Math.max(1000, numCols * 25)}px` }}>
        <div className="flex-1 relative">
          {/* Column Labels */}
          <div className="flex mb-2">
             {columns.map((c, i) => (
                <div key={c} style={{ width: `${100/numCols}%` }} className="flex justify-start h-32 relative overflow-visible">
                   <span className={`absolute bottom-1 left-1/2 origin-bottom-left text-[10px] font-mono ${theme.textMuted} whitespace-nowrap ${numCols > 15 ? '-rotate-90' : '-rotate-45'}`}>{c}</span>
                </div>
             ))}
          </div>
          
          {/* SVG Matrix */}
          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} preserveAspectRatio="none" className={`w-full h-[500px] ${theme.bgInput} border ${theme.border} shadow-inner rounded-sm`}>
            {columns.map((_, cIdx) => (
               <g key={cIdx} transform={`translate(${cIdx * colWidth}, 0)`}>
                  {getBlocks(cIdx).map((block, i) => (
                     <rect
                        key={i}
                        x={colWidth * 0.05}
                        y={block.start * rowHeight}
                        width={colWidth * 0.9}
                        height={(block.end - block.start + 1) * rowHeight}
                        fill={theme.id === 'light' ? '#475569' : '#cbd5e1'}
                        className="transition-all hover:fill-blue-400"
                     />
                  ))}
               </g>
            ))}
          </svg>
        </div>

        {/* Completeness Sparkline */}
        <div className="w-20 h-[500px] relative flex flex-col items-center">
          <div className={`text-[10px] ${theme.textSub} font-mono text-center absolute -top-8 w-full`}>Data<br/>Completeness</div>
          <svg viewBox={`0 0 100 ${svgHeight}`} preserveAspectRatio="none" className={`w-full h-full border-r border-t border-b ${theme.borderAlt} ${theme.bgCardAlt} rounded-r-sm`}>
            <polygon points={sparkPoly} fill="rgba(59, 130, 246, 0.15)" />
            <polyline points={sparklinePoints} fill="none" stroke="#3b82f6" strokeWidth="1.5" />
          </svg>
          <div className={`absolute top-2 right-2 text-xs font-mono ${theme.textMuted}`}>{numCols}</div>
          <div className={`absolute bottom-2 right-2 text-xs font-mono ${theme.textMuted}`}>0</div>
        </div>
      </div>
    </div>
  );
}
