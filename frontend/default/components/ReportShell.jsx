import { THEMES } from "../constants.js";

const { Database, Search, Clock, X, Sun } = LucideReact;

export function ReportShell({
  theme,
  setTheme,
  reportData,
  navItems,
  activeTab,
  setActiveTab,
  search,
  setSearch,
  imgError,
  setImgError,
  children,
}) {
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
              {children}
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
