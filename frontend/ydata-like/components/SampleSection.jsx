const { AlignLeft } = LucideReact;

export const SampleSection = ({ data }) => {
  const sampleData = data.sample?.head || data.sample;
  if (!sampleData || (Array.isArray(sampleData) && sampleData.length === 0)) return null;
  
  let columns = [];
  let rows = [];
  
  if (Array.isArray(sampleData)) {
    columns = Object.keys(sampleData[0]);
    rows = sampleData;
  } else {
    columns = Object.keys(sampleData);
    const numRows = sampleData[columns[0]].length;
    rows = Array.from({ length: numRows }).map((_, i) => {
      const row = {};
      columns.forEach(col => {
        row[col] = sampleData[col][i];
      });
      return row;
    });
  }

  return (
    <div id="sample" className="space-y-4 animate-fadeIn section">
      <div className="flex items-center gap-2 mb-4">
        <AlignLeft size={24} className="text-slate-600" />
        <h2 className="text-2xl font-bold text-gray-800">Sample</h2>
      </div>
      <div className="bg-white rounded-md shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-800">First rows</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                {columns.map(col => (
                  <th key={col} className="py-3 px-4 bg-gray-100 font-semibold text-sm text-gray-700 border-b border-gray-200 border-r last:border-r-0 whitespace-nowrap">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50 border-b border-gray-100 last:border-0">
                  {columns.map(col => {
                    const val = row[col];
                    const isNull = val === null || val === 'NaN' || (typeof val === 'number' && Number.isNaN(val));
                    return (
                      <td key={col} className={`py-2.5 px-4 text-sm border-r border-gray-100 last:border-r-0 font-mono ${isNull ? 'text-red-400 italic' : 'text-gray-600'}`}>
                        {isNull ? 'Null' : String(val)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
