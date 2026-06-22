import { THEMES } from "./constants.js";
import { ThemeContext } from "./theme.js";
import { AppContent } from "./AppContent.jsx";

const { useState, useEffect } = React;

export function App() {
  const getInitialTheme = () => {
    const saved = localStorage.getItem('ibis-profiler-theme');
    return (saved && THEMES[saved]) ? THEMES[saved] : THEMES.dark;
  };

  const [theme, setThemeState] = useState(getInitialTheme);

  const setTheme = (t) => {
    setThemeState(t);
    localStorage.setItem('ibis-profiler-theme', t.id);
  };

  useEffect(() => {
    // Apply global background to body for smooth transitions
    document.body.className = theme.bgMain;
    // Also apply a data-theme attribute if needed for CSS
    document.documentElement.setAttribute('data-theme', theme.id);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <AppContent />
    </ThemeContext.Provider>
  );
}
