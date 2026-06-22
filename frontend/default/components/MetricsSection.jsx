import { ThemeContext } from "../theme.js";
import { MetricRow } from "./MetricRow.jsx";

const { useContext } = React;

export const MetricsSection = ({ title, metrics }) => {
  const { theme } = useContext(ThemeContext);
  const validMetrics = metrics.filter(m => m.val !== undefined && m.val !== null && m.val !== 'null' && m.val !== 'N/A' && !(typeof m.val === 'number' && Number.isNaN(m.val)));
  if (validMetrics.length === 0) return null;

  return (
    <div>
      <h5 className={`text-[10px] font-bold ${theme.textMuted} uppercase tracking-widest mb-3`}>{title}</h5>
      <div>
        {validMetrics.map((m, i) => (
          <MetricRow key={i} label={m.label} val={m.val} isPercent={m.isPercent} />
        ))}
      </div>
    </div>
  );
};
