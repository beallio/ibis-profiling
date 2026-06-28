import { filterMissingBins, hasValidMetrics } from "../helpers.js";
import { AlertBadge } from "./AlertBadge.jsx";
import { CategoricalChart } from "./CategoricalChart.jsx";
import { ExtremeValuesList } from "./ExtremeValuesList.jsx";
import { MetricsSection } from "./MetricsSection.jsx";
import { NumericHistogram } from "./NumericHistogram.jsx";

const { BarChart3, ShieldCheck, TrendingUp, Percent, TextSelect } = LucideReact;

export function VariablesSection({ theme, reportData, filteredVariables, getAlertsForVariable }) {
  return (
                <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <BarChart3 className="text-blue-400" size={24} />
                      <h2 className={`text-2xl font-bold ${theme.textPrimary}`}>Variable Details</h2>
                    </div>
                    <div className={`text-xs font-mono ${theme.textSub} ${theme.bgCard} border ${theme.border} px-3 py-1.5 rounded-full`}>
                      Showing {filteredVariables.length} / {reportData.table.n_var}
                    </div>
                  </div>
                  
                  {filteredVariables.map(([name, meta]) => {
                    const varAlerts = getAlertsForVariable(name);
                    const isCategorical = meta.type === 'Categorical' || meta.type === 'Boolean';
                    const isNumericOrDate = meta.type === 'Numeric' || meta.type === 'DateTime';
                    const hasExtremeValues = (meta.extreme_values_smallest && meta.extreme_values_smallest.length > 0) || 
                                             (meta.extreme_values_largest && meta.extreme_values_largest.length > 0);

                    const coreMetrics = [
                      { label: "Mean", val: meta.mean },
                      { label: "Std Dev", val: meta.std },
                      { label: "Min", val: meta.min },
                      { label: "Max", val: meta.max },
                      { label: "Mean Length", val: meta.mean_length },
                      { label: "Min Length", val: meta.min_length },
                      { label: "Max Length", val: meta.max_length },
                      { label: "Unique", val: meta.is_unique }
                    ];
                    
                    const dataProperties = [
                      { label: "Zero Values", val: meta.n_zeros },
                      { label: "% Zeros", val: meta.p_zeros, isPercent: true },
                      { label: "Negative Values", val: meta.n_negative },
                      { label: "% Negative", val: meta.p_negative, isPercent: true },
                      { label: "Infinite Values", val: meta.n_infinite },
                      { label: "Hashable", val: meta.hashable },
                      { label: "Monotonic Inc.", val: meta.monotonic_increasing },
                      { label: "Monotonic Dec.", val: meta.monotonic_decreasing }
                    ];

                    const advancedStats = [
                      { label: "Skewness", val: meta.skewness },
                      { label: "Kurtosis", val: meta.kurtosis },
                      { label: "Variance", val: meta.variance },
                      { label: "Sum", val: meta.sum }
                    ];

                    const shapeAndScale = [
                      { label: "Range", val: meta.range },
                      { label: "IQR", val: meta.iqr },
                      { label: "Coeff Var (CV)", val: meta.cv },
                      { label: "Mean Abs Dev (MAD)", val: meta.mad },
                    ];

                    const renderCol1 = hasValidMetrics(coreMetrics) || hasValidMetrics(dataProperties);
                    const renderCol2 = hasValidMetrics(shapeAndScale) || hasValidMetrics(advancedStats);

                    // Filter out Nulls/NaNs from charts
                    const { filteredBins: histBins, filteredCounts: histCounts } = filterMissingBins(meta.histogram?.bins, meta.histogram?.counts);

                    let sortedLengthHistogram = null;
                    if (meta.length_histogram?.bins && meta.length_histogram?.counts) {
                      const { filteredBins: lenBins, filteredCounts: lenCounts } = filterMissingBins(meta.length_histogram.bins, meta.length_histogram.counts);
                      const paired = lenBins.map((bin, i) => ({
                        bin: Number(bin),
                        count: lenCounts[i]
                      }));
                      paired.sort((a, b) => a.bin - b.bin);
                      sortedLengthHistogram = {
                        bins: paired.map(p => String(p.bin)),
                        counts: paired.map(p => p.count)
                      };
                    }

                    return (
                      <div key={name} className={`${theme.bgCard} border ${theme.border} rounded-2xl overflow-hidden shadow-xl mb-8`}>
                        
                        <div className={`${theme.bgCardAlt} p-5 px-6 border-b ${theme.border} flex justify-between items-center flex-wrap gap-4`}>
                          <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-xl ${theme.bgMain} border ${theme.border} flex items-center justify-center text-blue-400`}>
                              {meta.type === 'Numeric' ? <TrendingUp size={20}/> : meta.type === 'Categorical' ? <TextSelect size={20}/> : <ShieldCheck size={20}/>}
                            </div>
                            <div>
                              <div className="flex items-center gap-3">
                                <h3 className={`font-bold text-lg ${theme.textPrimary}`}>{name}</h3>
                                {varAlerts.map((alert, i) => <AlertBadge key={i} alert={alert} />)}
                              </div>
                              <div className="flex gap-3 mt-1">
                                 <span className={`text-[10px] ${theme.bgMain} ${theme.textMuted} border ${theme.borderAlt} px-2 py-0.5 rounded uppercase font-bold tracking-wider`}>
                                   {meta.logical_type && meta.logical_type !== meta.type
                                     ? `${meta.type} (${meta.logical_type})`
                                     : meta.type}
                                 </span>
                                 {meta.n_distinct !== undefined && (
                                   <span className={`text-[10px] ${theme.textSub} font-mono`}>{meta.n_distinct.toLocaleString()} distinct</span>
                                 )}
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-6">
                            <div className="text-right">
                              <div className={`text-[10px] ${theme.textSub} uppercase font-bold tracking-widest`}>Missingness</div>
                              <div className={`text-sm font-bold font-mono ${meta.n_missing > 0 ? 'text-red-400' : theme.textSecondary}`}>
                                {((meta.p_missing || 0) * 100).toFixed(2)}% ({meta.n_missing?.toLocaleString() || 0})
                              </div>
                            </div>
                            {meta.type === 'Categorical' && meta.n_empty > 0 && (
                              <div className="text-right">
                                <div className={`text-[10px] ${theme.textSub} uppercase font-bold tracking-widest`}>Empty</div>
                                <div className="text-sm font-bold font-mono text-amber-400">
                                  {((meta.p_empty || 0) * 100).toFixed(2)}% ({meta.n_empty?.toLocaleString() || 0})
                                </div>
                              </div>
                            )}
                          </div>                        </div>
                        
                        <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
                          <div className={hasExtremeValues ? "lg:col-span-2" : "lg:col-span-3"}>
                             
                             {(histBins && histCounts && histCounts.length > 0) && (
                               <>
                                 <h4 className={`text-[10px] font-bold ${theme.textSub} uppercase mb-4 tracking-widest border-b ${theme.border} pb-2 flex items-center gap-2`}>
                                   <Percent size={14}/> Distribution Overview
                                 </h4>
                                 <div className="mb-8">
                                   {isNumericOrDate ? (
                                     <>
                                       <NumericHistogram bins={histBins} counts={histCounts} height={140} showTooltip={true} />
                                       <div className={`flex justify-between mt-3 px-1 text-[10px] ${theme.textSub} font-mono`}>
                                          <span>Min: {meta.min !== undefined && meta.min !== null ? meta.min : 'N/A'}</span>
                                          <span>Max: {meta.max !== undefined && meta.max !== null ? meta.max : 'N/A'}</span>
                                       </div>
                                     </>
                                   ) : (
                                     <CategoricalChart bins={histBins} counts={histCounts} />
                                   )}
                                 </div>
                               </>
                             )}

                             {sortedLengthHistogram && sortedLengthHistogram.counts.length > 0 && (
                               <div className="mb-8">
                                 <h4 className={`text-[10px] font-bold ${theme.textSub} uppercase mb-3 tracking-widest flex items-center gap-2 border-b ${theme.border} pb-2`}>
                                   Length Distribution (Chars)
                                 </h4>
                                 <CategoricalChart bins={sortedLengthHistogram.bins} counts={sortedLengthHistogram.counts} />
                               </div>
                             )}
                             
                             {(renderCol1 || renderCol2) && (
                               <div className={`grid grid-cols-1 ${renderCol1 && renderCol2 ? 'md:grid-cols-2' : ''} gap-8`}>
                                  {renderCol1 && (
                                    <div className="space-y-8">
                                      <MetricsSection title="Core Metrics" metrics={coreMetrics} />
                                      <MetricsSection title="Data Properties" metrics={dataProperties} />
                                    </div>
                                  )}
                                  {renderCol2 && (
                                    <div className="space-y-8">
                                      <MetricsSection title="Shape & Scale" metrics={shapeAndScale} />
                                      <MetricsSection title="Advanced Stats" metrics={advancedStats} />
                                    </div>
                                  )}
                               </div>
                             )}
                          </div>

                          {hasExtremeValues && (
                            <div className="space-y-6">
                              <div className={`${theme.bgMain} p-5 rounded-2xl border ${theme.borderAlt}`}>
                                <h4 className={`text-[10px] font-bold ${theme.textSub} uppercase mb-4 tracking-widest border-b ${theme.border} pb-2`}>Extreme Values</h4>
                                <div className="flex flex-col gap-6">
                                  <ExtremeValuesList title="Smallest" values={meta.extreme_values_smallest} />
                                  <ExtremeValuesList title="Largest" values={meta.extreme_values_largest} />
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
  );
}
