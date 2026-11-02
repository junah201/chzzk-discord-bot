import type { MetadataRoute } from "next";
import { SITE_URL } from "@/constants/links";
import routeMap from "@/constants/route-map";

export const dynamic = "force-static";

const PUBLIC_PATHS = [
  routeMap.HOME,
  routeMap.PRICING,
  routeMap.DOCS.INSTALLATION,
  routeMap.DOCS.NOTIFICATIONS,
  routeMap.DOCS.CUSTOMIZATION,
  routeMap.DOCS.CUSTOM_WEBHOOK,
  routeMap.DOCS.TROUBLESHOOTING,
  routeMap.TERMS_OF_SERVICE,
  routeMap.PRIVACY_POLICY,
  routeMap.COOKIE_POLICY,
];

export default function sitemap(): MetadataRoute.Sitemap {
  return PUBLIC_PATHS.map((path) => ({ url: `${SITE_URL}${path}` }));
}
