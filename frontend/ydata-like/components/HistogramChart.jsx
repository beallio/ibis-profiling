import { formatNum } from "../helpers.js";

export const HistogramChart = ({ data, isCategorical = false }) => {
  if (!data || !data.bins || !data.counts || data.bins.length === 0) return null;
  
  const maxCount = Math.max(...data.counts);
  const total = data.counts.reduce((a, b) => a + b, 0);
  
  const chartData = data.bins.map((bin, i) => ({
    label: bin,
    count: data.counts[i],
    percent: ((data.counts[i] / total) * 100).toFixed(1)
  }));

  if (isCategorical) {
    return (
      <div className="flex flex-col gap-3 mt-4 w-full max-w-md">
        {chartData.map((d, i) => (
          <div key={i} className="flex flex-col text-sm">
            <div className="flex justify-between text-gray-600 mb-1">
              <span className="truncate pr-4 font-medium">{d.label}</span>
              <span className="font-mono text-xs whitespace-nowrap">{formatNum(d.count)} ({d.percent}%)</span>
            </div>
            <div className="w-full bg-gray-100 h-5 rounded-sm overflow-hidden flex">
              <div 
                className="h-full bg-blue-500" 
                style={{ width: `${(d.count / maxCount) * 100}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex items-end h-40 gap-1.5 w-full max-w-md mt-6 mb-10">
      {chartData.map((d, i) => {
        const showLabel = i === 0 || i === chartData.length - 1 || i % 5 === 0;
        return (
          <div key={i} className="flex-1 flex flex-col justify-end group relative h-full">
            <div 
              className="w-full bg-blue-500 hover:bg-blue-600 transition-colors rounded-t-sm" 
              style={{ height: `${Math.max((d.count / maxCount) * 100, 2)}%` }}
              title={`${d.label}: ${d.count}`}
            ></div>
            {showLabel && (
              <div className="text-[11px] text-gray-500 absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
                {String(d.label).replace(/[[\]()]/g, '').split(',')[0]}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
