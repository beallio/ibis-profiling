import { formatBytes, formatPct, formatNum, getAlertColor } from "../helpers.js";
import { StatRow } from "./StatRow.jsx";

const { Info, AlertTriangle } = LucideReact;

export const OverviewSection = ({ data }) => {
  const table = data.table;
  const types = Object.entries(table.types || {});

  return (
    <div id="overview" className="space-y-2 animate-fadeIn section-top">
      <div className="flex items-center gap-2 mb-4">
        <Info size={24} className="text-slate-600" />
        <h2 className="text-2xl font-bold text-gray-800">Overview</h2>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="bg-white rounded-md shadow-sm border border-gray-200 p-3 flex flex-col lg:col-span-6">
          <h3 className="text-sm font-semibold text-gray-700 border-b border-gray-100 pb-1 mb-2 uppercase tracking-wider">Dataset statistics</h3>
          <div className="grid grid-cols-1 gap-0 flex-1">
            <StatRow label="Number of variables" value={formatNum(table.n_var)} compact={true} />
            <StatRow label="Number of observations" value={formatNum(table.n)} compact={true} />
            <StatRow label="Missing cells" value={formatNum(table.n_cells_missing)} compact={true} />
            <StatRow label="Missing cells (%)" value={formatPct(table.p_cells_missing)} compact={true} />
            <StatRow label="Empty cells" value={formatNum(table.n_cells_empty)} compact={true} />
            <StatRow label="Empty cells (%)" value={formatPct(table.p_cells_empty)} compact={true} />
            <StatRow label="Variables with missing values" value={formatNum(table.n_vars_with_missing)} compact={true} />
            <StatRow label="Variables with empty values" value={formatNum(table.n_vars_with_empty)} compact={true} />
            <StatRow label="Variables with all missing values" value={formatNum(table.n_vars_all_missing)} compact={true} />
            {table.n_vars_constant !== undefined && (
              <StatRow label="Constant variables" value={formatNum(table.n_vars_constant)} compact={true} />
            )}
            {table.n_duplicates !== undefined && (
              <>
                <StatRow label="Duplicate rows" value={formatNum(table.n_duplicates)} compact={true} />
                <StatRow label="Duplicate rows (%)" value={formatPct(table.p_duplicates)} compact={true} />
              </>
            )}
            <StatRow label="Total size in memory" value={formatBytes(table.memory_size)} compact={true} />
            <StatRow label="Average record size in memory" value={`${formatNum(table.record_size)} B`} compact={true} />
          </div>
        </div>

        <div className="bg-white rounded-md shadow-sm border border-gray-200 p-3 flex flex-col lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-700 border-b border-gray-100 pb-1 mb-2 uppercase tracking-wider">Variable types</h3>
          <div className="grid grid-cols-1 gap-0 flex-1">
            {types.length > 0 ? types.map(([type, count]) => (
              <StatRow key={type} label={type} value={count} compact={true} />
            )) : (
              <span className="text-gray-400 text-sm italic">No type data available.</span>
            )}
          </div>
        </div>

        {data.alerts && data.alerts.length > 0 ? (
          <div className="bg-white rounded-md shadow-sm border border-gray-200 flex flex-col overflow-hidden lg:col-span-4">
            <div className="bg-gray-50 p-2 border-b border-gray-200 flex items-center shrink-0">
              <AlertTriangle size={16} className="text-yellow-500 mr-2" />
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Alerts</h3>
            </div>
            <div className="p-0 overflow-y-auto max-h-[300px] flex-1">
              <ul className="divide-y divide-gray-100">
                {data.alerts.map((alert, idx) => {
                  return (
                    <li key={idx} className="p-2 hover:bg-gray-50 transition-colors flex items-start gap-3 text-xs">
                      <span className={`
                        inline-block px-1.5 py-0.5 text-[10px] rounded border font-medium whitespace-nowrap mt-0.5
                        ${getAlertColor(alert.alert_type)}
                      `}>
                        {alert.alert_type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-gray-700">
                        <strong>{alert.fields.join(', ')}</strong> has a {alert.alert_type.toLowerCase().replace(/_/g, ' ')} condition
                        {alert.value !== undefined ? ` (${typeof alert.value === 'number' && alert.value < 1 ? formatPct(alert.value) : formatNum(alert.value)})` : ''}.
                      </span>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-md shadow-sm border border-gray-200 p-3 flex items-center justify-center lg:col-span-4 text-gray-400 italic text-sm">
            No alerts detected.
          </div>
        )}
      </div>
    </div>
  );
};
