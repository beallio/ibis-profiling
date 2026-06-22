import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const ExtremeValuesList = ({ title, values }) => {
  const { theme } = useContext(ThemeContext);
  if (!values || values.length === 0) return null;
  return (
    <div className="flex-1">
      <h5 className={`text-[10px] font-bold ${theme.textSub} uppercase tracking-widest mb-3`}>{title}</h5>
      <div className="space-y-1.5">
        {values.map((v, i) => (
          <div key={i} className={`flex items-center gap-2 text-xs ${theme.bgCardAlt} px-2 py-1.5 rounded border ${theme.border}`}>
            <span className="text-slate-600 font-mono w-4">{i+1}.</span>
            <span className={`${theme.textSecondary} font-mono truncate`} title={String(v)}>{String(v)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
