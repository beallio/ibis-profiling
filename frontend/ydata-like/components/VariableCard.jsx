import { formatNum, formatPct } from "../helpers.js";
import { TypeIcon } from "./TypeIcon.jsx";
import { HistogramChart } from "./HistogramChart.jsx";
import { VariableDetails } from "./VariableDetails.jsx";

const { useState } = React;
const { ChevronRight, ChevronDown, Grid } = LucideReact;

export const VariableCard = ({ name, variable }) => {
  const isNumeric = variable.type === 'Numeric';
  const isCategorical = variable.type === 'Categorical' || variable.type === 'Boolean';
  const [expanded, setExpanded] = useState(true);
  const isHighCardinality = variable.type === 'Categorical' && variable.p_distinct > 0.5;

  return (
    <div className="bg-white rounded-md shadow-sm border border-gray-200 overflow-hidden mb-4">
      <div className="px-5 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
        <div className="flex items-center gap-3">
          <TypeIcon type={variable.type} />
          <h3 className="text-lg font-bold text-gray-800">{name}</h3>
        </div>
        <div className="flex gap-2">
           <span className="px-2.5 py-1 bg-gray-200 text-gray-700 text-xs rounded-full font-medium">
             {variable.logical_type && variable.logical_type !== variable.type
               ? `${variable.type} (${variable.logical_type})`
               : variable.type}
           </span>
           {isHighCardinality && (
             <span className="px-2.5 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full font-medium border border-yellow-200">
               High cardinality
             </span>
           )}
           {variable.is_unique && (
             <span className="px-2.5 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium border border-blue-200">
               Unique
             </span>
           )}
        </div>
      </div>

      <div className="p-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <div className="grid grid-cols-2 gap-x-8 gap-y-1">
              <div className="col-span-2 mb-3"><h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Overview</h4></div>
              
              <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Distinct</div>
              <div className="text-sm font-medium text-right py-1 border-b border-gray-50">{formatNum(variable.n_distinct)} <span className="text-gray-400 text-xs font-normal">({formatPct(variable.p_distinct)})</span></div>
              
              <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Missing</div>
              <div className="text-sm font-medium text-right py-1 border-b border-gray-50">
                <span className={variable.n_missing > 0 ? 'text-red-600' : ''}>{formatNum(variable.n_missing)}</span>
                <span className="text-gray-400 text-xs font-normal ml-1">({formatPct(variable.p_missing)})</span>
              </div>

              {variable.type === 'Categorical' && (
                <>
                  <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Empty</div>
                  <div className="text-sm font-medium text-right py-1 border-b border-gray-50">
                    <span className={variable.n_empty > 0 ? 'text-amber-600' : ''}>{formatNum(variable.n_empty)}</span>
                    <span className="text-gray-400 text-xs font-normal ml-1">({formatPct(variable.p_empty)})</span>
                  </div>
                </>
              )}                  
              {isNumeric && (
                <>
                  <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Infinite</div>
                  <div className="text-sm font-medium text-right py-1 border-b border-gray-50">{formatNum(variable.n_infinite)} <span className="text-gray-400 text-xs font-normal">({formatPct(variable.p_infinite)})</span></div>
                  
                  <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Mean</div>
                  <div className="text-sm font-medium text-right py-1 border-b border-gray-50">{formatNum(variable.mean)}</div>
                  
                  <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Minimum</div>
                  <div className="text-sm font-medium text-right py-1 border-b border-gray-50">{formatNum(variable.min)}</div>
                  
                  <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Maximum</div>
                  <div className="text-sm font-medium text-right py-1 border-b border-gray-50">{formatNum(variable.max)}</div>
                  
                  <div className="text-sm text-gray-600 py-1 border-b border-gray-50">Zeros</div>
                  <div className="text-sm font-medium text-right py-1 border-b border-gray-50">
                     <span className={variable.n_zeros > 0 ? 'text-yellow-600' : ''}>{formatNum(variable.n_zeros)}</span>
                     <span className="text-gray-400 text-xs font-normal ml-1">({formatPct(variable.p_zeros)})</span>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="flex flex-col justify-center items-center pb-6">
            {variable.histogram && (
               <HistogramChart 
                 data={variable.histogram} 
                 isCategorical={isCategorical} 
               />
            )}
            {(!variable.histogram || variable.histogram.bins.length === 0) && isHighCardinality && (
               <div className="text-gray-400 text-sm flex flex-col items-center justify-center h-full text-center p-4">
                 <Grid size={32} className="mb-2 opacity-20" />
                 High cardinality variable.<br/>Too many distinct values to display distribution.
               </div>
            )}
          </div>
        </div>

        {isNumeric && (
          <div className="mt-4 flex justify-end">
            <button 
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded"
            >
              {expanded ? 'Hide details' : 'More details'}
              {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
          </div>
        )}

        {(expanded || !isNumeric) && <VariableDetails variable={variable} />}
      </div>
    </div>
  );
};
