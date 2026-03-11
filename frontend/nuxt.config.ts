export default defineNuxtConfig({
  css: ["@/assets/main.css"],
  app: {
    head: {
      title: "Proximeet",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "description", content: "Organisez vos déjeuners avec vos collègues consultants" },
        { name: "theme-color", content: "#3b82f6" },
        { name: "apple-mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" },
        { name: "apple-mobile-web-app-title", content: "Proximeet" }
      ],
      link: [
        { rel: "manifest", href: "/manifest.json" },
        { rel: "apple-touch-icon", href: "/icons/icon-192x192.png" }
      ]
    }
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
      msalClientId: process.env.NUXT_PUBLIC_MSAL_CLIENT_ID || "",
      msalTenantId: process.env.NUXT_PUBLIC_MSAL_TENANT_ID || "common",
      msalRedirectUri: process.env.NUXT_PUBLIC_MSAL_REDIRECT_URI || "http://localhost:3000",
      msalScopes: (process.env.NUXT_PUBLIC_MSAL_SCOPES || "User.Read").split(",")
    }
  }
});
