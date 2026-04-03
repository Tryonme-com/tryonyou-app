import { useCallback, useEffect, useState } from "react";

const GOLD = "#C5A46D";
const DARK = "#1a1510";

type AgentRecord = {
  id: number;
  name: string;
  role: string;
  status: "idle" | "running" | "done" | "error";
  last_output: string;
  updated_at: string;
};

type MesaDecision = {
  integrantes?: string[];
  decisiones?: Record<string, string>;
  ideas?: { id: number; origen: string; contenido: string; timestamp: string }[];
  resumen_agentes?: { total: number; completados: number; con_error: number };
  message?: string;
};

type GeminiResponse = {
  pregunta?: string;
  respuesta_agent70?: string;
  respuesta_jules?: string;
  coordinador?: string;
  timestamp?: string;
};

type OrchestrationStatus = {
  status: string;
  total_agents?: number;
  completados?: number;
  running?: number;
  errores?: number;
  agents?: AgentRecord[];
  mesa_decision?: MesaDecision;
  gemini_response?: GeminiResponse;
  started_at?: string;
  patent?: string;
};

const STATUS_COLOR: Record<string, string> = {
  idle: "#555",
  running: "#D4AF37",
  done: "#4caf50",
  error: "#e53935",
};

const STATUS_ICON: Record<string, string> = {
  idle: "○",
  running: "◎",
  done: "●",
  error: "✕",
};

function AgentRow({ agent }: { agent: AgentRecord }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "3px 0",
        borderBottom: "1px solid rgba(255,255,255,0.04)",
        fontSize: 11,
      }}
    >
      <span
        style={{
          color: STATUS_COLOR[agent.status] ?? "#888",
          width: 14,
          textAlign: "center",
          flexShrink: 0,
        }}
        title={agent.status}
      >
        {STATUS_ICON[agent.status] ?? "?"}
      </span>
      <span style={{ color: GOLD, minWidth: 28, flexShrink: 0, opacity: 0.6 }}>
        #{agent.id}
      </span>
      <span style={{ color: "#ddd", minWidth: 160, flexShrink: 0 }}>
        @{agent.name}
      </span>
      <span style={{ color: "#888", fontSize: 10, flex: 1 }}>{agent.role}</span>
    </div>
  );
}

export function MesaAgentes() {
  const [data, setData] = useState<OrchestrationStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch("/api/agents/status");
      if (!r.ok) return;
      const json = (await r.json()) as OrchestrationStatus;
      setData(json);
    } catch {
      /* silencioso */
    }
  }, []);

  useEffect(() => {
    void fetchStatus();
  }, [fetchStatus]);

  const handleRun = async () => {
    setRunning(true);
    setLoading(true);
    try {
      const r = await fetch("/api/agents/run", { method: "POST" });
      if (!r.ok) return;
      const json = (await r.json()) as { status: string; result?: OrchestrationStatus };
      if (json.result) setData(json.result);
      else await fetchStatus();
    } catch {
      /* silencioso */
    } finally {
      setRunning(false);
      setLoading(false);
    }
  };

  const agents = data?.agents ?? [];
  const mesa = data?.mesa_decision;
  const gemini = data?.gemini_response;

  const totalDone = agents.filter((a) => a.status === "done").length;
  const totalError = agents.filter((a) => a.status === "error").length;
  const totalRunning = agents.filter((a) => a.status === "running").length;

  return (
    <div
      style={{
        background: "rgba(10,8,5,0.92)",
        border: `1px solid ${GOLD}33`,
        borderRadius: 12,
        padding: "18px 20px",
        maxWidth: 680,
        margin: "18px auto",
        color: "#fff",
        fontFamily: "monospace",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <div>
          <p
            style={{
              margin: 0,
              fontSize: 9,
              letterSpacing: 4,
              textTransform: "uppercase",
              color: GOLD,
            }}
          >
            MESA DE LOS LISTOS · TRYONYOU V10
          </p>
          <p style={{ margin: "4px 0 0", fontSize: 11, color: "#aaa" }}>
            {data?.patent ?? "PCT/EP2025/067317"} · 61 Agentes
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleRun()}
          disabled={running}
          style={{
            padding: "7px 16px",
            fontSize: 10,
            letterSpacing: 2,
            textTransform: "uppercase",
            background: running ? "rgba(197,164,109,0.15)" : GOLD,
            color: running ? GOLD : DARK,
            border: `1px solid ${GOLD}`,
            borderRadius: 999,
            cursor: running ? "not-allowed" : "pointer",
            fontWeight: 700,
          }}
        >
          {loading ? "Orquestando…" : "▶ LANZAR"}
        </button>
      </div>

      {/* Stats bar */}
      {agents.length > 0 && (
        <div
          style={{
            display: "flex",
            gap: 16,
            marginBottom: 12,
            padding: "8px 12px",
            background: "rgba(255,255,255,0.03)",
            borderRadius: 6,
            fontSize: 11,
          }}
        >
          <span style={{ color: "#4caf50" }}>✓ {totalDone} completados</span>
          <span style={{ color: "#D4AF37" }}>◎ {totalRunning} activos</span>
          <span style={{ color: "#e53935" }}>✕ {totalError} errores</span>
          <span style={{ color: "#888" }}>○ {agents.length - totalDone - totalError - totalRunning} pendientes</span>
        </div>
      )}

      {/* Agent list (scrollable) */}
      {agents.length > 0 && (
        <div
          style={{
            maxHeight: 200,
            overflowY: "auto",
            marginBottom: 14,
            padding: "6px 8px",
            background: DARK,
            borderRadius: 6,
            border: "1px solid rgba(255,255,255,0.05)",
          }}
        >
          {agents.map((a) => (
            <AgentRow key={a.id} agent={a} />
          ))}
        </div>
      )}

      {/* Mesa decisions */}
      {mesa && (
        <div
          style={{
            marginBottom: 12,
            padding: "10px 12px",
            background: "rgba(197,164,109,0.06)",
            borderRadius: 6,
            border: `1px solid ${GOLD}22`,
          }}
        >
          <p
            style={{
              margin: "0 0 6px",
              fontSize: 9,
              letterSpacing: 3,
              textTransform: "uppercase",
              color: GOLD,
            }}
          >
            Decisiones Mesa
          </p>
          {mesa.decisiones &&
            Object.entries(mesa.decisiones).map(([k, v]) => (
              <p key={k} style={{ margin: "3px 0", fontSize: 10, color: "#ccc" }}>
                <span style={{ color: GOLD }}>[{k.toUpperCase()}]</span> {v}
              </p>
            ))}
          {mesa.message && (
            <p style={{ margin: "3px 0", fontSize: 10, color: "#888" }}>{mesa.message}</p>
          )}
          {mesa.ideas && mesa.ideas.length > 0 && (
            <div style={{ marginTop: 6 }}>
              <p
                style={{
                  margin: "0 0 4px",
                  fontSize: 9,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                  color: "#888",
                }}
              >
                Ideas
              </p>
              {mesa.ideas.map((idea) => (
                <p
                  key={idea.id}
                  style={{ margin: "2px 0", fontSize: 10, color: "#bbb" }}
                >
                  💡 <span style={{ color: GOLD }}>@{idea.origen}</span>: {idea.contenido}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Gemini response */}
      {gemini && (
        <div
          style={{
            padding: "10px 12px",
            background: "rgba(255,255,255,0.03)",
            borderRadius: 6,
            border: "1px solid rgba(255,255,255,0.07)",
          }}
        >
          <p
            style={{
              margin: "0 0 6px",
              fontSize: 9,
              letterSpacing: 3,
              textTransform: "uppercase",
              color: "#aaa",
            }}
          >
            @tryonyouagent → @gemini
          </p>
          {gemini.respuesta_agent70 && (
            <p style={{ margin: "3px 0", fontSize: 10, color: "#ccc" }}>
              <span style={{ color: GOLD }}>@agent70</span>: {gemini.respuesta_agent70}
            </p>
          )}
          {gemini.respuesta_jules && (
            <p style={{ margin: "3px 0", fontSize: 10, color: "#ccc" }}>
              <span style={{ color: GOLD }}>@jules</span>: {gemini.respuesta_jules}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
