/**
 * Vercel Edge Middleware - Protocolo Bloqueo V10 (LICENSE_PAID).
 * Proyecto: Vite SPA + Python /api; sin Next.js. Si el runtime no ejecuta este
 * archivo, el bloqueo sigue activo via `main.tsx` + build define.
 *
 * Exenciones: /api/*, estáticos con extensión, /payment-terminal.
 */
export const config = {
  matcher: "/:path*",
};

type EdgeProcess = {
  env?: Record<string, string | undefined>;
};

function isStaticAsset(pathname: string): boolean {
  const last = pathname.split("/").pop() ?? "";
  return last.includes(".") && !pathname.endsWith("/");
}

function isLicensePaid(): boolean {
  const edgeEnv =
    (globalThis as typeof globalThis & { process?: EdgeProcess }).process?.env ?? {};
  const raw = String(edgeEnv.LICENSE_PAID ?? edgeEnv.VITE_LICENSE_PAID ?? "")
    .toLowerCase()
    .trim();
  return raw === "true" || raw === "1" || raw === "yes" || raw === "on";
}

export default function middleware(request: Request): Response | undefined {
  const url = new URL(request.url);
  const path = url.pathname;

  if (path.startsWith("/api")) {
    return undefined;
  }
  if (isStaticAsset(path)) {
    return undefined;
  }
  if (path === "/payment-terminal" || path.startsWith("/payment-terminal/")) {
    return undefined;
  }

  if (isLicensePaid()) {
    return undefined;
  }

  const dest = new URL("/payment-terminal", url.origin);
  dest.search = url.search;
  return Response.redirect(dest.toString(), 307);
}
