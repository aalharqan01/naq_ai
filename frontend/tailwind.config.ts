import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Qatar Official Brand Colors (gba.gco.gov.qa)
        adaam: {
          DEFAULT: "#8A1538",
          light: "#B91E4A",
          dark: "#5C0E26",
          50: "#FDF2F5",
          100: "#FCE4EA",
          200: "#F9C9D5",
          300: "#F3A0B5",
          400: "#E76B8A",
          500: "#D43D64",
          600: "#B91E4A",
          700: "#8A1538",
          800: "#6B1030",
          900: "#4D0C22",
        },
        gold: {
          DEFAULT: "#E9C56B",
          light: "#F2D98A",
          dark: "#C4A455",
          muted: "#A29475",
          50: "#FDF9EE",
          100: "#FBF2D4",
          200: "#F5E2A5",
          300: "#F0D07A",
          400: "#E9C56B",
          500: "#D4AD4E",
          600: "#B8923A",
          700: "#97742F",
          800: "#7A5E2A",
          900: "#644D25",
        },
        dune: {
          DEFAULT: "#A29475",
          light: "#BFB29A",
          dark: "#7A6E58",
        },
        // Dark theme surfaces
        surface: {
          DEFAULT: "#0A0A0F",
          raised: "#121218",
          card: "#1A1A24",
          glass: "#1E1E2A",
          overlay: "#252535",
        },
        // Heritage accent colors
        skyline: "#0D4261",
        palm: "#129B82",
        sea: "#4194B3",
        sunrise: "#FDF39D",
        // Text colors
        warm: {
          white: "#F5F0E8",
          muted: "#A29475",
          dim: "#6B6B7B",
        },
      },
      fontFamily: {
        arabic: ["Cairo", "Noto Kufi Arabic", "Tahoma", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Amiri", "Georgia", "serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "hero-gradient": "linear-gradient(135deg, #0A0A0F 0%, #1A1A24 40%, #0D4261 100%)",
        "maroon-gradient": "linear-gradient(135deg, #8A1538 0%, #5C0E26 100%)",
        "gold-shimmer": "linear-gradient(90deg, transparent 0%, rgba(233,197,107,0.1) 50%, transparent 100%)",
      },
      animation: {
        "fade-in": "fadeIn 0.6s ease-out forwards",
        "fade-up": "fadeUp 0.6s ease-out forwards",
        "slide-in-right": "slideInRight 0.4s ease-out forwards",
        "slide-in-left": "slideInLeft 0.4s ease-out forwards",
        "glow-pulse": "glowPulse 3s ease-in-out infinite",
        "pattern-drift": "patternDrift 60s linear infinite",
        "shimmer": "shimmer 2s linear infinite",
        "typing-bounce": "typingBounce 1.4s infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideInLeft: {
          "0%": { opacity: "0", transform: "translateX(-20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(233,197,107,0.1)" },
          "50%": { boxShadow: "0 0 40px rgba(233,197,107,0.2)" },
        },
        patternDrift: {
          "0%": { transform: "translate(0, 0) rotate(0deg)" },
          "100%": { transform: "translate(40px, 40px) rotate(3deg)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        typingBounce: {
          "0%, 60%, 100%": { opacity: "0.3", transform: "scale(0.8)" },
          "30%": { opacity: "1", transform: "scale(1)" },
        },
      },
      boxShadow: {
        "gold-sm": "0 0 10px rgba(233,197,107,0.1)",
        "gold-md": "0 0 20px rgba(233,197,107,0.15)",
        "gold-lg": "0 0 40px rgba(233,197,107,0.2)",
        "maroon-sm": "0 0 10px rgba(138,21,56,0.15)",
        "maroon-md": "0 0 20px rgba(138,21,56,0.2)",
        "glass": "0 8px 32px rgba(0,0,0,0.3)",
        "card": "0 4px 24px rgba(0,0,0,0.2)",
      },
    },
  },
  plugins: [],
};

export default config;
