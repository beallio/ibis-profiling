const { Table } = LucideReact;

export function SampleSection({ theme, reportData, sampleRows }) {
  return (
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
  );
}
