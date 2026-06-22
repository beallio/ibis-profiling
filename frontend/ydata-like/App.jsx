import { REPORT_DATA } from "./data.js";
import { OverviewSection } from "./components/OverviewSection.jsx";
import { VariableCard } from "./components/VariableCard.jsx";
import { CorrelationsSection } from "./components/CorrelationsSection.jsx";
import { InteractionsSection } from "./components/InteractionsSection.jsx";
import { MissingValuesSection } from "./components/MissingValuesSection.jsx";
import { SampleSection } from "./components/SampleSection.jsx";

const { useState } = React;
const { AlertTriangle, Info, Hash, PieChart, ScatterChart, AlignLeft, BarChart2 } = LucideReact;

export function App() {
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
