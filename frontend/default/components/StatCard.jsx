import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const StatCard = ({ title, value, icon: Icon, sub, color="blue" }) => {
  const { theme } = useContext(ThemeContext);
  return (
    <div className={`${theme.bgCard} border ${theme.border} p-5 rounded-2xl shadow-xl hover:shadow-${color}-900/10 transition-shadow`}>
      <div className="flex justify-between items-start mb-3">
        <span className={`${theme.textMuted} text-sm font-medium`}>{title}</span>
        <div className={`p-2 rounded-lg bg-${color}-500/10 text-${color}-400`}>
          <Icon size={18} />
        </div>
      </div>
      <div className={`text-2xl font-mono font-bold ${theme.textPrimary}`}>{value}</div>
      {sub && <div className={`text-xs ${theme.textSub} mt-1`}>{sub}</div>}
    </div>
  );
};
