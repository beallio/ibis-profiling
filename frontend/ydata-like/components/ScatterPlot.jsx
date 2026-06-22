import { formatNum } from "../helpers.js";

export const ScatterPlot = ({ points, xLabel, yLabel }) => {
  if (!points || points.length === 0) return (
    <div className="h-96 flex items-center justify-center text-gray-400 italic bg-gray-50 border border-dashed border-gray-200 rounded">
      No data points available for this pair.
    </div>
  );

  const padding = 60;
  const width = 800;
  const height = 600;

  const xValues = points.map(p => p.x);
  const yValues = points.map(p => p.y);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);

  const xRange = xMax - xMin || 1;
  const yRange = yMax - yMin || 1;

  const scaleX = (x) => padding + ((x - xMin) / xRange) * (width - 2 * padding);
  const scaleY = (y) => height - padding - ((y - yMin) / yRange) * (height - 2 * padding);

  return (
    <div className="flex flex-col items-center w-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto bg-white max-h-[700px]">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(v => (
          <React.Fragment key={v}>
            <line 
              x1={padding} y1={height - padding - v * (height - 2 * padding)} 
              x2={width - padding} y2={height - padding - v * (height - 2 * padding)} 
              stroke="#f1f5f9" strokeWidth="1" 
            />
            <line 
              x1={padding + v * (width - 2 * padding)} y1={padding} 
              x2={padding + v * (width - 2 * padding)} y2={height - padding} 
              stroke="#f1f5f9" strokeWidth="1" 
            />
          </React.Fragment>
        ))}

        {/* Axes */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#94a3b8" strokeWidth="2" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#94a3b8" strokeWidth="2" />

        {/* Points */}
        {points.map((p, i) => (
          <circle 
            key={i} 
            cx={scaleX(p.x)} 
            cy={scaleY(p.y)} 
            r="3" 
            fill="#3b82f6" 
            fillOpacity="0.6"
            className="hover:fill-blue-800 transition-colors"
          >
            <title>{`(${formatNum(p.x)}, ${formatNum(p.y)})`}</title>
          </circle>
        ))}

        {/* Axis Labels */}
        <text x={width / 2} y={height - 10} textAnchor="middle" className="text-xs font-medium fill-gray-500 uppercase tracking-wider">{xLabel}</text>
        <text x={15} y={height / 2} textAnchor="middle" transform={`rotate(-90, 15, ${height / 2})`} className="text-xs font-medium fill-gray-500 uppercase tracking-wider">{yLabel}</text>
        
        {/* Min/Max Labels */}
        <text x={padding} y={height - padding + 20} textAnchor="middle" className="text-[10px] fill-gray-400 font-mono">{formatNum(xMin)}</text>
        <text x={width - padding} y={height - padding + 20} textAnchor="middle" className="text-[10px] fill-gray-400 font-mono">{formatNum(xMax)}</text>
        <text x={padding - 10} y={height - padding} textAnchor="end" className="text-[10px] fill-gray-400 font-mono">{formatNum(yMin)}</text>
        <text x={padding - 10} y={padding} textAnchor="end" className="text-[10px] fill-gray-400 font-mono">{formatNum(yMax)}</text>
      </svg>
    </div>
  );
};
