import { useEffect, useState } from "react";

const presentationUrl = "/STATION_T/PRESENTATION/TRYONYOU_StationT_Presentation.pdf";

export default function StationTPage() {
  const [isPresentationAvailable, setIsPresentationAvailable] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function checkPresentation() {
      try {
        const response = await fetch(presentationUrl, {
          method: "HEAD",
          cache: "no-store",
        });
        const contentType = response.headers.get("content-type") ?? "";

        if (isMounted) {
          setIsPresentationAvailable(
            response.ok && contentType.includes("application/pdf"),
          );
        }
      } catch {
        if (isMounted) {
          setIsPresentationAvailable(false);
        }
      }
    }

    void checkPresentation();

    return () => {
      isMounted = false;
    };
  }, []);

  if (isPresentationAvailable) {
    return (
      <iframe
        src={presentationUrl}
        title="TRYONYOU Station T presentation"
        style={{ width: "100%", height: "100vh", border: "none" }}
      />
    );
  }

  return (
    <main
      style={{
        alignItems: "center",
        backgroundColor: "#0B0B0D",
        color: "#F5F5F5",
        display: "flex",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "24px",
      }}
    >
      <section style={{ maxWidth: "640px" }}>
        <p
          style={{
            color: "#C7A86A",
            fontSize: "12px",
            letterSpacing: "0.15em",
            margin: 0,
            textTransform: "uppercase",
          }}
        >
          TRYONYOU · Station T
        </p>
        <h1 style={{ fontFamily: "Georgia, serif", fontSize: "32px" }}>
          {isPresentationAvailable === null
            ? "Checking the presentation"
            : "Presentation pending"}
        </h1>
        <p style={{ lineHeight: 1.6, opacity: 0.78 }}>
          {isPresentationAvailable === null
            ? "The Station T dossier is being checked."
            : "Add the approved PDF to STATION_T/PRESENTATION/TRYONYOU_StationT_Presentation.pdf and rebuild the application."}
        </p>
        <a
          href="/"
          style={{ color: "#C7A86A", display: "inline-block", marginTop: "16px" }}
        >
          Back to TRYONYOU
        </a>
      </section>
    </main>
  );
}
