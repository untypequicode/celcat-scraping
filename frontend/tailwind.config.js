/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        // Serif éditorial pour les titres.
        serif: ['"Fraunces"', "ui-serif", "Georgia", "serif"],
        // Sans-serif neutre pour le corps de texte.
        sans: ['"Inter"', "ui-sans-serif", "system-ui", "sans-serif"],
        // Mono pour les éléments techniques (liens générés, labels).
        mono: ['"Space Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        // Fond clair cassé / fond sombre profond.
        paper: "#F6F4EF",
        graphite: "#120B08",
        // Texte / blocs pleins — brun profond de l'Université de Bordeaux.
        ink: "#3B1C13",
        // Gris secondaires (clair / sombre).
        mist: "#6E655F",
        smoke: "#9C9691",
        // Accent vif — bleu de l'Université de Bordeaux.
        signal: "#009DE0",
      },
    },
  },
  plugins: [],
};
