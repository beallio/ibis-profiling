import { formatNum } from "../helpers.js";
import { NullityMatrix } from "./NullityMatrix.jsx";
import { CorrelationMatrixComponent } from "./CorrelationMatrixComponent.jsx";

const { AlertTriangle } = LucideReact;

export const MissingValuesSection = ({ data }) => {
  const missingBar = data.missing?.bar?.matrix || data.missing?.bar || null;
  
  if (!data.missing || Object.keys(data.missing).length === 0) {
    return null;
  }

  const total = data.table.n;
  let missingData = [];
  
  if (missingBar && Array.isArray(missingBar.columns) && Array.isArray(missingBar.counts)) {
    missingData = missingBar.columns.map((name, i) => {
      const missingCount = missingBar.counts[i];
      const present = total - missingCount;
      return { name, present, missing: missingCount, percent: (present / total) * 100 };
    });
  }

  return (
    <div id="missing" className="space-y-4 animate-fadeIn section">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle size={24} className="text-slate-600" />
        <h2 className="text-2xl font-bold text-gray-800">Missing values</h2>
      </div>
      <div className="bg-white rounded-md shadow-sm border border-gray-200 p-8">
        {missingData.length > 0 && (
          <div className="mb-12">
            <h3 className="text-lg font-medium text-gray-800 mb-6">Count</h3>
            <div className="flex flex-col gap-3 w-full max-w-4xl">
              {missingData.map((d, i) => (
                <div key={i} className="flex items-center gap-4 text-sm group">
                  <div className="w-48 text-gray-600 text-right truncate font-mono font-medium" title={d.name}>
                    {d.name}
                  </div>
                  <div className="flex-1 bg-gray-100 h-6 rounded-sm overflow-hidden flex border border-gray-200 shadow-inner group-hover:border-gray-300 transition-colors">
                    <div 
                      className="h-full bg-slate-700 group-hover:bg-slate-800 transition-colors" 
                      style={{ width: `${d.percent}%` }}
                      title={`${d.name}: ${d.missing} missing`}
                    ></div>
                    <div 
                      className="h-full bg-red-100/50" 
                      style={{ width: `${100 - d.percent}%` }}
                    ></div>
                  </div>
                  <div className="font-mono text-xs whitespace-nowrap text-gray-500 w-48">
                    <span className="font-bold text-slate-700">{formatNum(d.present)}</span> present / <span className="text-red-600">{formatNum(d.missing)}</span> missing
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.missing?.matrix?.matrix?.matrix && (
           <NullityMatrix 
              data={data.missing.matrix.matrix.matrix} 
              metadata={data.missing.matrix.matrix._metadata}
            />
        )}
        
        {data.missing?.heatmap?.matrix?.matrix && data.missing.heatmap.matrix.matrix.length > 0 && (
          <div className="mt-8 pt-8 border-t border-gray-100">
            <div className="flex flex-col mb-10">
              <h3 className="text-lg font-medium text-gray-800">Heatmap</h3>
              {data.missing.heatmap.matrix._metadata?.truncated && (
                <span className="text-xs text-amber-600 font-medium flex items-center gap-1 mt-1">
                  <AlertTriangle size={12} /> Truncated to top {data.missing.heatmap.matrix._metadata.limit} variables with most missing values
                </span>
              )}
            </div>
            <div className="flex justify-center">
              <CorrelationMatrixComponent data={data.missing.heatmap.matrix} />
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
