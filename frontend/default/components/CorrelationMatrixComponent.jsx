import { parseMatrixData } from "../helpers.js";
import { ThemeContext } from "../theme.js";

const { useMemo, useContext } = React;

// Sub-component for rendering standardized Correlation Matrices
export const CorrelationMatrixComponent = ({ data }) => {
  const { theme } = useContext(ThemeContext);
  const { columns, matrix } = useMemo(() => parseMatrixData(data), [data]);
  
  if (!columns || columns.length === 0 || !matrix || matrix.length === 0) {
    return <div className={`py-12 text-center ${theme.textSub}`}>No data available for this metric.</div>;
  }

  return (
    <div className="overflow-x-auto pb-8">
      <table className="min-w-max border-collapse">
        <thead>
          <tr>
            <th className="p-1"></th>
            {columns.map(c => (
              <th key={c} className={`p-2 font-mono font-bold ${theme.textMuted} h-32 align-bottom`}>
                <div className={`transform origin-bottom-left ml-8 truncate w-32 ${columns.length > 15 ? '-rotate-90' : '-rotate-45'}`}>
                  {c}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <td className={`p-2 font-mono font-bold ${theme.textMuted} text-right pr-8 whitespace-nowrap min-w-[150px]`}>
                {columns[i]}
              </td>
              {row.map((cell, j) => {
                const isMissing = cell === null || cell === undefined || Number.isNaN(cell);
                const bgOpacity = isMissing ? 0 : Math.min(Math.abs(cell), 1);
                // Blue for positive correlation, Red for negative
                const bgColor = isMissing ? 'transparent' : cell >= 0 ? `rgba(59, 130, 246, ${bgOpacity})` : `rgba(239, 68, 68, ${bgOpacity})`;
                
                return (
                  <td 
                    key={j} 
                    className={`w-16 h-16 border ${theme.border} text-center hover:scale-105 transition-transform cursor-crosshair relative group`} 
                    style={{ backgroundColor: bgColor }}
                  >
                    {isMissing ? (
                      <span className={`${theme.textMuted} text-[10px] italic`}>NaN</span>
                    ) : (
                      <>
                        <span className={`font-mono text-xs font-bold ${bgOpacity > 0.5 ? 'text-white' : (theme.id === 'light' ? 'text-slate-900' : 'text-slate-400')}`}>
                          {cell === 1 ? '1.0' : cell.toFixed(2)}
                        </span>
                        <div className={`absolute z-10 hidden group-hover:block bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 ${theme.bgCard} ${theme.textPrimary} text-xs rounded whitespace-nowrap shadow-xl border ${theme.border}`}>
                          {columns[i]} × {columns[j]}
                          <br/>
                          <span className="font-mono text-blue-300">{cell.toFixed(4)}</span>
                        </div>
                      </>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
