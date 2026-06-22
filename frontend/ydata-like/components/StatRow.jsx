export const StatRow = ({ label, value, subValue = null, alert = false, compact = false }) => (
  <div className={`flex justify-between ${compact ? 'py-0' : 'py-1.5'} ${compact ? '' : 'border-b border-gray-100'} last:border-0 text-sm`}>
    <span className="text-gray-600">{label}</span>
    <div className="text-right">
      <span className={`font-medium ${alert ? 'text-red-600' : 'text-gray-800'}`}>{value}</span>
      {subValue && <span className="text-gray-400 text-xs ml-2">{subValue}</span>}
    </div>
  </div>
);
