"use client";

import { useState } from "react";
import { Globe, Menu, X } from "lucide-react";

interface HeaderProps {
  language: "en" | "ar";
  onLanguageToggle: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: "chat", labelEn: "Heritage Explorer", labelAr: "مستكشف التراث" },
  { id: "archive", labelEn: "Archive", labelAr: "الأرشيف" },
  { id: "upload", labelEn: "Upload", labelAr: "رفع" },
];

export default function Header({
  language,
  onLanguageToggle,
  activeTab,
  onTabChange,
}: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const isAr = language === "ar";

  return (
    <header className="sticky top-0 z-50 border-b border-white/5" style={{
      background: "rgba(10, 10, 15, 0.8)",
      backdropFilter: "blur(20px)",
      WebkitBackdropFilter: "blur(20px)",
    }}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-adaam/20 flex items-center justify-center border border-adaam/30 animate-glow-pulse">
                <span className="text-shimmer font-display font-bold text-xl">
                  {isAr ? "ذ" : "D"}
                </span>
              </div>
              <div className="absolute -inset-1 rounded-xl bg-adaam/10 blur-sm -z-10" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wide text-warm-white font-arabic">
                {isAr ? "ذاكرة" : "Dhakira"}
              </h1>
              <p className="text-[10px] uppercase tracking-[0.2em] text-gold-muted hidden sm:block">
                {isAr ? "الأرشيف الوطني لدولة قطر" : "National Archives of Qatar"}
              </p>
            </div>
          </div>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center">
            <div className="flex items-center gap-1 glass-panel rounded-xl p-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`px-5 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                    activeTab === tab.id
                      ? "bg-adaam text-warm-white shadow-maroon-sm"
                      : "text-warm-muted hover:text-warm-white hover:bg-white/5"
                  }`}
                >
                  {isAr ? tab.labelAr : tab.labelEn}
                </button>
              ))}
            </div>
          </nav>

          <div className="flex items-center gap-3">
            {/* Language toggle */}
            <button
              onClick={onLanguageToggle}
              className="btn-ghost flex items-center gap-2 px-3 py-2 text-sm"
              title="Switch language"
            >
              <Globe className="w-4 h-4 text-gold" />
              <span className="font-arabic">{isAr ? "English" : "عربي"}</span>
            </button>

            {/* Mobile menu */}
            <button
              className="md:hidden p-2 text-warm-muted hover:text-warm-white transition-colors"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile nav */}
        {menuOpen && (
          <nav className="md:hidden pb-4">
            <div className="gold-line mb-3" />
            <div className="flex flex-col gap-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => { onTabChange(tab.id); setMenuOpen(false); }}
                  className={`px-4 py-3 rounded-xl text-sm font-medium text-start transition-all duration-300 ${
                    activeTab === tab.id
                      ? "bg-adaam/20 text-gold border border-adaam/30"
                      : "text-warm-muted hover:text-warm-white hover:bg-white/5"
                  }`}
                >
                  {isAr ? tab.labelAr : tab.labelEn}
                </button>
              ))}
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
