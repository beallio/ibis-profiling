
    import { THEMES, ALERT_CONFIG, TYPE_LABELS } from "./constants.js";
    import { REPORT_DATA } from "./data.js";
    import { ThemeContext } from "./theme.js";
    import { filterMissingBins, hasValidMetrics } from "./helpers.js";
    import { AlertBadge } from "./components/AlertBadge.jsx";
    import { CategoricalChart } from "./components/CategoricalChart.jsx";
    import { CorrelationMatrixComponent } from "./components/CorrelationMatrixComponent.jsx";
    import { ExtremeValuesList } from "./components/ExtremeValuesList.jsx";
    import { MetricRow } from "./components/MetricRow.jsx";
    import { MetricsSection } from "./components/MetricsSection.jsx";
    import { NullityMatrix } from "./components/NullityMatrix.jsx";
    import { NumericHistogram } from "./components/NumericHistogram.jsx";
    import { ScatterPlot } from "./components/ScatterPlot.jsx";
    import { StatCard } from "./components/StatCard.jsx";

    const { useState, useMemo, useEffect, createContext, useContext } = React;
    const { 
      BarChart3, AlertTriangle, Table, Database, Info, Search, 
      Clock, CheckCircle2, LayoutDashboard, PieChart, ChevronRight,
      MapPin, ShieldCheck, TrendingUp, Percent,
      Fingerprint, Lock, Copy, FileWarning, TextSelect, X, Layers,
      Sun, Moon, Contrast
    } = LucideReact;

    function AppContent() {
      const { theme, setTheme } = useContext(ThemeContext);
      const [reportData, setReportData] = useState(REPORT_DATA);
      
      // Initialize activeTab from URL hash if present
      const getInitialTab = () => {
        const hash = window.location.hash.slice(1);
        const validTabs = ['overview', 'variables', 'interactions', 'correlations', 'missing', 'alerts', 'sample'];
        return validTabs.includes(hash) ? hash : 'overview';
      };

      const [activeTab, setActiveTab] = useState(getInitialTab);
      const [search, setSearch] = useState('');
      const [imgError, setImgError] = useState(false);

      const numericCols = useMemo(() => {
        return Object.entries(reportData.variables)
          .filter(([_, meta]) => meta.type === 'Numeric')
          .map(([name]) => name);
      }, [reportData]);

      const interactionCols = useMemo(() => {
        if (!reportData.interactions) return [];
        return Object.keys(reportData.interactions).filter(k => k !== '_metadata').sort();
      }, [reportData]);

      const [interX, setInterX] = useState('');
      const [interY, setInterY] = useState('');

      useEffect(() => {
        const cols = interactionCols.length > 0 ? interactionCols : numericCols;
        if (!interX && cols.length > 0) setInterX(cols[0]);
        if (!interY && cols.length > 1) setInterY(cols[1]);
        else if (!interY && cols.length > 0) setInterY(cols[0]);
      }, [interactionCols, numericCols]);

      const interactionData = useMemo(() => {
        if (!reportData.interactions || !interX || !interY) return [];
        return reportData.interactions[interX]?.[interY] || [];
      }, [reportData.interactions, interX, interY]);

      // Support hash-based switching for deep linking
      useEffect(() => {
        const handleHashChange = () => {
          setActiveTab(getInitialTab());
        };
        window.addEventListener('hashchange', handleHashChange);
        return () => window.removeEventListener('hashchange', handleHashChange);
      }, []);

      const defaultCorrType = useMemo(() => {
        if (!reportData.correlations) return '';
        const keys = Object.keys(reportData.correlations).filter(k => k !== '_metadata');
        return keys[0] || '';
      }, [reportData.correlations]);
      const [corrType, setCorrType] = useState(defaultCorrType);

      // Re-evaluate if default changes (e.g., if reportData loads asynchronously)
      useEffect(() => {
        if (defaultCorrType && !Object.keys(reportData.correlations || {}).includes(corrType)) {
          setCorrType(defaultCorrType);
        }
      }, [defaultCorrType, corrType, reportData.correlations]);

      const filteredVariables = useMemo(() => {
        if (!reportData || !reportData.variables) return [];
        return Object.entries(reportData.variables).filter(([key]) => 
          key.toLowerCase().includes(search.toLowerCase())
        );
      }, [search, reportData]);

      const sampleRows = useMemo(() => {
        if (!reportData || !reportData.sample || !reportData.sample.head) return [];
        const cols = Object.keys(reportData.sample.head);
        if (cols.length === 0) return [];
        const numRows = reportData.sample.head[cols[0]].length;
        
        return Array.from({ length: numRows }).map((_, i) => {
          const row = {};
          cols.forEach(col => {
            row[col] = reportData.sample.head[col][i];
          });
          return row;
        });
      }, [reportData]);

      const generateAlertMessage = (alert) => {
        if (alert.message) return alert.message;
        const fieldStr = alert.fields.join(', ');
        switch (alert.alert_type) {
          case 'UNIQUE': return `${fieldStr} contains entirely unique values.`;
          case 'CONSTANT': return `${fieldStr} has a constant value across all rows.`;
          case 'HIGH_CARDINALITY': return `${fieldStr} has high cardinality (${alert.value?.toLocaleString() || 'many'} distinct values).`;
          case 'MISSING': return `${fieldStr} has missing values.`;
          default: return `${fieldStr} triggered a ${alert.alert_type} alert.`;
        }
      };

      const getAlertsForVariable = (varName) => {
        return reportData.alerts?.filter(a => a.fields.includes(varName)) || [];
      };

      const currentCorrelationRaw = corrType ? reportData.correlations?.[corrType] : null;

      // Polymorphic Navigation Construction
      const navItems = [
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
        { id: 'variables', label: 'Variables', icon: BarChart3 }
      ];

      const hasInteractions = reportData.interactions && Object.keys(reportData.interactions).length > 0;
      if (hasInteractions) {
        navItems.push({ id: 'interactions', label: 'Interactions', icon: TrendingUp });
      }
      
      const hasMissing = reportData.missing && Object.keys(reportData.missing).length > 0;
      if (hasMissing) {
        navItems.push({ id: 'missing', label: 'Missing', icon: FileWarning });
      }
      
      const hasCorrelations = reportData.correlations && Object.keys(reportData.correlations).length > 0;
      if (hasCorrelations) {
        navItems.push({ id: 'correlations', label: 'Correlations', icon: PieChart });
      }
      
      const hasDuplicates = reportData.duplicates && Object.keys(reportData.duplicates).length > 0;
      if (hasDuplicates) {
        navItems.push({ id: 'duplicates', label: 'Duplicates', icon: Layers });
      }
      
      if (reportData.sample && reportData.sample.head && Object.keys(reportData.sample.head).length > 0) {
        navItems.push({ id: 'sample', label: 'Sample Data', icon: Table });
      }

      return (
        <div className={`min-h-screen ${theme.bgMain} ${theme.textSecondary} font-sans pb-20 lg:pb-0 transition-colors duration-300`}>
          
          <aside className={`fixed left-0 top-0 bottom-0 w-64 ${theme.bgSidebar} border-r ${theme.border} backdrop-blur-md z-20 hidden lg:block`}>
            <div className="p-6 h-full flex flex-col">
              <div className="flex items-center gap-3 mb-10">
                {imgError ? (
                  <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20">
                    <Database className="text-white" size={20} />
                  </div>
                ) : (
                  <img 
                    src="https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/ibis-profiling-icon.png" 
                    alt="Ibis Profiler Logo" 
                    className={`w-10 h-10 rounded-xl shadow-lg shadow-blue-500/20 object-cover border ${theme.borderAlt} ${theme.bgCard} p-1`} 
                    onError={() => setImgError(true)} 
                  />
                )}
                <div>
                  <h1 className={`font-bold text-lg leading-tight tracking-tight ${theme.textPrimary}`}>Ibis Profiler</h1>
                </div>
              </div>

              <nav className="space-y-1 flex-1">
                {navItems.map(item => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                        activeTab === item.id 
                          ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' 
                          : `${theme.textMuted} hover:${theme.bgCardAlt} hover:${theme.textPrimary}`
                      }`}
                    >
                      <Icon size={18} />
                      <span className="font-medium text-sm">{item.label}</span>
                    </button>
                  );
                })}
              </nav>

              <div className="mt-auto pt-6 space-y-4">
                <div className={`p-4 ${theme.bgCardAlt} rounded-xl border ${theme.borderAlt}`}>
                  <div className={`flex items-center gap-2 mb-3 ${theme.textSub}`}>
                    <Sun size={14} />
                    <span className="text-xs font-bold uppercase tracking-wider">Appearance</span>
                  </div>
                  <div className={`flex items-center p-1 ${theme.bgMain} rounded-lg border ${theme.border}`}>
                    {Object.values(THEMES).map(t => {
                      const Icon = t.icon;
                      return (
                        <button
                          key={t.id}
                          onClick={() => setTheme(t)}
                          title={t.name}
                          className={`flex-1 flex justify-center py-1.5 rounded-md transition-all ${
                            theme.id === t.id ? 'bg-blue-600 text-white shadow-sm' : `${theme.textSub} hover:${theme.textMuted}`
                          }`}
                        >
                          <Icon size={16} />
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className={`p-4 ${theme.bgCardAlt} rounded-xl border ${theme.borderAlt}`}>
                  <div className={`flex items-center gap-2 mb-2 ${theme.textSub}`}>
                    <Clock size={14} />
                    <span className="text-xs">Job Duration</span>
                  </div>
                  <div data-visual-volatile="" className={`text-sm font-mono ${theme.textSecondary}`}>
                    {reportData.analysis.duration !== undefined ? (
                      reportData.analysis.duration > 1000 
                        ? `${(reportData.analysis.duration / 1000).toFixed(2)} s` 
                        : `${Number(reportData.analysis.duration).toFixed(0)} ms`
                    ) : (
                      `${Math.max(0, new Date(reportData.analysis.date_end) - new Date(reportData.analysis.date_start))} ms`
                    )}
                  </div>
                </div>
              </div>
            </div>
          </aside>

          <main className="lg:pl-64">
            
            <header className={`sticky top-0 ${theme.bgHeader} backdrop-blur-xl border-b ${theme.border} z-10 px-8 py-4 flex flex-col md:flex-row justify-between items-center gap-4`}>
              <div>
                <h2 className={`text-xl font-bold ${theme.textPrimary}`}>{reportData.analysis.title}</h2>
                <p data-visual-volatile="" className={`text-xs ${theme.textSub} font-mono`}>Analysis run {new Date(reportData.analysis.date_start).toLocaleString()}</p>
              </div>
              <div className="relative w-full md:w-80">
                <Search className={`absolute left-3 top-1/2 -translate-y-1/2 ${theme.textSub} pointer-events-none`} size={16} />
                <input 
                  type="text" 
                  placeholder="Search attributes..." 
                  className={`w-full ${theme.bgInput} border ${theme.border} rounded-full py-2 pl-10 pr-10 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200 ${theme.textPrimary}`}
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                {search.length > 0 && (
                  <button 
                    onClick={() => setSearch('')} 
                    className={`absolute right-3 top-1/2 -translate-y-1/2 ${theme.textMuted} hover:${theme.textPrimary} transition-colors p-1 ${theme.bgCardAlt} rounded-full flex items-center justify-center cursor-pointer z-10`}
                    type="button"
                    aria-label="Clear search"
                  >
                    <X size={14} strokeWidth={3} />
                  </button>
                )}
              </div>
            </header>

            <div className="p-8 w-full mx-auto">
              
              {/* OVERVIEW TAB */}
              {activeTab === 'overview' && (
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
              )}

              {/* VARIABLES TAB */}
              {activeTab === 'variables' && (
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
              )}

              {/* INTERACTIONS TAB */}
              {activeTab === 'interactions' && (
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
              )}

              {/* MISSING TAB */}
              {activeTab === 'missing' && (
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
              )}

              {/* CORRELATIONS TAB */}
              {activeTab === 'correlations' && (
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
              )}

              {/* DUPLICATES TAB */}
              {activeTab === 'duplicates' && (
                 <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-10 shadow-2xl animate-in zoom-in-95 duration-500`}>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                      <div>
                        <h2 className={`text-2xl font-bold mb-2 flex items-center gap-2 ${theme.textPrimary}`}>
                          <Layers className="text-blue-500" /> Duplicate Rows
                        </h2>
                        <p className={`${theme.textSub} text-sm`}>
                          Records that are exactly identical across all variables.
                        </p>
                      </div>
                    </div>
                    <div className={`py-12 text-center ${theme.textSub} border ${theme.borderAlt} border-dashed rounded-xl`}>
                      Duplicate data overview not available in current payload.
                    </div>
                 </div>
              )}

              {/* SAMPLE DATA TAB */}
              {activeTab === 'sample' && (
                 <div className={`${theme.bgCard} border ${theme.border} rounded-2xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-500`}>
                    <div className={`p-6 border-b ${theme.border} flex justify-between items-center ${theme.bgCardAlt}`}>
                      <h2 className={`text-xl font-bold flex items-center gap-2 ${theme.textPrimary}`}>
                        <Table className="text-blue-400" /> Sample Data Preview
                      </h2>
                      <span className={`text-xs font-mono ${theme.textSub} ${theme.bgMain} px-3 py-1.5 rounded-lg border ${theme.border}`}>
                        Showing top {sampleRows.length} rows
                      </span>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-[11px] leading-tight border-collapse">
                        <thead className={`${theme.bgMain}/80`}>
                          <tr>
                            {sampleRows.length > 0 && Object.keys(sampleRows[0]).map(k => (
                              <th key={k} className={`px-5 py-4 text-left font-bold uppercase tracking-wider ${theme.textMuted} whitespace-nowrap border-b ${theme.border}`}>
                                {k}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className={`divide-y ${theme.border}`}>
                          {sampleRows.map((row, i) => (
                            <tr key={i} className={`hover:${theme.bgCardAlt} transition-colors`}>
                              {Object.values(row).map((val, j) => {
                                const isMissing = val === 'null' || val === null || val === 'NaN' || val === 'nan' || (typeof val === 'number' && Number.isNaN(val));
                                return (
                                  <td key={j} className={`px-5 py-4 font-mono whitespace-nowrap ${isMissing ? 'text-red-400/80 italic font-bold' : theme.textSecondary} ${typeof val === 'string' && val.length > 40 ? 'max-w-[200px] truncate' : ''}`} title={String(val)}>
                                    {isMissing ? 'Null' : (typeof val === 'number' ? val.toLocaleString() : String(val))}
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                 </div>
              )}
            </div>

            <footer className={`mt-16 pb-8 text-center ${theme.textMuted} text-xs font-mono border-t ${theme.border} pt-8`}>
              Generated by ibis-profiling v{reportData.package?.version || 'dev'}
            </footer>
          </main>

          <div className={`lg:hidden fixed bottom-0 left-0 right-0 ${theme.bgSidebar} border-t ${theme.border} px-4 py-3 flex justify-around z-30 backdrop-blur-md`}>
             {navItems.map(item => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex flex-col items-center gap-1 transition-colors ${activeTab === item.id ? 'text-blue-500' : `${theme.textSub} hover:${theme.textPrimary}`}`}
                >
                  <Icon size={20} />
                  <span className="text-[9px] font-bold uppercase tracking-widest">{item.label}</span>
                </button>
              );
            })}
          </div>

        </div>
      );
    }

    function App() {
      const getInitialTheme = () => {
        const saved = localStorage.getItem('ibis-profiler-theme');
        return (saved && THEMES[saved]) ? THEMES[saved] : THEMES.dark;
      };

      const [theme, setThemeState] = useState(getInitialTheme);

      const setTheme = (t) => {
        setThemeState(t);
        localStorage.setItem('ibis-profiler-theme', t.id);
      };

      useEffect(() => {
        // Apply global background to body for smooth transitions
        document.body.className = theme.bgMain;
        // Also apply a data-theme attribute if needed for CSS
        document.documentElement.setAttribute('data-theme', theme.id);
      }, [theme]);

      return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
          <AppContent />
        </ThemeContext.Provider>
      );
    }

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  
