import axios from "axios";

const LINEAR_API_URL = "https://api.linear.app/graphql";
const SHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets";

type LinearIssueNode = {
  id: string;
  identifier: string;
  title: string;
  description: string | null;
  updatedAt: string;
  createdAt: string;
  priority: number | null;
  state: { name: string } | null;
  assignee: { name: string | null; email: string | null } | null;
};


type LinearIssueConnection = {
  nodes?: LinearIssueNode[];
  pageInfo?: { hasNextPage?: boolean; endCursor?: string | null };
};

type LinearIssuesResponse = {
  data?: {
    issues?: LinearIssueConnection;
  };
  errors?: Array<{ message?: string }>;
};

type SyncResult = {
  ok: boolean;
  status: "success" | "skipped" | "error";
  message: string;
  issuesFetched: number;
  rowsWritten: number;
};

function getMissingRequiredEnv(): string[] {
  const required = [
    "LINEAR_API_TOKEN",
    "GOOGLE_SHEETS_ID",
    "GOOGLE_SHEETS_ACCESS_TOKEN",
  ];

  return required.filter((name) => !process.env[name]);
}

async function fetchLinearIssues(): Promise<LinearIssueNode[]> {
  const token = process.env.LINEAR_API_TOKEN as string;
  const linearAuth = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  const pageSize = Number(process.env.LINEAR_PAGE_SIZE ?? 50);
  const maxPages = Number(process.env.LINEAR_MAX_PAGES ?? 10);

  const nodes: LinearIssueNode[] = [];
  let after: string | null = null;

  for (let page = 0; page < maxPages; page += 1) {
    const query = `
      query SyncLinearIssues($first: Int!, $after: String) {
        issues(first: $first, after: $after) {
          nodes {
            id
            identifier
            title
            description
            createdAt
            updatedAt
            priority
            state {
              name
            }
            assignee {
              name
              email
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    `;

    const response: { data: LinearIssuesResponse } = await axios.post<LinearIssuesResponse>(
      LINEAR_API_URL,
      { query, variables: { first: pageSize, after } },
      {
        headers: {
          Authorization: linearAuth,
          "Content-Type": "application/json",
        },
        timeout: 20000,
      },
    );

    if (response.data?.errors?.length) {
      const firstError = response.data.errors[0]?.message ?? "Unknown Linear error";
      throw new Error(`Linear API error: ${firstError}`);
    }

    const issueConnection: LinearIssueConnection | undefined = response.data?.data?.issues;
    const pageNodes: LinearIssueNode[] = issueConnection?.nodes ?? [];
    const pageInfo: { hasNextPage?: boolean; endCursor?: string | null } | undefined = issueConnection?.pageInfo;

    nodes.push(...pageNodes);

    if (!pageInfo?.hasNextPage || !pageInfo?.endCursor) {
      break;
    }

    after = pageInfo.endCursor;
  }

  return nodes;
}

function toSheetRows(issues: LinearIssueNode[]): string[][] {
  const headers = [
    "id",
    "identifier",
    "title",
    "description",
    "state",
    "priority",
    "assignee_name",
    "assignee_email",
    "created_at",
    "updated_at",
  ];

  const rows = issues.map((issue) => [
    issue.id,
    issue.identifier,
    issue.title,
    issue.description ?? "",
    issue.state?.name ?? "",
    issue.priority != null ? String(issue.priority) : "",
    issue.assignee?.name ?? "",
    issue.assignee?.email ?? "",
    issue.createdAt,
    issue.updatedAt,
  ]);

  return [headers, ...rows];
}

async function writeRowsToSheet(rows: string[][]): Promise<void> {
  const sheetId = process.env.GOOGLE_SHEETS_ID as string;
  const accessToken = process.env.GOOGLE_SHEETS_ACCESS_TOKEN as string;
  const range = process.env.GOOGLE_SHEETS_RANGE ?? "Linear Tasks!A1";

  const encodedRange = encodeURIComponent(range);
  const url = `${SHEETS_API_BASE}/${sheetId}/values/${encodedRange}?valueInputOption=RAW`;

  await axios.put(
    url,
    { values: rows },
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      timeout: 20000,
    },
  );
}

export async function syncLinearToGoogleSheets(): Promise<SyncResult> {
  const missingEnv = getMissingRequiredEnv();
  if (missingEnv.length > 0) {
    return {
      ok: false,
      status: "skipped",
      message: `Sync skipped. Missing env: ${missingEnv.join(", ")}`,
      issuesFetched: 0,
      rowsWritten: 0,
    };
  }

  try {
    const issues = await fetchLinearIssues();
    const rows = toSheetRows(issues);
    await writeRowsToSheet(rows);

    return {
      ok: true,
      status: "success",
      message: "Linear tasks synced to Google Sheets.",
      issuesFetched: issues.length,
      rowsWritten: rows.length,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown sync error";
    return {
      ok: false,
      status: "error",
      message,
      issuesFetched: 0,
      rowsWritten: 0,
    };
  }
}

export function startSyncCron(): void {
  const rawInterval = process.env.LINEAR_SYNC_CRON_MS;
  if (!rawInterval) {
    return;
  }

  const intervalMs = Number(rawInterval);
  if (!Number.isFinite(intervalMs) || intervalMs <= 0) {
    console.warn("[sync] Ignoring invalid LINEAR_SYNC_CRON_MS value");
    return;
  }

  const timer = setInterval(async () => {
    const result = await syncLinearToGoogleSheets();
    console.log(
      `[sync] status=${result.status} fetched=${result.issuesFetched} rows=${result.rowsWritten}`,
    );
  }, intervalMs);

  timer.unref();
}
