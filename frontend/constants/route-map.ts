export const routeMap = {
  HOME: "/",
  TERMS_OF_SERVICE: "/terms-of-service/",
  PRIVACY_POLICY: "/privacy-policy/",
  COOKIE_POLICY: "/cookie-policy/",
  PRICING: "/pricing/",
  DOCS: {
    HOME: "/docs/",
    INSTALLATION: "/docs/installation/",
    NOTIFICATIONS: "/docs/notifications/",
    CUSTOMIZATION: "/docs/customization/",
    TROUBLESHOOTING: "/docs/troubleshooting/",
    CUSTOM_WEBHOOK: "/docs/custom-webhook/",
    AUTO_CROSSPOST: "/docs/auto-crosspost/",
  },
  REDIRECTS: {
    INVITE: "/invite/",
    SUPPORT_SERVER: "/support-server/",
  },
  AUTH: {
    LOGIN: "/login/",
    LOGIN_CALLBACK: "/login/callback/",
    LOGOUT: "/logout/",
  },
  DASHBOARD: {
    HOME: "/dashboard/",
    SERVER_PATH: "/dashboard/server/",
    SERVER: (id: string) => `/dashboard/server/?id=${id}`,
  },
};

export default routeMap;
