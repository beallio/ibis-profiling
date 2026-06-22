
    import { REPORT_DATA } from "./data.js";
    import { formatBytes, formatPct, formatNum, getAlertColor } from "./helpers.js";
    import { TypeIcon } from "./components/TypeIcon.jsx";
    import { HistogramChart } from "./components/HistogramChart.jsx";
    import { StatRow } from "./components/StatRow.jsx";
    import { NullityMatrix } from "./components/NullityMatrix.jsx";
    import { CorrelationMatrixComponent } from "./components/CorrelationMatrixComponent.jsx";
    import { ScatterPlot } from "./components/ScatterPlot.jsx";

    const { useState, useMemo, useEffect } = React;
    const {
      AlertTriangle,
      Info,
      BarChart2,
      Hash,
      AlignLeft,
      Grid,
      ChevronRight,
      ChevronDown,
      PieChart,
      ScatterChart
    } = LucideReact;

    // --- MAIN SECTIONS ---
    const OverviewSection = ({ data }) => {
      const table = data.table;
      const types = Object.entries(table.types || {});

      return (
        <div id="overview" className="space-y-2 animate-fadeIn section-top">
          <div className="flex items-center gap-2 mb-4">
            <Info size={24} className="text-slate-600" />
            <h2 className="text-2xl font-bold text-gray-800">Overview</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            <div className="bg-white rounded-md shadow-sm border border-gray-200 p-3 flex flex-col lg:col-span-6">
              <h3 className="text-sm font-semibold text-gray-700 border-b border-gray-100 pb-1 mb-2 uppercase tracking-wider">Dataset statistics</h3>
              <div className="grid grid-cols-1 gap-0 flex-1">
                <StatRow label="Number of variables" value={formatNum(table.n_var)} compact={true} />
                <StatRow label="Number of observations" value={formatNum(table.n)} compact={true} />
                <StatRow label="Missing cells" value={formatNum(table.n_cells_missing)} compact={true} />
                <StatRow label="Missing cells (%)" value={formatPct(table.p_cells_missing)} compact={true} />
                <StatRow label="Empty cells" value={formatNum(table.n_cells_empty)} compact={true} />
                <StatRow label="Empty cells (%)" value={formatPct(table.p_cells_empty)} compact={true} />
                <StatRow label="Variables with missing values" value={formatNum(table.n_vars_with_missing)} compact={true} />
                <StatRow label="Variables with empty values" value={formatNum(table.n_vars_with_empty)} compact={true} />
                <StatRow label="Variables with all missing values" value={formatNum(table.n_vars_all_missing)} compact={true} />
                {table.n_vars_constant !== undefined && (
                  <StatRow label="Constant variables" value={formatNum(table.n_vars_constant)} compact={true} />
                )}
                {table.n_duplicates !== undefined && (
                  <>
                    <StatRow label="Duplicate rows" value={formatNum(table.n_duplicates)} compact={true} />
                    <StatRow label="Duplicate rows (%)" value={formatPct(table.p_duplicates)} compact={true} />
                  </>
                )}
                <StatRow label="Total size in memory" value={formatBytes(table.memory_size)} compact={true} />
                <StatRow label="Average record size in memory" value={`${formatNum(table.record_size)} B`} compact={true} />
              </div>
            </div>

            <div className="bg-white rounded-md shadow-sm border border-gray-200 p-3 flex flex-col lg:col-span-2">
              <h3 className="text-sm font-semibold text-gray-700 border-b border-gray-100 pb-1 mb-2 uppercase tracking-wider">Variable types</h3>
              <div className="grid grid-cols-1 gap-0 flex-1">
                {types.length > 0 ? types.map(([type, count]) => (
                  <StatRow key={type} label={type} value={count} compact={true} />
                )) : (
                  <span className="text-gray-400 text-sm italic">No type data available.</span>
                )}
              </div>
            </div>

            {data.alerts && data.alerts.length > 0 ? (
              <div className="bg-white rounded-md shadow-sm border border-gray-200 flex flex-col overflow-hidden lg:col-span-4">
                <div className="bg-gray-50 p-2 border-b border-gray-200 flex items-center shrink-0">
                  <AlertTriangle size={16} className="text-yellow-500 mr-2" />
                  <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Alerts</h3>
                </div>
                <div className="p-0 overflow-y-auto max-h-[300px] flex-1">
                  <ul className="divide-y divide-gray-100">
                    {data.alerts.map((alert, idx) => {
                      return (
                        <li key={idx} className="p-2 hover:bg-gray-50 transition-colors flex items-start gap-3 text-xs">
                          <span className={`
                            inline-block px-1.5 py-0.5 text-[10px] rounded border font-medium whitespace-nowrap mt-0.5
                            ${getAlertColor(alert.alert_type)}
                          `}>
                            {alert.alert_type.replace(/_/g, ' ')}
                          </span>
                          <span className="text-gray-700">
                            <strong>{alert.fields.join(', ')}</strong> has a {alert.alert_type.toLowerCase().replace(/_/g, ' ')} condition
                            {alert.value !== undefined ? ` (${typeof alert.value === 'number' && alert.value < 1 ? formatPct(alert.value) : formatNum(alert.value)})` : ''}.
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-md shadow-sm border border-gray-200 p-3 flex items-center justify-center lg:col-span-4 text-gray-400 italic text-sm">
                No alerts detected.
              </div>
            )}
          </div>
        </div>
      );
    };

    const VariableDetails = ({ variable }) => {
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

    const VariableCard = ({ name, variable }) => {
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

    const MissingValuesSection = ({ data }) => {
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

    const CorrelationsSection = ({ data }) => {
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

    const SampleSection = ({ data }) => {
      const sampleData = data.sample?.head || data.sample;
      if (!sampleData || (Array.isArray(sampleData) && sampleData.length === 0)) return null;
      
      let columns = [];
      let rows = [];
      
      if (Array.isArray(sampleData)) {
        columns = Object.keys(sampleData[0]);
        rows = sampleData;
      } else {
        columns = Object.keys(sampleData);
        const numRows = sampleData[columns[0]].length;
        rows = Array.from({ length: numRows }).map((_, i) => {
          const row = {};
          columns.forEach(col => {
            row[col] = sampleData[col][i];
          });
          return row;
        });
      }

      return (
        <div id="sample" className="space-y-4 animate-fadeIn section">
          <div className="flex items-center gap-2 mb-4">
            <AlignLeft size={24} className="text-slate-600" />
            <h2 className="text-2xl font-bold text-gray-800">Sample</h2>
          </div>
          <div className="bg-white rounded-md shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-800">First rows</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr>
                    {columns.map(col => (
                      <th key={col} className="py-3 px-4 bg-gray-100 font-semibold text-sm text-gray-700 border-b border-gray-200 border-r last:border-r-0 whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 border-b border-gray-100 last:border-0">
                      {columns.map(col => {
                        const val = row[col];
                        const isNull = val === null || val === 'NaN' || (typeof val === 'number' && Number.isNaN(val));
                        return (
                          <td key={col} className={`py-2.5 px-4 text-sm border-r border-gray-100 last:border-r-0 font-mono ${isNull ? 'text-red-400 italic' : 'text-gray-600'}`}>
                            {isNull ? 'Null' : String(val)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      );
    };

    const InteractionsSection = ({ data }) => {
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

    function App() {
      const [imgError, setImgError] = useState(false);

      if (!REPORT_DATA || !REPORT_DATA.analysis || !REPORT_DATA.table || !REPORT_DATA.variables) {
        return (
          <div className="min-h-screen bg-gray-100 flex items-center justify-center p-8">
            <div className="bg-white p-6 rounded-md shadow border border-red-200 text-center max-w-md">
              <AlertTriangle className="text-red-500 mx-auto mb-4" size={48} />
              <h2 className="text-xl font-bold text-gray-800 mb-2">Invalid Payload</h2>
              <p className="text-gray-600 text-sm">
                The provided JSON payload does not match the expected <code>ibis-profiling</code> specification.
              </p>
            </div>
          </div>
        );
      }

      const navItems = [
        { id: 'overview', label: 'Overview', icon: <Info size={16} /> },
        { id: 'variables', label: 'Variables', icon: <Hash size={16} /> }
      ];

      if (REPORT_DATA.correlations && Object.keys(REPORT_DATA.correlations).length > 0) {
        navItems.push({ id: 'correlations', label: 'Correlations', icon: <PieChart size={16} /> });
      }

      if (REPORT_DATA.interactions && Object.keys(REPORT_DATA.interactions).length > 0) {
        navItems.push({ id: 'interactions', label: 'Interactions', icon: <ScatterChart size={16} /> });
      }

      if (REPORT_DATA.missing && Object.keys(REPORT_DATA.missing).length > 0) {
        navItems.push({ id: 'missing', label: 'Missing values', icon: <AlertTriangle size={16} /> });
      }

      navItems.push({ id: 'sample', label: 'Sample', icon: <AlignLeft size={16} /> });

      return (
        <div className="min-h-screen bg-gray-100 font-sans text-gray-800 selection:bg-blue-200 pb-12">
          <header className="bg-slate-800 text-white shadow-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-14">
                <div className="flex items-center gap-3">
                  {imgError ? (
                    <div className="bg-blue-500 text-white p-1.5 rounded-md">
                      <BarChart2 size={20} />
                    </div>
                  ) : (
                    <img 
                      src="https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/ibis-profiling-icon.png" 
                      alt="Ibis Profiler Logo" 
                      className="w-8 h-8 rounded-md bg-white p-0.5 object-contain" 
                      onError={() => setImgError(true)} 
                    />
                  )}
                  <h1 className="text-xl font-bold tracking-tight">Profiling Report</h1>
                </div>
                <div className="text-slate-300 text-sm font-mono bg-slate-900 px-3 py-1 rounded truncate max-w-[200px] md:max-w-md">
                  {REPORT_DATA.analysis.title}
                </div>
              </div>
            </div>
            
            <div className="bg-slate-50 border-b border-slate-200 shadow-sm">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <nav className="flex space-x-1 overflow-x-auto no-scrollbar justify-center">
                  {navItems.map((item) => (
                    <a
                      key={item.id}
                      href={`#${item.id}`}
                      className="flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100 hover:border-slate-300 transition-all"
                    >
                      {item.icon}
                      {item.label}
                    </a>
                  ))}
                </nav>
              </div>
            </div>
          </header>

          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
            <OverviewSection data={REPORT_DATA} />
            
            <div id="variables" className="space-y-4 section">
              <div className="flex items-center gap-2 mb-4">
                <Hash size={24} className="text-slate-600" />
                <h2 className="text-2xl font-bold text-gray-800">Variables</h2>
              </div>
              <div className="animate-fadeIn">
                {Object.entries(REPORT_DATA.variables).map(([colName, variableData]) => (
                  <VariableCard key={colName} name={colName} variable={variableData} />
                ))}
              </div>
            </div>

            <CorrelationsSection data={REPORT_DATA} />

            <InteractionsSection data={REPORT_DATA} />

            <MissingValuesSection data={REPORT_DATA} />
            
            <SampleSection data={REPORT_DATA} />
          </main>

          <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center text-sm text-gray-500 mt-8 border-t border-gray-200 pt-6">
            <span>Report generated via Ibis Profiling</span>
            <span className="font-mono text-xs">{REPORT_DATA.package?.version || 'ibis-profiling'}</span>
          </footer>
        </div>
      );
    }

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  
