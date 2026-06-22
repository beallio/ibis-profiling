import { parseMatrixData } from "../helpers.js";

const { useMemo } = React;

// Sub-component for rendering standardized Correlation Matrices
export const CorrelationMatrixComponent = ({ data }) => {
  const { columns, matrix } = useMemo(() => parseMatrixData(data), [data]);
  
  if (!columns || columns.length === 0 || !matrix || matrix.length === 0) {
    return <div className="py-12 text-center text-gray-500">No data available for this metric.</div>;
  }

  return (
    <div className="overflow-x-auto pb-4">
      <table className="mx-auto text-xs border-collapse">
        <thead>
          <tr>
            <th className="p-1"></th>
            {columns.map(c => (
              <th key={c} className="p-2 font-mono font-bold text-gray-500 h-28 align-bottom">
                <div className={`transform origin-bottom-left ml-6 truncate w-24 ${columns.length > 15 ? '-rotate-90' : '-rotate-45'}`}>
                  {c}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <td className="p-2 font-mono font-bold text-gray-500 text-right pr-6 whitespace-nowrap">
                {columns[i]}
              </td>
              {row.map((cell, j) => {
                const isMissing = cell === null || cell === undefined || Number.isNaN(cell);
                const bgOpacity = isMissing ? 0 : Math.min(Math.abs(cell), 1);
                const bgColor = isMissing ? 'transparent' : cell >= 0 ? `rgba(59, 130, 246, ${bgOpacity})` : `rgba(239, 68, 68, ${bgOpacity})`;
                
                return (
                  <td 
                    key={j} 
                    className="w-12 h-12 border border-gray-100 text-center hover:scale-105 transition-transform cursor-crosshair relative group" 
                    style={{ backgroundColor: bgColor }}
                  >
                    {isMissing ? (
                      <span className="text-gray-400 text-[10px] italic">Null</span>
                    ) : (
                      <>
                        <span className={`font-mono text-[10px] ${bgOpacity > 0.5 ? 'text-white' : 'text-gray-800'}`}>
                          {cell === 1 ? '1.0' : cell.toFixed(2)}
                        </span>
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
