import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const ScatterPlot = ({ data, xLabel, yLabel }) => {
  const { theme } = useContext(ThemeContext);
  if (!data || data.length === 0) return <div className={`h-96 flex items-center justify-center ${theme.textSub} italic border ${theme.border} rounded-xl`}>No interaction data for this pair</div>;

  const margin = { top: 20, right: 20, bottom: 40, left: 60 };
  const width = 800;
  const height = 400;

  const xValues = data.map(d => d.x);
  const yValues = data.map(d => d.y);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);

  // Add 5% padding to scales
  const xRange = xMax - xMin || 1;
  const yRange = yMax - yMin || 1;
  const xSMin = xMin - xRange * 0.05;
  const xSMax = xMax + xRange * 0.05;
  const ySMin = yMin - yRange * 0.05;
  const ySMax = yMax + yRange * 0.05;

  const xScale = (val) => margin.left + ((val - xSMin) / (xSMax - xSMin)) * (width - margin.left - margin.right);
  const yScale = (val) => height - margin.bottom - ((val - ySMin) / (ySMax - ySMin)) * (height - margin.top - margin.bottom);

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${width} ${height}`} className={`w-full h-auto ${theme.bgCardAlt} rounded-xl border ${theme.border}`}>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(v => (
          <React.Fragment key={v}>
            <line 
              x1={margin.left} y1={yScale(ySMin + v * (ySMax - ySMin))} 
              x2={width - margin.right} y2={yScale(ySMin + v * (ySMax - ySMin))} 
              stroke={theme.border} strokeDasharray="4"
            />
            <line 
              x1={xScale(xSMin + v * (xSMax - xSMin))} y1={margin.top} 
              x2={xScale(xSMin + v * (xSMax - xSMin))} y2={height - margin.bottom} 
              stroke={theme.border} strokeDasharray="4"
            />
          </React.Fragment>
        ))}

        {/* Axes */}
        <line x1={margin.left} y1={height - margin.bottom} x2={width - margin.right} y2={height - margin.bottom} stroke={theme.textMuted} strokeWidth="2" />
        <line x1={margin.left} y1={margin.top} x2={margin.left} y2={height - margin.bottom} stroke={theme.textMuted} strokeWidth="2" />

        {/* Points */}
        {data.map((d, i) => (
          <circle 
            key={i} 
            cx={xScale(d.x)} 
            cy={yScale(d.y)} 
            r="3" 
            fill="rgba(59, 130, 246, 0.6)" 
            className="hover:fill-blue-400 transition-colors"
          >
            <title>{`(${d.x.toFixed(4)}, ${d.y.toFixed(4)})`}</title>
          </circle>
        ))}

        {/* Labels */}
        <text x={width / 2} y={height - 5} textAnchor="middle" className={`text-xs font-bold fill-current ${theme.textMuted}`}>{xLabel}</text>
        <text x={15} y={height / 2} textAnchor="middle" transform={`rotate(-90, 15, ${height / 2})`} className={`text-xs font-bold fill-current ${theme.textMuted}`}>{yLabel}</text>
      </svg>
    </div>
  );
};
