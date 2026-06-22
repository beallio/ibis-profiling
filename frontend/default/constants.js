const {
  Moon,
  Sun,
  Contrast,
  Fingerprint,
  Lock,
  Copy,
  FileWarning,
  Info
} = LucideReact;

export const THEMES = {
  dark: {
    id: 'dark',
    name: 'Dark',
    icon: Moon,
    bgMain: 'bg-slate-950',
    bgSidebar: 'bg-slate-900/50',
    bgCard: 'bg-slate-900',
    bgCardAlt: 'bg-slate-800/20',
    bgHeader: 'bg-slate-950/80',
    bgInput: 'bg-slate-900',
    border: 'border-slate-800',
    borderAlt: 'border-slate-800/50',
    textPrimary: 'text-slate-100',
    textSecondary: 'text-slate-200',
    textMuted: 'text-slate-400',
    textSub: 'text-slate-500',
    accent: 'blue'
  },
  light: {
    id: 'light',
    name: 'Light',
    icon: Sun,
    bgMain: 'bg-slate-50',
    bgSidebar: 'bg-slate-100/80',
    bgCard: 'bg-white',
    bgCardAlt: 'bg-slate-100/50',
    bgHeader: 'bg-white/80',
    bgInput: 'bg-white',
    border: 'border-slate-200',
    borderAlt: 'border-slate-100',
    textPrimary: 'text-slate-900',
    textSecondary: 'text-slate-800',
    textMuted: 'text-slate-600',
    textSub: 'text-slate-500',
    accent: 'blue'
  },
  contrast: {
    id: 'contrast',
    name: 'High Contrast',
    icon: Contrast,
    bgMain: 'bg-black',
    bgSidebar: 'bg-zinc-900',
    bgCard: 'bg-zinc-900',
    bgCardAlt: 'bg-zinc-800',
    bgHeader: 'bg-black/90',
    bgInput: 'bg-zinc-900',
    border: 'border-zinc-700',
    borderAlt: 'border-zinc-700',
    textPrimary: 'text-white',
    textSecondary: 'text-zinc-100',
    textMuted: 'text-zinc-300',
    textSub: 'text-zinc-400',
    accent: 'blue'
  }
};

// Alert configuration for distinct styling
export const ALERT_CONFIG = {
  UNIQUE: { icon: Fingerprint, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
  CONSTANT: { icon: Lock, color: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/20' },
  HIGH_CARDINALITY: { icon: Copy, color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
  MISSING: { icon: FileWarning, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
  DEFAULT: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' }
};

export const TYPE_LABELS = {
  Numeric: 'Num',
  Categorical: 'Cat',
  Boolean: 'Bool',
  DateTime: 'Date',
  Email: 'Email',
  URL: 'URL',
  IPAddress: 'IP',
  PhoneNumber: 'Phone',
  UUID: 'UUID',
  Integer: 'Int',
  Decimal: 'Dec',
  Ordinal: 'Ord',
  Count: 'Count',
  Unsupported: 'Other'
};
