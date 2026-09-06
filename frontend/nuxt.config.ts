// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss"],
  css: ["~/assets/css/main.css"],
  app: {
    head: {
      htmlAttrs: { lang: "fr" },
      meta: [
        { name: "color-scheme", content: "light dark" },
        {
          name: "theme-color",
          content: "#F6F4EF",
          media: "(prefers-color-scheme: light)",
        },
        {
          name: "theme-color",
          content: "#120B08",
          media: "(prefers-color-scheme: dark)",
        },
        { name: "format-detection", content: "telephone=no" },
      ],
      link: [
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        {
          rel: "preconnect",
          href: "https://fonts.gstatic.com",
          crossorigin: "",
        },
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,500;0,600;0,700;0,900;1,500;1,600&family=Inter:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap",
        },
        // Icônes : favicon.ico (racine, détecté automatiquement par les
        // navigateurs) + version vectorielle + icône iOS + manifest PWA.
        { rel: "icon", href: "/favicon.ico", sizes: "48x48" },
        { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
        {
          rel: "apple-touch-icon",
          sizes: "180x180",
          href: "/apple-touch-icon.png",
        },
        { rel: "manifest", href: "/site.webmanifest" },
      ],
      script: [
        {
          // Applique le thème avant l'hydratation pour éviter le flash
          // clair/sombre (FOUC). Respecte un choix manuel stocké, sinon
          // suit la préférence système (prefers-color-scheme).
          innerHTML: `(function () {
            try {
              var stored = localStorage.getItem('color-scheme');
              var dark = stored ? stored === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
              document.documentElement.classList.toggle('dark', dark);
            } catch (e) {}
          })();`,
          tagPosition: "head",
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      // URL de base de l'API backend (celcat-to-ics). Surchargeable via
      // la variable d'environnement NUXT_PUBLIC_API_BASE_URL.
      apiBaseUrl: "http://localhost:8000",
      // URL publique du site, utilisée pour les balises canoniques et
      // Open Graph/Twitter (URLs absolues requises par ces standards).
      // Laisser vide pour une détection automatique depuis la requête
      // entrante ; surchargeable via NUXT_PUBLIC_SITE_URL en production.
      siteUrl: "",
    },
  },
});
