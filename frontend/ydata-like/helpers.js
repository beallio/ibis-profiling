// --- FORMATTING HELPERS ---
export const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export const formatPct = (val) => {
  if (val === undefined || val === null) return '0.0%';
  return (val * 100).toFixed(1) + '%';
};

export const formatNum = (val) => {
  if (val === undefined || val === null) return '-';
  return typeof val === 'number' ? (Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2)) : val;
};

// Helper: Safely parse different matrix JSON structures
export const parseMatrixData = (data) => {
  if (!data) return { columns: [], matrix: [] };
  
  // 1) Handle { matrix: [ {col1: v1, ...}, ... ] } - new standard
  if (data.matrix && Array.isArray(data.matrix) && data.matrix.length > 0 && typeof data.matrix[0] === 'object' && !Array.isArray(data.matrix[0])) {
      const columns = Object.keys(data.matrix[0]);
      const matrix = data.matrix.map(row => columns.map(col => row[col]));
      return { columns, matrix };
  }

  // 2) Handle array of objects format (e.g. from missing heatmap or correlations)
  if (Array.isArray(data)) {
    if (data.length === 0) return { columns: [], matrix: [] };
    const columns = Object.keys(data[0]);
    const matrix = data.map(row => columns.map(col => row[col]));
    return { columns, matrix };
  }
  
  // 3) Standard { columns, matrix } or { columns, values }
  if (data.columns) {
    if (data.matrix) return { columns: data.columns, matrix: data.matrix };
    if (data.values) return { columns: data.columns, matrix: data.values };
  }
  
  return { columns: [], matrix: [] };
};

export const getAlertColor = (type) => {
  const colors = {
    'CONSTANT': 'bg-gray-100 text-gray-800 border-gray-200',
    'ZEROS': 'bg-orange-100 text-orange-800 border-orange-200',
    'HIGH_CARDINALITY': 'bg-purple-100 text-purple-800 border-purple-200',
    'SKEWED': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'MISSING': 'bg-red-100 text-red-800 border-red-200',
    'UNIQUE': 'bg-blue-100 text-blue-800 border-blue-200',
    'REJECTED': 'bg-slate-200 text-slate-900 border-slate-300'
  };
  return colors[type] || 'bg-blue-100 text-blue-800 border-blue-200';
};
