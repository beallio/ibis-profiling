// Helper: Safely parse different matrix JSON structures
export const parseMatrixData = (data) => {
  if (!data) return { columns: [], matrix: [] };
  
  // 1) Handle { matrix: [ {col1: v1, ...}, ... ] } - new standard
  if (data.matrix && Array.isArray(data.matrix) && data.matrix.length > 0 && typeof data.matrix[0] === 'object' && !Array.isArray(data.matrix[0])) {
      const columns = Object.keys(data.matrix[0]);
      const matrix = data.matrix.map(row => columns.map(col => row[col]));
      return { columns, matrix };
  }

  // 2) If it's already an array, parse it as array-of-objects
  if (Array.isArray(data)) {
    if (data.length === 0) return { columns: [], matrix: [] };
    const columns = Object.keys(data[0]);
    const matrix = data.map(row => columns.map(col => row[col]));
    return { columns, matrix };
  }

  // 3) Handle { columns, matrix } or { columns, values } standard shapes
  if (data.columns) {
    if (data.matrix) return { columns: data.columns, matrix: data.matrix };
    if (data.values) return { columns: data.columns, matrix: data.values };
  }
  
  return { columns: [], matrix: [] };
};

// Filter helper to remove None/Null/NaN bins from histogram charts
export const filterMissingBins = (bins, counts) => {
  if (!bins || !counts || !Array.isArray(bins) || !Array.isArray(counts)) {
    return { filteredBins: bins || [], filteredCounts: counts || [] };
  }
  const missingLabels = ['none', 'null', 'nan', 'undefined', ''];
  const filteredBins = [];
  const filteredCounts = [];
  for (let i = 0; i < bins.length; i++) {
    const binVal = bins[i];
    if (binVal === null || binVal === undefined) continue;
    
    let binStr = "";
    try {
      binStr = String(binVal).toLowerCase().trim();
    } catch (e) {
      binStr = "";
    }
    
    // Don't filter out range labels like "[10.0, 20.0]"
    if (!missingLabels.includes(binStr)) {
      filteredBins.push(binVal);
      filteredCounts.push(counts[i]);
    }
  }
  return { filteredBins, filteredCounts };
};

export const hasValidMetrics = (metrics) => {
  return metrics.some(m => m.val !== undefined && m.val !== null && m.val !== 'null' && m.val !== 'N/A' && !(typeof m.val === 'number' && Number.isNaN(m.val)));
};
