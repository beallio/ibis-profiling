import { CorrelationMatrixComponent } from "./CorrelationMatrixComponent.jsx";

const { useState, useMemo, useEffect } = React;
const { PieChart, Info, AlertTriangle } = LucideReact;

export const CorrelationsSection = ({ data }) => {
  if (!data.correlations || Object.keys(data.correlations).length === 0) return null;
  
  const defaultCorrType = useMemo(() => {
    const keys = Object.keys(data.correlations).filter(k => k !== '_metadata');
    return keys[0] || '';
  }, [data.correlations]);
  
  const [corrType, setCorrType] = useState(defaultCorrType);

  useEffect(() => {
    if (defaultCorrType && !Object.keys(data.correlations || {}).includes(corrType)) {
      setCorrType(defaultCorrType);
    }
  }, [defaultCorrType, corrType, data.correlations]);

  if (!corrType || !data.correlations[corrType]) return null;

  return (
    <div id="correlations" className="space-y-4 animate-fadeIn section">
      <div className="flex items-center gap-2 mb-4">
        <PieChart size={24} className="text-slate-600" />
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold text-gray-800">Correlations</h2>
          {data.correlations?.[corrType]?.sampled && (
            <span className="text-xs text-amber-600 font-medium flex items-center gap-1">
              <Info size={12} /> Sampled estimate ({data.correlations[corrType].sample_size?.toLocaleString()} rows)
            </span>
          )}
          {data.correlations?._metadata?.truncated && (
            <span className="text-xs text-amber-600 font-medium flex items-center gap-1">
              <AlertTriangle size={12} /> Matrix truncated to top {data.correlations._metadata.limit} variables out of {data.correlations._metadata.original_count}
            </span>
          )}
        </div>
      </div>
      <div className="bg-white rounded-md shadow-sm border border-gray-200 p-8">
        <div className="flex justify-center gap-2 mb-8 border-b border-gray-100 pb-4 overflow-x-auto no-scrollbar">
          {Object.keys(data.correlations).filter(type => type !== '_metadata').map(type => (
            <button
              key={type}
              onClick={() => setCorrType(type)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                corrType === type ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
        <div className="flex justify-center">
           <CorrelationMatrixComponent data={data.correlations[corrType]} />
        </div>
      </div>
    </div>
  );
};
