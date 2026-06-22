import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const MetricRow = ({ label, val, isPercent = false }) => {
  const { theme } = useContext(ThemeContext);
  if (val === undefined || val === null || val === 'null' || val === 'N/A' || (typeof val === 'number' && Number.isNaN(val))) return null;
  
  let formattedVal = val;
  if (isPercent && typeof val === 'number') {
    formattedVal = `${(val * 100).toFixed(2)}%`;
  } else if (typeof val === 'number') {
    if (val !== 0 && Math.abs(val) < 0.001) {
      formattedVal = val.toExponential(3);
    } else {
      formattedVal = val.toLocaleString(undefined, { maximumFractionDigits: 4 });
    }
  } else if (typeof val === 'boolean') {
    formattedVal = val ? 'True' : 'False';
  } else if (val === 'Skipped') {
    formattedVal = 'Skipped';
  }

  return (
    <div className={`flex justify-between items-center py-1.5 border-b ${theme.borderAlt} last:border-0 hover:bg-slate-800/20 transition-all duration-200 px-1 rounded`}>
      <span className={`text-xs ${theme.textMuted}`}>{label}</span>
      <span className={`text-xs font-mono font-bold ${theme.textSecondary}`}>
        {String(formattedVal)}
      </span>
    </div>
  );
};
