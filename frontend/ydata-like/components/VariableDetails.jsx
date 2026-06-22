import { REPORT_DATA } from "../data.js";
import { formatNum } from "../helpers.js";
import { StatRow } from "./StatRow.jsx";

export const VariableDetails = ({ variable }) => {
  const isNumeric = variable.type === 'Numeric';
  const isCategorical = variable.type === 'Categorical' || variable.type === 'Boolean';

  return (
    <div className={`mt-6 ${isNumeric ? 'border-t border-gray-100 pt-6' : ''} animate-fadeIn`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {isNumeric && (
          <>
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Quantile statistics</h4>
              <div className="bg-gray-50 p-4 rounded border border-gray-100">
                <StatRow label="Minimum" value={formatNum(variable.min)} />
                <StatRow label="5-th percentile" value={formatNum(variable["5%"])} />
                <StatRow label="Q1" value={formatNum(variable["25%"])} />
                <StatRow label="Median" value={formatNum(variable["50%"])} />
                <StatRow label="Q3" value={formatNum(variable["75%"])} />
                <StatRow label="95-th percentile" value={formatNum(variable["95%"])} />
                <StatRow label="Maximum" value={formatNum(variable.max)} />
                <StatRow label="Range" value={formatNum(variable.range)} />
                <StatRow label="Interquartile range" value={formatNum(variable.iqr)} />
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Descriptive statistics</h4>
              <div className="bg-gray-50 p-4 rounded border border-gray-100">
                <StatRow label="Standard deviation" value={formatNum(variable.std)} />
                <StatRow label="Coefficient of variation" value={formatNum(variable.cv)} />
                <StatRow label="Kurtosis" value={formatNum(variable.kurtosis)} />
                <StatRow label="Mean" value={formatNum(variable.mean)} />
                <StatRow label="MAD" value={formatNum(variable.mad)} />
                <StatRow label="Skewness" value={formatNum(variable.skewness)} />
                <StatRow label="Variance" value={formatNum(variable.variance)} />
                <StatRow label="Monotonicity" value={variable.monotonic_increasing === 'Skipped' ? 'Skipped' : (variable.monotonic_increasing ? 'Increasing' : variable.monotonic_decreasing ? 'Decreasing' : 'None')} />
              </div>
            </div>
          </>
        )}
        
        {isCategorical && (
          <>
            {variable.mean_length !== undefined && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Length (characters)</h4>
                <div className="bg-gray-50 p-4 rounded border border-gray-100">
                  <StatRow label="Max length" value={formatNum(variable.max_length)} />
                  <StatRow label="Mean length" value={formatNum(variable.mean_length)} />
                  <StatRow label="Min length" value={formatNum(variable.min_length)} />
                </div>
              </div>
            )}
            <div>
               <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Frequency Summary</h4>
               <div className="bg-gray-50 p-4 rounded border border-gray-100">
                  {variable.histogram && variable.histogram.bins.slice(0, 5).map((bin, i) => (
                    <StatRow key={i} label={String(bin)} value={formatNum(variable.histogram.counts[i])} subValue={`(${((variable.histogram.counts[i] / REPORT_DATA.table.n) * 100).toFixed(1)}%)`} />
                  ))}
                  {(!variable.histogram || variable.histogram.bins.length === 0) && (
                    <div className="h-24 flex items-center justify-center text-gray-400 text-sm italic">
                      No frequency data available.
                    </div>
                  )}
               </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
