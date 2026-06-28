const { useMemo, useEffect } = React;

export function getInitialTab() {
  const hash = window.location.hash.slice(1);
  const validTabs = ['overview', 'variables', 'interactions', 'correlations', 'missing', 'alerts', 'sample'];
  return validTabs.includes(hash) ? hash : 'overview';
}

export function generateAlertMessage(alert) {
  if (alert.message) return alert.message;
  const fieldStr = alert.fields.join(', ');
  switch (alert.alert_type) {
    case 'UNIQUE': return `${fieldStr} contains entirely unique values.`;
    case 'CONSTANT': return `${fieldStr} has a constant value across all rows.`;
    case 'HIGH_CARDINALITY': return `${fieldStr} has high cardinality (${alert.value?.toLocaleString() || 'many'} distinct values).`;
    case 'MISSING': return `${fieldStr} has missing values.`;
    default: return `${fieldStr} triggered a ${alert.alert_type} alert.`;
  }
}

export function useReportViewModel({
  reportData,
  search,
  interX,
  interY,
  corrType,
  setInterX,
  setInterY,
  setCorrType,
  icons,
}) {
  const numericCols = useMemo(() => {
    return Object.entries(reportData.variables)
      .filter(([_, meta]) => meta.type === 'Numeric')
      .map(([name]) => name);
  }, [reportData]);

  const interactionCols = useMemo(() => {
    if (!reportData.interactions) return [];
    return Object.keys(reportData.interactions).filter(k => k !== '_metadata').sort();
  }, [reportData]);

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

  const defaultCorrType = useMemo(() => {
    if (!reportData.correlations) return '';
    const keys = Object.keys(reportData.correlations).filter(k => k !== '_metadata');
    return keys[0] || '';
  }, [reportData.correlations]);

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

  const getAlertsForVariable = (varName) => {
    return reportData.alerts?.filter(a => a.fields.includes(varName)) || [];
  };

  const currentCorrelationRaw = corrType ? reportData.correlations?.[corrType] : null;

  const navItems = [
    { id: 'overview', label: 'Overview', icon: icons.LayoutDashboard },
    { id: 'variables', label: 'Variables', icon: icons.BarChart3 }
  ];

  const hasInteractions = reportData.interactions && Object.keys(reportData.interactions).length > 0;
  if (hasInteractions) {
    navItems.push({ id: 'interactions', label: 'Interactions', icon: icons.TrendingUp });
  }

  const hasMissing = reportData.missing && Object.keys(reportData.missing).length > 0;
  if (hasMissing) {
    navItems.push({ id: 'missing', label: 'Missing', icon: icons.FileWarning });
  }

  const hasCorrelations = reportData.correlations && Object.keys(reportData.correlations).length > 0;
  if (hasCorrelations) {
    navItems.push({ id: 'correlations', label: 'Correlations', icon: icons.PieChart });
  }

  const hasDuplicates = reportData.duplicates && Object.keys(reportData.duplicates).length > 0;
  if (hasDuplicates) {
    navItems.push({ id: 'duplicates', label: 'Duplicates', icon: icons.Layers });
  }

  if (reportData.sample && reportData.sample.head && Object.keys(reportData.sample.head).length > 0) {
    navItems.push({ id: 'sample', label: 'Sample Data', icon: icons.Table });
  }

  return {
    interactionCols,
    interactionData,
    filteredVariables,
    sampleRows,
    getAlertsForVariable,
    currentCorrelationRaw,
    navItems,
  };
}
