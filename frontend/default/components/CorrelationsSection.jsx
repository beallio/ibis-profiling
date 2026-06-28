import { CorrelationMatrixComponent } from "./CorrelationMatrixComponent.jsx";

const { AlertTriangle, Info, PieChart } = LucideReact;

export function CorrelationsSection({
  theme,
  reportData,
  corrType,
  setCorrType,
  currentCorrelationRaw,
}) {
  return (
                <div className="space-y-6 animate-in fade-in duration-700">
                  <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-10 shadow-2xl`}>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
                      <div>
                        <h2 className={`text-2xl font-bold mb-2 flex items-center gap-2 ${theme.textPrimary}`}>
                          <PieChart className="text-blue-500" /> Correlation Matrix
                        </h2>
                        {reportData.correlations?._metadata?.truncated && (
                          <div className="mb-4 text-amber-400 text-sm font-medium flex items-center gap-2">
                            <AlertTriangle size={16} />
                            Matrix truncated to top {reportData.correlations._metadata.limit} variables out of {reportData.correlations._metadata.original_count}.
                          </div>
                        )}
                        <p className={`${theme.textSub} text-sm`}>
                          Linear dependence overview. Coloring indicates absolute correlation strength. <span className="text-blue-400">Blue</span> is positive, <span className="text-red-400">Red</span> is negative.
                          {reportData.correlations?.[corrType]?.sampled && (
                            <span className="block mt-1 text-amber-400 font-medium">
                              <Info size={14} className="inline mr-1" />
                              Sampled estimate: calculated from a representative subset of {reportData.correlations[corrType].sample_size?.toLocaleString()} rows.
                            </span>
                          )}
                        </p>
                      </div>
                      
                      {reportData.correlations && (
                        <div className={`flex ${theme.bgMain} border ${theme.border} rounded-lg p-1`}>
                          {Object.keys(reportData.correlations).filter(type => type !== '_metadata').map(type => (
                            <button

                              key={type}
                              onClick={() => setCorrType(type)}
                              className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-all ${
                                corrType === type ? 'bg-blue-600 text-white shadow-md' : `${theme.textSub} hover:${theme.textMuted}`
                              }`}
                            >
                              {type}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {currentCorrelationRaw && (
                      <CorrelationMatrixComponent data={currentCorrelationRaw} />
                    )}
                  </div>
                </div>
  );
}
