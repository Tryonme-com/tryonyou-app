import { useCallback, useRef, useState } from "react";
import { buildCoreHeaders, ensureMirrorSessionId, resolveAccountScope } from "../lib/coreEngineClient";

export type GarmentSuggestion = {
  id: string;
  name: string;
  price: number;
  fit_profile: string;
  score: number;
};

export type ScanResult = {
  status: string;
  looks: GarmentSuggestion[];
  message?: string;
};

export type SnapResult = {
  status: string;
  action?: string;
  look_id?: string;
  model_url?: string;
};

export type MirrorEngineState = {
  scanning: boolean;
  scanComplete: boolean;
  suggestions: GarmentSuggestion[];
  activeLook: GarmentSuggestion | null;
  snapTriggered: boolean;
  error: string | null;
};

const SNAP_AUDIO_URL = "/audio/snap.mp3";

let snapAudioElement: HTMLAudioElement | null = null;

function getSnapAudio(): HTMLAudioElement {
  if (!snapAudioElement) {
    snapAudioElement = new Audio(SNAP_AUDIO_URL);
    snapAudioElement.volume = 0.7;
    snapAudioElement.preload = "auto";
  }
  return snapAudioElement;
}

export function useMirrorEngine() {
  const [state, setState] = useState<MirrorEngineState>({
    scanning: false,
    scanComplete: false,
    suggestions: [],
    activeLook: null,
    snapTriggered: false,
    error: null,
  });

  const abortRef = useRef<AbortController | null>(null);

  const triggerScan = useCallback(async (eventType = "soirée") => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState((prev) => ({
      ...prev,
      scanning: true,
      scanComplete: false,
      suggestions: [],
      activeLook: null,
      snapTriggered: false,
      error: null,
    }));

    try {
      const response = await fetch("/api/v1/pau/scan", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify({
          event_type: eventType,
          session_id: ensureMirrorSessionId(),
          account_scope: resolveAccountScope(),
        }),
        signal: controller.signal,
        credentials: "same-origin",
      });

      if (!response.ok) {
        throw new Error(`Scan failed: ${response.status}`);
      }

      const data = await response.json();
      const looks: GarmentSuggestion[] = data?.scan_result?.looks ?? [];

      setState((prev) => ({
        ...prev,
        scanning: false,
        scanComplete: true,
        suggestions: looks.slice(0, 5),
        activeLook: looks[0] ?? null,
        error: null,
      }));

      return looks;
    } catch (err) {
      if ((err as Error).name === "AbortError") return [];
      setState((prev) => ({
        ...prev,
        scanning: false,
        error: (err as Error).message,
      }));
      return [];
    }
  }, []);

  const triggerSnap = useCallback(async (lookId?: string) => {
    const audio = getSnapAudio();
    audio.currentTime = 0;
    void audio.play().catch(() => {});

    setState((prev) => ({ ...prev, snapTriggered: true }));

    try {
      const body: Record<string, unknown> = {
        session_id: ensureMirrorSessionId(),
        account_scope: resolveAccountScope(),
      };
      if (lookId) body.look_id = lookId;

      const response = await fetch("/api/v1/pau/snap", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify(body),
        credentials: "same-origin",
      });

      if (!response.ok) return null;

      const data = await response.json();
      const snap: SnapResult = data?.snap ?? {};

      if (snap.look_id) {
        setState((prev) => {
          const match = prev.suggestions.find((s) => s.id === snap.look_id);
          return { ...prev, activeLook: match ?? prev.activeLook };
        });
      }

      window.dispatchEvent(
        new CustomEvent("tryonyou:snap", { detail: { lookId: snap.look_id, modelUrl: snap.model_url } }),
      );

      return snap;
    } catch {
      return null;
    }
  }, []);

  const triggerBalmainSnap = useCallback(async () => {
    const audio = getSnapAudio();
    audio.currentTime = 0;
    void audio.play().catch(() => {});

    setState((prev) => ({ ...prev, snapTriggered: true }));

    try {
      const response = await fetch("/api/v1/pau/snap", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify({
          look_id: "L1",
          session_id: ensureMirrorSessionId(),
          account_scope: resolveAccountScope(),
          brand_trigger: "balmain",
        }),
        credentials: "same-origin",
      });

      if (!response.ok) return null;

      const data = await response.json();
      const snap: SnapResult = data?.snap ?? {};

      setState((prev) => {
        const balmainLook = prev.suggestions.find((s) => s.id === "L1") ?? {
          id: "L1",
          name: "Balmain Evening",
          price: 2450,
          fit_profile: "structured",
          score: 10,
        };
        return { ...prev, activeLook: balmainLook };
      });

      window.dispatchEvent(
        new CustomEvent("tryonyou:snap", {
          detail: { lookId: "L1", modelUrl: snap.model_url, brand: "balmain" },
        }),
      );

      return snap;
    } catch {
      return null;
    }
  }, []);

  const selectLook = useCallback((look: GarmentSuggestion) => {
    setState((prev) => ({ ...prev, activeLook: look }));
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState({
      scanning: false,
      scanComplete: false,
      suggestions: [],
      activeLook: null,
      snapTriggered: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    triggerScan,
    triggerSnap,
    triggerBalmainSnap,
    selectLook,
    reset,
  };
}
