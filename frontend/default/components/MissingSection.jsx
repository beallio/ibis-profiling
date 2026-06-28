import { CategoricalChart } from "./CategoricalChart.jsx";
import { CorrelationMatrixComponent } from "./CorrelationMatrixComponent.jsx";
import { NullityMatrix } from "./NullityMatrix.jsx";

const { AlertTriangle, CheckCircle2, FileWarning, PieChart } = LucideReact;

export function MissingSection({ theme, reportData }) {
  return (
                <div className="space-y-6 animate-in fade-in duration-700">
                  <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-10 shadow-2xl`}>
                     <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                      <div>
                        <h2 className={`text-2xl font-bold mb-2 flex items-center gap-2 ${theme.textPrimary}`}>
                          <FileWarning className="text-red-400" /> Missing Data Analysis
                        </h2>
                        <p className={`${theme.textSub} text-sm`}>
                          Overview of nullity across all variables in the dataset.
                        </p>
                      </div>
                    </div>

                    {reportData.missing?.bar?.matrix?.counts?.every(c => c === 0) ? (
                      <div className="py-16 text-center border-2 border-dashed border-green-500/20 rounded-xl bg-green-500/5 flex flex-col items-center">
                         <CheckCircle2 size={48} className="text-green-500 mb-4" />
                         <h3 className="text-xl font-bold text-green-400 mb-2">100% Data Completeness</h3>
                         <p className="text-slate-400">No missing values were detected in any of the {reportData.table.n_var} variables.</p>
                      </div>
                    ) : (
                      <CategoricalChart
                        bins={reportData.missing?.bar?.matrix?.columns}
                        counts={reportData.missing?.bar?.matrix?.counts}
                        limit={reportData.missing?.bar?.matrix?.columns?.length || 20}
                      />

                    )}

                    {reportData.missing?.matrix?.matrix?.matrix && reportData.missing.matrix.matrix.matrix.length > 0 && (
                      <NullityMatrix 
                         data={reportData.missing.matrix.matrix.matrix} 
                         metadata={reportData.missing.matrix.matrix._metadata}
                       />
                    )}
                    {reportData.missing?.heatmap?.matrix?.matrix && reportData.missing.heatmap.matrix.matrix.length > 0 && (
                      <div className={`mt-16 pt-8 border-t ${theme.borderAlt}`}>
                        <h3 className={`text-xl font-bold mb-2 flex items-center gap-2 ${theme.textPrimary}`}>
                          <PieChart className="text-blue-500" /> Nullity Correlation Heatmap
                        </h3>
                        {reportData.missing.heatmap.matrix._metadata?.truncated && (
                          <div className="mb-4 text-amber-400 text-sm font-medium flex items-center gap-2">
                            <AlertTriangle size={16} />
                            Correlation matrix truncated to top {reportData.missing.heatmap.matrix._metadata.limit} variables with most missing values (out of {reportData.missing.heatmap.matrix._metadata.original_count}).
                          </div>
                        )}
                        <p className={`${theme.textSub} text-sm mb-8`}>
                          {reportData.missing.heatmap.caption || "Pearson correlation of nullity between variables (-1 to 1)."}
                        </p>
                        <CorrelationMatrixComponent data={reportData.missing.heatmap.matrix} />
                      </div>
                    )}
                  </div>
                </div>
  );
}
