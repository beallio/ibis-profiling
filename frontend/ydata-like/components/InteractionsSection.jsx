import { ScatterPlot } from "./ScatterPlot.jsx";

const { useState, useMemo } = React;
const { ScatterChart, AlertTriangle } = LucideReact;

export const InteractionsSection = ({ data }) => {
  if (!data.interactions || Object.keys(data.interactions).length === 0) return null;

  const columns = Object.keys(data.interactions).filter(k => k !== '_metadata').sort();
  const [colX, setColX] = useState(columns[0]);
  const [colY, setColY] = useState(columns[1] || columns[0]);

  const points = useMemo(() => {
    if (data.interactions[colX] && data.interactions[colX][colY]) {
      return data.interactions[colX][colY];
    }
    return [];
  }, [data.interactions, colX, colY]);

  return (
    <div id="interactions" className="space-y-4 animate-fadeIn section">
      <div className="flex items-center gap-2 mb-4">
        <ScatterChart size={24} className="text-slate-600" />
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold text-gray-800">Interactions</h2>
          {data.interactions?._metadata?.is_truncated && (
            <span className="text-xs text-amber-600 font-medium flex items-center gap-1">
              <AlertTriangle size={12} /> Top {data.interactions._metadata.active_columns.length} most interactive variables shown
            </span>
          )}
        </div>
      </div>
      <div className="bg-white rounded-md shadow-sm border border-gray-200 p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-1 space-y-6">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">X-Axis</label>
              <div className="flex flex-col gap-1 max-h-64 overflow-y-auto custom-scrollbar border border-gray-100 rounded-sm p-1">
                {columns.map(col => (
                  <button
                    key={col}
                    onClick={() => setColX(col)}
                    className={`text-left px-3 py-2 text-sm rounded transition-colors ${colX === col ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    {col}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Y-Axis</label>
              <div className="flex flex-col gap-1 max-h-64 overflow-y-auto custom-scrollbar border border-gray-100 rounded-sm p-1">
                {columns.map(col => (
                  <button
                    key={col}
                    onClick={() => setColY(col)}
                    className={`text-left px-3 py-2 text-sm rounded transition-colors ${colY === col ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    {col}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="md:col-span-3 flex items-center justify-center min-h-[500px]">
            <ScatterPlot points={points} xLabel={colX} yLabel={colY} />
          </div>
        </div>
      </div>
    </div>
  );
};
