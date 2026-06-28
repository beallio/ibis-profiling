import { ALERT_CONFIG, TYPE_LABELS } from "../constants.js";
import { filterMissingBins } from "../helpers.js";
import { NumericHistogram } from "./NumericHistogram.jsx";
import { StatCard } from "./StatCard.jsx";

const { AlertTriangle, Database, Table, CheckCircle2, FileWarning, ChevronRight } = LucideReact;

export function OverviewSection({
  theme,
  reportData,
  setActiveTab,
  setSearch,
  getAlertsForVariable,
  generateAlertMessage,
}) {
  return (
                <div className="space-y-8 animate-in fade-in duration-500">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-20">
                    <StatCard
                      title="Total Rows"
                      value={reportData.table.n.toLocaleString()}
                      icon={Database}
                      sub={reportData.table.p_duplicates !== undefined ?
                        `${(reportData.table.p_duplicates * 100).toFixed(1)}% duplicated rows` :
                        "Duplication check skipped"}
                    />
                    <StatCard
                      title="Variables"
                      value={reportData.table.n_var}
                      icon={Table}
                      sub={Object.entries(reportData.table.types || {})
                        .filter(([_, count]) => count > 0)
                        .map(([type, count]) => `${count} ${TYPE_LABELS[type] || type.substring(0, 3)}`)
                        .join(', ')} 
                      color="purple" 
                    />                    <StatCard
                      title="Missing Cells"
                      value={`${reportData.table.p_cells_missing === 0 ? '0' : (reportData.table.p_cells_missing * 100).toFixed(2)}%`}
                      icon={FileWarning}
                      sub={`Across ${reportData.table.n_vars_with_missing} variables`}
                      color="red"
                    />
                    <StatCard
                      title="Empty Cells"
                      value={`${reportData.table.p_cells_empty === 0 ? '0' : (reportData.table.p_cells_empty * 100).toFixed(2)}%`}
                      icon={Database}
                      sub={`Across ${reportData.table.n_vars_with_empty || 0} variables`}
                      color="slate"
                    />
                    <StatCard
                      title="Memory Size"                      value={`${(reportData.table.memory_size / 1024 / 1024).toFixed(2)} MiB`}
                      icon={CheckCircle2}
                      sub={`${reportData.table.record_size} bytes per record`}
                      color="green"
                    />                  </div>

                  <section className={`${theme.bgCard} border ${theme.border} p-6 rounded-2xl shadow-xl`}>
                    <h3 className={`font-bold text-lg mb-4 flex items-center gap-2 ${theme.textPrimary}`}>
                      <AlertTriangle className="text-yellow-500" size={20} /> System Alerts ({reportData.alerts?.length || 0})
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {reportData.alerts?.map((alert, idx) => {
                        const config = ALERT_CONFIG[alert.alert_type] || ALERT_CONFIG.DEFAULT;
                        const Icon = config.icon;
                        return (
                          <div key={idx} className={`flex items-start gap-3 p-4 ${theme.bgMain} border rounded-xl hover:${theme.bgCardAlt} transition-all duration-200 ${config.border}`}>
                            <div className={`mt-0.5 ${config.color}`}>
                              <Icon size={16} />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1.5">
                                <span className={`text-[10px] font-mono font-bold uppercase px-1.5 py-0.5 rounded tracking-wider ${config.bg} ${config.color}`}>
                                  {alert.alert_type}
                                </span>
                              </div>
                              <div className={`text-sm font-medium ${theme.textSecondary}`}>{generateAlertMessage(alert)}</div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </section>

                  <section>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className={`font-bold text-lg ${theme.textPrimary}`}>Variable Quick View</h3>
                      <button onClick={() => setActiveTab('variables')} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium transition-colors">
                        View detailed stats <ChevronRight size={14} />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                      {Object.entries(reportData.variables).map(([name, meta]) => {
                        const varAlerts = getAlertsForVariable(name);
                        const { filteredBins: qvBins, filteredCounts: qvCounts } = filterMissingBins(meta.histogram?.bins, meta.histogram?.counts);

                        return (
                          <div 
                            key={name} 
                            className={`${theme.bgCard} border ${theme.border} p-4 rounded-2xl hover:border-blue-500/30 transition-colors group cursor-pointer flex flex-col h-full shadow-lg`} 
                            onClick={() => {
                              setSearch(name);
                              setActiveTab('variables');
                            }}
                          >
                            <div className="flex justify-between items-start mb-3">
                              <span className={`font-bold text-sm ${theme.textSecondary} group-hover:text-blue-400 transition-colors truncate pr-2`}>{name}</span>
                              <span className={`text-[9px] ${theme.bgCardAlt} ${theme.textMuted} px-1.5 py-0.5 rounded uppercase font-bold tracking-wider`}>{meta.type}</span>
                            </div>
                            
                            <div className="flex-1 mb-3">
                              {meta.type === 'Categorical' || meta.type === 'Boolean' ? (
                                <div className="h-full flex flex-col justify-center">
                                  <div className={`h-10 w-full ${theme.bgCardAlt} rounded-lg flex items-end gap-0.5 p-1`}>
                                    {qvCounts.slice(0, 10).map((c, i) => {
                                      const max = Math.max(...qvCounts, 1);
                                      return (
                                        <div 
                                          key={i} 
                                          className="bg-purple-500/40 hover:bg-purple-400 transition-all rounded-t-sm flex-1"
                                          style={{ height: `${(c / max) * 100}%` }}
                                          title={`${qvBins[i]}: ${c.toLocaleString()}`}
                                        />
                                      );
                                    })}
                                  </div>
                                  <div className={`text-[8px] ${theme.textSub} mt-1 text-center truncate`}>
                                    {qvBins.length} distinct categories
                                  </div>
                                </div>
                              ) : (
                                <NumericHistogram bins={qvBins} counts={qvCounts} height={40} showTooltip={false} />
                              )}
                            </div>

                            <div className={`flex justify-between items-center mt-auto pt-3 border-t ${theme.borderAlt}`}>
                              <div className="flex gap-1">
                                {varAlerts.slice(0, 3).map((a, i) => {
                                   const config = ALERT_CONFIG[a.alert_type] || ALERT_CONFIG.DEFAULT;
                                   const Icon = config.icon;
                                   return <div key={i} className={`${config.color} ${config.bg} p-1 rounded`} title={a.alert_type}><Icon size={10} /></div>;
                                })}
                                {varAlerts.length > 3 && <span className={`text-[10px] ${theme.textSub} self-center`}>+{varAlerts.length-3}</span>}
                              </div>
                              <div className="flex flex-col items-end">
                                <span className={`text-[9px] font-bold font-mono ${meta.n_missing > 0 ? 'text-red-400' : 'text-green-500'}`}>
                                  {((meta.p_missing || 0) * 100).toFixed(1)}% null
                                </span>
                                {meta.type === 'Categorical' && meta.n_empty > 0 && (
                                  <span className="text-[9px] font-bold font-mono text-amber-400">
                                    {((meta.p_empty || 0) * 100).toFixed(1)}% empty
                                  </span>
                                )}
                              </div>
                            </div>                          </div>
                        );
                      })}
                    </div>
                  </section>
                </div>
  );
}
