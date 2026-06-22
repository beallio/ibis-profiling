const { AlertTriangle } = LucideReact;

// Sub-component for Nullity Matrix Rendering (Missingno style SVG)
export const NullityMatrix = ({ data, metadata }) => {
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

  const rowCompleteness = values.map(row => row.filter(isMissing => !isMissing).length);

  const getBlocks = (cIdx) => {
      const blocks = [];
      let inBlock = false;
      let start = 0;
      for (let r = 0; r < numRows; r++) {
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
    <div className="overflow-x-auto mt-8 pt-4 border-t border-gray-100">
      <h3 className="text-lg font-medium text-gray-800 mb-2">Matrix</h3>

      {metadata?.truncated && (
        <div className="mb-4 text-amber-600 text-xs font-medium flex items-center gap-1">
          <AlertTriangle size={12} /> Matrix truncated to first {metadata.limit} columns out of {metadata.original_count}
        </div>
      )}

      <p className="text-sm text-gray-500 mb-6">Visualization of data completeness (first {numRows} rows). Gaps indicate missing data.</p>

      <div className="flex gap-4 items-end" style={{ minWidth: `${Math.max(800, numCols * 25)}px` }}>
        <div className="flex-1 relative">
          <div className="flex mb-2">
             {columns.map((c, i) => (
                <div key={c} style={{ width: `${100/numCols}%` }} className="flex justify-start h-32 relative overflow-visible">
                   <span className={`absolute bottom-1 left-1/2 origin-bottom-left text-[10px] font-mono text-gray-500 whitespace-nowrap ${numCols > 15 ? '-rotate-90' : '-rotate-45'}`}>{c}</span>
                </div>
             ))}
          </div>
          
          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} preserveAspectRatio="none" className="w-full h-[500px] bg-gray-50 border border-gray-200 shadow-inner rounded-sm">
            {columns.map((_, cIdx) => (
               <g key={cIdx} transform={`translate(${cIdx * colWidth}, 0)`}>
                  <line x1={colWidth/2} y1="0" x2={colWidth/2} y2={svgHeight} stroke="#e5e7eb" strokeWidth="0.5" strokeDasharray="4 4" />
                  
                  {getBlocks(cIdx).map((block, i) => (
                     <rect
                        key={i}
                        x={colWidth * 0.05}
                        y={block.start * rowHeight}
                        width={colWidth * 0.9}
                        height={(block.end - block.start + 1) * rowHeight}
                        fill="#475569"
                        className="transition-all hover:fill-blue-500"
                     />
                  ))}
               </g>
            ))}
          </svg>
        </div>

        <div className="w-20 h-[500px] relative flex flex-col items-center">
          <div className="text-[10px] text-gray-400 font-mono text-center absolute -top-8 w-full">Data<br/>Completeness</div>
          <svg viewBox={`0 0 100 ${svgHeight}`} preserveAspectRatio="none" className="w-full h-full border-r border-t border-b border-gray-200 bg-gray-50 rounded-r-sm">
            <polygon points={sparkPoly} fill="rgba(59, 130, 246, 0.15)" />
            <polyline points={sparklinePoints} fill="none" stroke="#3b82f6" strokeWidth="1.5" />
          </svg>
          <div className="absolute top-2 right-2 text-xs font-mono text-gray-400">{numCols}</div>
          <div className="absolute bottom-2 right-2 text-xs font-mono text-gray-400">0</div>
        </div>
      </div>
    </div>
  );
}
