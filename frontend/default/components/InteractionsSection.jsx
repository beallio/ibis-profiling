import { ScatterPlot } from "./ScatterPlot.jsx";

const { AlertTriangle, Info, TrendingUp } = LucideReact;

export function InteractionsSection({
  theme,
  reportData,
  interX,
  setInterX,
  interY,
  setInterY,
  interactionCols,
  interactionData,
}) {
  return (
                <div className="space-y-6 animate-in fade-in duration-700">
                  <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-10 shadow-2xl`}>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                      <div>
                        <h2 className={`text-2xl font-bold mb-2 flex items-center gap-2 ${theme.textPrimary}`}>
                          <TrendingUp className="text-blue-400" /> Variable Interactions
                        </h2>
                        <p className={`${theme.textSub} text-sm`}>
                          Pairwise scatter plots of numeric variables (sampled up to 1,000 points).
                          {reportData.interactions?._metadata?.is_truncated && (
                            <span className="block mt-1 text-amber-400 font-medium">
                              <AlertTriangle size={14} className="inline mr-1" />
                              Displaying Top {reportData.interactions._metadata.active_columns.length} most interactive variables out of {reportData.interactions._metadata.total_numeric_columns} total numeric columns.
                            </span>
                          )}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                      <div className="space-y-2">
                        <label className={`text-xs font-bold uppercase tracking-widest ${theme.textSub}`}>X-Axis Variable</label>
                        <select 
                          value={interX} 
                          onChange={(e) => setInterX(e.target.value)}
                          className={`w-full ${theme.bgInput} border ${theme.border} rounded-lg p-2.5 text-sm font-mono ${theme.textPrimary} focus:ring-2 focus:ring-blue-500/50 outline-none`}
                        >
                          {interactionCols.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className={`text-xs font-bold uppercase tracking-widest ${theme.textSub}`}>Y-Axis Variable</label>
                        <select 
                          value={interY} 
                          onChange={(e) => setInterY(e.target.value)}
                          className={`w-full ${theme.bgInput} border ${theme.border} rounded-lg p-2.5 text-sm font-mono ${theme.textPrimary} focus:ring-2 focus:ring-blue-500/50 outline-none`}
                        >
                          {interactionCols.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                    </div>

                    <div className="flex justify-center">
                      <div className="w-full max-w-5xl">
                        <ScatterPlot data={interactionData} xLabel={interX} yLabel={interY} />
                      </div>
                    </div>

                    <div className={`mt-10 p-4 ${theme.bgCardAlt} rounded-xl border ${theme.borderAlt} text-center`}>
                       <p className={`text-xs ${theme.textSub}`}>
                         <Info size={14} className="inline mr-1 mb-0.5" /> 
                         Scatter plots help identify non-linear relationships, clusters, and outliers that correlation coefficients might miss.
                       </p>
                    </div>
                  </div>
                </div>
  );
}
