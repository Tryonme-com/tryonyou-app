/**
 * Vercel Edge Middleware — Protocolo Bloqueo V10 (LICENSE_PAID).
 * Proyecto: Vite SPA + Python /api; sin Next.js. Si el runtime no ejecuta este
 * archivo, el bloqueo sigue activo vía `main.tsx` + build define.
 *
 * Exenciones: /api/*, estáticos con extensión, /payment-terminal.
 */
export const config = {
  matcher: "/:path*",
};

function isStaticAsset(pathname: string): boolean {
  const last = pathname.split("/").pop() ?? "";
  return last.includes(".") && !pathname.endsWith("/");
}

export default function middleware(request: Request): Response | Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname;

  if (path.startsWith("/api")) {
    return fetch(request);
  }
  if (isStaticAsset(path)) {
    return fetch(request);
  }
  if (path === "/payment-terminal" || path.startsWith("/payment-terminal/")) {
    return fetch(request);
  }

  const raw = (process.env.LICENSE_PAID ?? "").toString().toLowerCase().trim();
  const paid = raw === "true" || raw === "1" || raw === "yes" || raw === "on";

  if (paid) {
    return fetch(request);
  }

  const dest = new URL("/payment-terminal", url.origin);
  dest.search = url.search;
  return Response.redirect(dest.toString(), 307);
}
