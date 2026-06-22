import { ALERT_CONFIG } from "../constants.js";
import { ThemeContext } from "../theme.js";

const { useContext } = React;

export const AlertBadge = ({ alert }) => {
  const { theme } = useContext(ThemeContext);
  const config = ALERT_CONFIG[alert.alert_type] || ALERT_CONFIG.DEFAULT;
  const Icon = config.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${config.color} ${config.bg} ${config.border}`} title={alert.message}>
      <Icon size={12} />
      {alert.alert_type}
    </span>
  );
};
