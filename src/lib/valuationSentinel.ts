export type ValuationSentinelInput = {
  monthlyNodeRevenueEur?: number;
  activeNodes?: readonly string[];
  arrMultiplier?: number;
  exitHorizonMonths?: number;
};

export type ValuationSentinelSnapshot = {
  monthlyRevenueEur: number;
  projectedArrEur: number;
  arrMultiplier: number;
  marketValuationEur: number;
  exitHorizonMonths: number;
  referenceNodes: readonly string[];
  status: "READY_FOR_REVIEW";
};

const DEFAULT_MONTHLY_NODE_REVENUE_EUR = 33240;
const DEFAULT_ACTIVE_NODES = ["Lafayette", "Le Bon Marche", "La Defense"] as const;
const DEFAULT_ARR_MULTIPLIER = 8.5;
const DEFAULT_EXIT_HORIZON_MONTHS = 6;

function assertPositiveFinite(value: number, fieldName: string): number {
  if (!Number.isFinite(value) || value <= 0) {
    throw new Error(`valuation_sentinel_invalid_${fieldName}`);
  }

  return value;
}

export function calculateValuationSentinel(
  input: ValuationSentinelInput = {},
): ValuationSentinelSnapshot {
  const monthlyRevenueEur = assertPositiveFinite(
    input.monthlyNodeRevenueEur ?? DEFAULT_MONTHLY_NODE_REVENUE_EUR,
    "monthly_revenue",
  );
  const arrMultiplier = assertPositiveFinite(
    input.arrMultiplier ?? DEFAULT_ARR_MULTIPLIER,
    "arr_multiplier",
  );
  const exitHorizonMonths = assertPositiveFinite(
    input.exitHorizonMonths ?? DEFAULT_EXIT_HORIZON_MONTHS,
    "exit_horizon",
  );
  const referenceNodes =
    input.activeNodes && input.activeNodes.length > 0 ? input.activeNodes : DEFAULT_ACTIVE_NODES;
  const projectedArrEur = monthlyRevenueEur * 12;

  return {
    monthlyRevenueEur,
    projectedArrEur,
    arrMultiplier,
    marketValuationEur: projectedArrEur * arrMultiplier,
    exitHorizonMonths,
    referenceNodes,
    status: "READY_FOR_REVIEW",
  };
}
