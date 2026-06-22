const { Hash, AlignLeft, ToggleLeft, Database } = LucideReact;

export const TypeIcon = ({ type }) => {
  switch (type) {
    case 'Numeric': return <Hash size={16} className="text-blue-500" />;
    case 'Categorical': return <AlignLeft size={16} className="text-blue-500" />;
    case 'Boolean': return <ToggleLeft size={16} className="text-blue-500" />;
    default: return <Database size={16} className="text-blue-500" />;
  }
};
