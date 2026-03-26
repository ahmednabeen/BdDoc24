    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            // Using System Fonts (No Google Fonts)
            display: ['ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            body: ['ui-sans-serif', 'system-ui', 'sans-serif'],
          },
          colors: {
            // Brand Colors
            primary: { DEFAULT: '#1d4ed8', 50: '#eff6ff', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a' },
            accent: { DEFAULT: '#0ea5e9', light: '#e0f2fe' },
            emerald: { DEFAULT: '#047857', 600: '#059669', 700: '#047857' },
            
            // Semantic Colors
            bg: '#f8fafc',         // Slate 50
            fg: '#0f172a',         // Slate 900
            muted: '#64748b',      // Slate 500
            card: '#ffffff',       // White
            border: '#e2e8f0',     // Slate 200
            // Changed CTA Button Color to Emerald (Green)
            bccent: '#059669',     
          }
        }
      }
    }
