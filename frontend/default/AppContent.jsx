import { REPORT_DATA } from "./data.js";
import { ThemeContext } from "./theme.js";
import {
  getInitialTab,
  generateAlertMessage,
  useReportViewModel,
} from "./reportViewModel.js";
import { ReportShell } from "./components/ReportShell.jsx";
import { OverviewSection } from "./components/OverviewSection.jsx";
import { VariablesSection } from "./components/VariablesSection.jsx";
import { InteractionsSection } from "./components/InteractionsSection.jsx";
import { MissingSection } from "./components/MissingSection.jsx";
import { CorrelationsSection } from "./components/CorrelationsSection.jsx";
import { DuplicatesSection } from "./components/DuplicatesSection.jsx";
import { SampleSection } from "./components/SampleSection.jsx";

const { useState, useEffect, useContext } = React;
const {
  BarChart3,
  Table,
  LayoutDashboard,
  PieChart,
  TrendingUp,
  FileWarning,
  Layers,
} = LucideReact;

export function AppContent() {
  const { theme, setTheme } = useContext(ThemeContext);
  const [reportData, setReportData] = useState(REPORT_DATA);
  const [activeTab, setActiveTab] = useState(getInitialTab);
  const [search, setSearch] = useState('');
  const [imgError, setImgError] = useState(false);
  const [interX, setInterX] = useState('');
  const [interY, setInterY] = useState('');
  const [corrType, setCorrType] = useState('');

  useEffect(() => {
    const handleHashChange = () => {
      setActiveTab(getInitialTab());
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const {
    interactionCols,
    interactionData,
    filteredVariables,
    sampleRows,
    getAlertsForVariable,
    currentCorrelationRaw,
    navItems,
  } = useReportViewModel({
    reportData,
    search,
    interX,
    interY,
    corrType,
    setInterX,
    setInterY,
    setCorrType,
    icons: {
      LayoutDashboard,
      BarChart3,
      TrendingUp,
      FileWarning,
      PieChart,
      Layers,
      Table,
    },
  });

  return (
    <ReportShell
      theme={theme}
      setTheme={setTheme}
      reportData={reportData}
      navItems={navItems}
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      search={search}
      setSearch={setSearch}
      imgError={imgError}
      setImgError={setImgError}
    >
      {activeTab === 'overview' && (
        <OverviewSection
          theme={theme}
          reportData={reportData}
          setActiveTab={setActiveTab}
          setSearch={setSearch}
          getAlertsForVariable={getAlertsForVariable}
          generateAlertMessage={generateAlertMessage}
        />
      )}

      {activeTab === 'variables' && (
        <VariablesSection
          theme={theme}
          reportData={reportData}
          filteredVariables={filteredVariables}
          getAlertsForVariable={getAlertsForVariable}
        />
      )}

      {activeTab === 'interactions' && (
        <InteractionsSection
          theme={theme}
          reportData={reportData}
          interX={interX}
          setInterX={setInterX}
          interY={interY}
          setInterY={setInterY}
          interactionCols={interactionCols}
          interactionData={interactionData}
        />
      )}

      {activeTab === 'missing' && <MissingSection theme={theme} reportData={reportData} />}

      {activeTab === 'correlations' && (
        <CorrelationsSection
          theme={theme}
          reportData={reportData}
          corrType={corrType}
          setCorrType={setCorrType}
          currentCorrelationRaw={currentCorrelationRaw}
        />
      )}

      {activeTab === 'duplicates' && <DuplicatesSection theme={theme} />}

      {activeTab === 'sample' && (
        <SampleSection theme={theme} reportData={reportData} sampleRows={sampleRows} />
      )}
    </ReportShell>
  );
}
