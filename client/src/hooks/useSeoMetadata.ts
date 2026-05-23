import { useEffect } from "react";

type OpenGraphMetadata = {
  title?: string;
  description?: string;
  type?: string;
  image?: string;
};

type SeoMetadata = {
  title: string;
  description: string;
  keywords?: string[];
  openGraph?: OpenGraphMetadata;
  structuredData?: Record<string, unknown>;
};

const JSON_LD_SCRIPT_ID = "tryonyou-seo-json-ld";

type MetaTagConfig = {
  selector: string;
  attribute: "name" | "property";
  key: string;
  value?: string;
};

type MetaTagSnapshot = {
  element: HTMLMetaElement;
  existed: boolean;
  previousContent: string | null;
};

function upsertMetaTag(attribute: "name" | "property", key: string, value?: string) {
  if (!value) {
    return null;
  }

  const selector = `meta[${attribute}="${key}"]`;
  const existingElement = document.head.querySelector<HTMLMetaElement>(selector);

  if (existingElement) {
    const previousContent = existingElement.getAttribute("content");
    existingElement.setAttribute("content", value);
    return { element: existingElement, existed: true, previousContent };
  }

  const element = document.createElement("meta");
  element.setAttribute(attribute, key);
  element.setAttribute("content", value);
  document.head.appendChild(element);

  return { element, existed: false, previousContent: null };
}

export function useSeoMetadata({
  title,
  description,
  keywords = [],
  openGraph,
  structuredData,
}: SeoMetadata) {
  useEffect(() => {
    const previousTitle = document.title;
    const tagConfigs: MetaTagConfig[] = [
      {
        selector: 'meta[name="description"]',
        attribute: "name",
        key: "description",
        value: description,
      },
      {
        selector: 'meta[name="keywords"]',
        attribute: "name",
        key: "keywords",
        value: keywords.length > 0 ? keywords.join(", ") : undefined,
      },
      {
        selector: 'meta[property="og:title"]',
        attribute: "property",
        key: "og:title",
        value: openGraph?.title ?? title,
      },
      {
        selector: 'meta[property="og:description"]',
        attribute: "property",
        key: "og:description",
        value: openGraph?.description ?? description,
      },
      {
        selector: 'meta[property="og:type"]',
        attribute: "property",
        key: "og:type",
        value: openGraph?.type ?? "website",
      },
      {
        selector: 'meta[property="og:image"]',
        attribute: "property",
        key: "og:image",
        value: openGraph?.image,
      },
    ];

    const previousTagState = new Map<string, MetaTagSnapshot | null>();

    for (const config of tagConfigs) {
      const existingElement = document.head.querySelector<HTMLMetaElement>(config.selector);
      previousTagState.set(
        config.selector,
        existingElement
          ? {
              element: existingElement,
              existed: true,
              previousContent: existingElement.getAttribute("content"),
            }
          : null,
      );

      const result = upsertMetaTag(config.attribute, config.key, config.value);
      if (result && !result.existed) {
        previousTagState.set(config.selector, {
          element: result.element,
          existed: false,
          previousContent: null,
        });
      }
    }

    const previousStructuredDataScript = document.getElementById(
      JSON_LD_SCRIPT_ID,
    ) as HTMLScriptElement | null;
    const previousStructuredData = previousStructuredDataScript?.textContent ?? null;

    document.title = title;

    let scriptElement = previousStructuredDataScript;
    if (structuredData) {
      if (!scriptElement) {
        scriptElement = document.createElement("script");
        scriptElement.id = JSON_LD_SCRIPT_ID;
        scriptElement.type = "application/ld+json";
        document.head.appendChild(scriptElement);
      }
      scriptElement.textContent = JSON.stringify(structuredData);
    }

    return () => {
      document.title = previousTitle;

      previousTagState.forEach((snapshot, selector) => {
        if (!snapshot) {
          const createdTag = document.head.querySelector<HTMLMetaElement>(selector);
          createdTag?.remove();
          return;
        }

        if (snapshot.existed) {
          if (snapshot.previousContent === null) {
            snapshot.element.removeAttribute("content");
          } else {
            snapshot.element.setAttribute("content", snapshot.previousContent);
          }
          return;
        }

        snapshot.element.remove();
      });

      if (!structuredData || !scriptElement) {
        return;
      }

      if (previousStructuredDataScript) {
        previousStructuredDataScript.textContent = previousStructuredData;
      } else {
        scriptElement.remove();
      }
    };
  }, [
    description,
    keywords,
    openGraph?.description,
    openGraph?.image,
    openGraph?.title,
    openGraph?.type,
    structuredData,
    title,
  ]);
}
