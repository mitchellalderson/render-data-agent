"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import {
  Database,
  Upload,
  Settings,
  PlayCircle,
  ChevronRight,
  MessageCircle,
  Loader2,
  Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger
} from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "@/components/ui/accordion";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from "recharts";

type TableData = {
  title: string;
  columns: string[];
  rows: Record<string, any>[];
};

type ChartData = {
  id: string;
  title: string;
  data: any[];
  xKey: string;
  yKey: string;
  meta?: string;
};

type AgentMessage = {
  id: string;
  role: "user" | "agent";
  content: string;
  table?: TableData;
  charts?: ChartData[];
  sql?: string;
};

const MOCK_SIGNUPS = [
  {
    id: 1,
    email: "alex@seriesasearch.com",
    name: "Alex Rivera",
    title: "CTO",
    company: "Series A Search",
    location: "San Francisco, CA",
    plan: "Team",
    source: "Homepage",
    icpFit: "High",
    sessions: 18,
    queriesRun: 220
  },
  {
    id: 2,
    email: "mira@buildflow.dev",
    name: "Mira Chen",
    title: "Head of Engineering",
    company: "BuildFlow",
    location: "New York, NY",
    plan: "Free",
    source: "Launch tweet",
    icpFit: "Medium",
    sessions: 6,
    queriesRun: 35
  },
  {
    id: 3,
    email: "jordan@agentlab.ai",
    name: "Jordan Patel",
    title: "Founder",
    company: "AgentLab",
    location: "Remote (US)",
    plan: "Team",
    source: "Clay outbound",
    icpFit: "High",
    sessions: 24,
    queriesRun: 410
  },
  {
    id: 4,
    email: "sam@opsstack.io",
    name: "Sam Gupta",
    title: "VP Engineering",
    company: "OpsStack",
    location: "Austin, TX",
    plan: "Enterprise",
    source: "Founder intro",
    icpFit: "High",
    sessions: 42,
    queriesRun: 980
  },
  {
    id: 5,
    email: "lee@betaapps.xyz",
    name: "Lee Park",
    title: "Senior Engineer",
    company: "BetaApps",
    location: "Toronto, CA",
    plan: "Free",
    source: "Product Hunt",
    icpFit: "Low",
    sessions: 3,
    queriesRun: 10
  }
];

const icpChartData = [
  { icpFit: "High", signups: 3 },
  { icpFit: "Medium", signups: 1 },
  { icpFit: "Low", signups: 1 }
];

const sourceChartData = [
  { source: "Homepage", signups: 1 },
  { source: "Launch tweet", signups: 1 },
  { source: "Clay outbound", signups: 1 },
  { source: "Founder intro", signups: 1 },
  { source: "Product Hunt", signups: 1 }
];

function Sidebar({
  onUpload,
  dataStatus
}: {
  onUpload: (file: File) => void;
  dataStatus: { enrichmentLoaded: boolean; enrichmentRows: number; databaseConnected: boolean };
}) {
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <aside className="hidden lg:flex lg:w-72 flex-col border-r border-zinc-800/50 bg-black/60 backdrop-blur-sm">
      <div className="px-4 py-3 flex items-center justify-between border-b border-zinc-800/50">
        <div className="flex items-center gap-2">
          <span className="h-6 w-6 rounded bg-gradient-to-br from-purple-600 to-purple-800 border border-purple-500/30 flex items-center justify-center text-xs font-semibold text-white shadow-lg shadow-purple-500/20">
            DA
          </span>
          <div>
            <div className="text-sm font-medium text-white">
              Data Analyst Agent
            </div>
            <div className="text-xs text-zinc-400">
              ICP Analysis Workspace
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 text-zinc-400 hover:text-white hover:bg-purple-500/10"
        >
          <Settings className="h-4 w-4" />
        </Button>
      </div>

      <div className="p-3 space-y-3 flex-1 overflow-auto">
        <div className="space-y-2">
          <div className="text-xs font-semibold text-zinc-400 tracking-wide">
            DATA SOURCES
          </div>

          <label className="block text-xs font-medium text-zinc-400 mt-3">
            Upload Enrichment CSV
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full border border-dashed border-purple-500/30 rounded-lg px-3 py-4 text-xs text-zinc-300 bg-gradient-to-br from-purple-950/20 to-black/40 flex flex-col items-center gap-1 hover:border-purple-500/50 hover:text-white hover:bg-purple-950/30 transition-all duration-200"
          >
            <Upload className="h-4 w-4 text-purple-400" />
            <span>Drop a CSV here or click to browse</span>
            <span className="text-[11px] text-zinc-500">
              Up to 300MB • columns auto-detected
            </span>
          </button>
        </div>

        <Separator className="bg-zinc-900" />

        <div className="space-y-1">
          <div className="text-xs font-semibold text-zinc-400 tracking-wide mb-1">
            CONNECTED DATA
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex items-center justify-between rounded-lg border border-purple-500/20 bg-gradient-to-r from-purple-950/30 to-black/50 px-2 py-1.5">
              <div className="flex items-center gap-2">
                <span className={`h-1.5 w-1.5 rounded-full ${dataStatus.databaseConnected ? 'bg-purple-400 shadow-sm shadow-purple-400/50' : 'bg-zinc-600'}`} />
                <div>
                  <div className="text-white">Signup Database</div>
                  <div className="text-[11px] text-zinc-400">
                    {dataStatus.databaseConnected ? "Connected" : "Not connected"}
                  </div>
                </div>
              </div>
              <span className="text-[11px] text-zinc-500">Read-only</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-purple-500/20 bg-gradient-to-r from-purple-950/30 to-black/50 px-2 py-1.5">
              <div className="flex items-center gap-2">
                <span className={`h-1.5 w-1.5 rounded-full ${dataStatus.enrichmentLoaded ? 'bg-purple-400 shadow-sm shadow-purple-400/50' : 'bg-zinc-600'}`} />
                <div>
                  <div className="text-white">Enrichment CSV</div>
                  <div className="text-[11px] text-zinc-400">
                    {dataStatus.enrichmentLoaded 
                      ? `${dataStatus.enrichmentRows.toLocaleString()} rows loaded`
                      : "Not uploaded"}
                  </div>
                </div>
              </div>
              {dataStatus.enrichmentLoaded && (
                <span className="text-[11px] text-purple-400">Ready</span>
              )}
            </div>
          </div>
        </div>

        <Separator className="bg-zinc-900" />

        <div className="space-y-2">
          <div className="text-xs font-semibold text-zinc-400 tracking-wide">
            EXAMPLE QUERIES
          </div>
          <div className="space-y-1 text-xs text-zinc-300">
            <div className="rounded-lg px-2 py-1.5 bg-purple-950/20 border border-purple-500/10 text-zinc-300 hover:bg-purple-950/30 hover:border-purple-500/20 transition-colors cursor-pointer">
              Who are our highest ICP fit customers?
            </div>
            <div className="rounded-lg px-2 py-1.5 bg-purple-950/20 border border-purple-500/10 text-zinc-300 hover:bg-purple-950/30 hover:border-purple-500/20 transition-colors cursor-pointer">
              Show me signups by industry and company size
            </div>
            <div className="rounded-lg px-2 py-1.5 bg-purple-950/20 border border-purple-500/10 text-zinc-300 hover:bg-purple-950/30 hover:border-purple-500/20 transition-colors cursor-pointer">
              What patterns do high-fit customers share?
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="mt-1">
        <div className="h-7 w-7 rounded-full bg-gradient-to-br from-purple-600/20 to-purple-800/20 border border-purple-500/40 flex items-center justify-center shadow-lg shadow-purple-500/20">
          <Sparkles className="h-3.5 w-3.5 text-purple-400 animate-pulse" />
        </div>
      </div>
      <div className="flex-1">
        <div className="rounded-2xl border border-purple-500/20 bg-gradient-to-r from-purple-950/30 to-black/50 px-3 py-2.5 text-sm text-zinc-300">
          <div className="flex items-center gap-2">
            <span>Thinking</span>
            <div className="flex gap-1">
              <span className="animate-bounce text-purple-400" style={{ animationDelay: "0ms" }}>
                •
              </span>
              <span className="animate-bounce text-purple-400" style={{ animationDelay: "150ms" }}>
                •
              </span>
              <span className="animate-bounce text-purple-400" style={{ animationDelay: "300ms" }}>
                •
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MessagesList({
  messages,
  isLoading
}: {
  messages: AgentMessage[];
  isLoading: boolean;
}) {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages or loading state changes
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <ScrollArea className="flex-1 pr-1">
      <div className="space-y-4">
        {messages.map((m) => (
          <div key={m.id} className="flex gap-3">
            <div className="mt-1">
              {m.role === "user" ? (
                <div className="h-7 w-7 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center text-[11px] text-zinc-200">
                  You
                </div>
              ) : (
                <div className="h-7 w-7 rounded-full bg-gradient-to-br from-purple-600/20 to-purple-800/20 border border-purple-500/40 flex items-center justify-center shadow-lg shadow-purple-500/20">
                  <MessageCircle className="h-3.5 w-3.5 text-purple-400" />
                </div>
              )}
            </div>
            <div className="flex-1 space-y-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-100">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
                    h1: ({ children }) => <h1 className="text-lg font-semibold mb-2 mt-4 first:mt-0 text-white">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-base font-semibold mb-2 mt-3 first:mt-0 text-white">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-sm font-semibold mb-1.5 mt-2 first:mt-0 text-white">{children}</h3>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1 ml-2">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1 ml-2">{children}</ol>,
                    li: ({ children }) => <li className="text-zinc-200 leading-relaxed">{children}</li>,
                    strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                    em: ({ children }) => <em className="italic text-zinc-200">{children}</em>,
                    code: ({ children, className }) => {
                      const isInline = !className;
                      return isInline ? (
                        <code className="bg-zinc-900 px-1.5 py-0.5 rounded text-xs text-purple-300 font-mono border border-zinc-800">{children}</code>
                      ) : (
                        <code className={className}>{children}</code>
                      );
                    },
                    pre: ({ children }) => (
                      <pre className="bg-zinc-900 p-3 rounded-lg overflow-x-auto mb-3 border border-zinc-800">
                        {children}
                      </pre>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-purple-500/50 pl-3 ml-2 italic text-zinc-300 mb-3">
                        {children}
                      </blockquote>
                    ),
                    hr: () => <hr className="my-4 border-zinc-800" />,
                    a: ({ children, href }) => (
                      <a href={href} className="text-purple-400 hover:text-purple-300 underline" target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    ),
                  }}
                >
                  {m.content}
                </ReactMarkdown>
              </div>

              {m.table && (
                <Card className="bg-black border-zinc-800">
                  <CardHeader className="py-2 px-3 flex flex-row items-center justify-between">
                    <CardTitle className="text-xs text-zinc-300">
                      {m.table.title}
                    </CardTitle>
                    <div className="flex items-center gap-1 text-[11px] text-zinc-500">
                      <span>{m.table.rows.length} rows</span>
                    </div>
                  </CardHeader>
                  <CardContent className="px-3 pb-3">
                    <div className="w-full overflow-x-auto text-xs">
                      <table className="min-w-full border border-zinc-900 rounded-md">
                        <thead className="bg-zinc-950/80">
                          <tr>
                            {m.table.columns.map((col) => (
                              <th
                                key={col}
                                className="px-2 py-1 text-left font-medium text-zinc-400 border-b border-zinc-900"
                              >
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {m.table.rows.map((row, idx) => (
                            <tr key={idx} className="hover:bg-zinc-950/60">
                              {m.table.columns.map((col) => (
                                <td
                                  key={col}
                                  className="px-2 py-1 border-b border-zinc-900 text-zinc-200"
                                >
                                  {row[col]}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {m.charts && m.charts.length > 0 && (
                <div className="grid gap-3 md:grid-cols-2">
                  {m.charts.map((chart) => (
                    <Card
                      key={chart.id}
                      className="bg-black border-zinc-800 h-60"
                    >
                      <CardHeader className="py-2 px-3">
                        <CardTitle className="text-xs text-zinc-300 flex items-center justify-between">
                          <span>{chart.title}</span>
                          {chart.meta && (
                            <span className="text-[11px] text-zinc-500">
                              {chart.meta}
                            </span>
                          )}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="px-3 pb-3 h-44">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={chart.data}>
                            <XAxis
                              dataKey={chart.xKey}
                              tick={{ fontSize: 10, fill: "#a1a1aa" }}
                              tickLine={false}
                              axisLine={{ stroke: "#27272a" }}
                            />
                            <YAxis
                              tick={{ fontSize: 10, fill: "#a1a1aa" }}
                              tickLine={false}
                              axisLine={{ stroke: "#27272a" }}
                            />
                            <RechartsTooltip
                              contentStyle={{
                                backgroundColor: "#020617",
                                border: "1px solid #27272a",
                                borderRadius: 8,
                                fontSize: 11
                              }}
                              labelStyle={{ color: "#e4e4e7" }}
                            />
                            <Bar dataKey={chart.yKey} radius={4} fill="#9333ea" />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {m.sql && (
                <Accordion
                  type="single"
                  collapsible
                  className="w-full text-xs"
                >
                  <AccordionItem
                    value="sql"
                    className="border border-zinc-800 rounded-md bg-black"
                  >
                    <AccordionTrigger className="px-3 py-1.5 text-xs text-zinc-400 hover:no-underline">
                      <div className="flex items-center gap-2">
                        <ChevronRight className="h-3 w-3" />
                        <span>Generated SQL (preview only)</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-3 pb-2">
                      <pre className="text-[11px] text-zinc-200 bg-zinc-950 rounded-md p-2 overflow-x-auto">
                        {m.sql}
                      </pre>
                      <div className="flex justify-end mt-1.5">
                        <Button
                          variant="outline"
                          size="xs"
                          className="border-zinc-800 text-[11px] h-6 px-2"
                          onClick={() => {
                            if (navigator.clipboard) {
                              navigator.clipboard.writeText(m.sql || "");
                            }
                          }}
                        >
                          Copy SQL
                        </Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              )}
            </div>
          </div>
        ))}
        {isLoading && <ThinkingIndicator />}
        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
}

function InputBar({
  onSend,
  isLoading
}: {
  onSend: (message: string) => void;
  isLoading: boolean;
}) {
  const [value, setValue] = React.useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSend(value.trim());
    setValue("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Submit on Enter (unless Shift is held for newline)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!value.trim() || isLoading) return;
      onSend(value.trim());
      setValue("");
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-zinc-800 pt-3 mt-3"
    >
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <Textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            placeholder={`Ask something like: "Which sources are bringing in the most high-ICP founders over the last 30 days?"`}
            className="w-full resize-none rounded-lg border-purple-500/20 bg-black/60 text-sm text-white placeholder:text-zinc-500 focus-visible:ring-2 focus-visible:ring-purple-500/50 focus-visible:border-purple-500/50 transition-all duration-200"
          />
        </div>
        <Button
          type="submit"
          disabled={isLoading || !value.trim()}
          className="h-9 px-3 rounded-lg bg-black text-white text-xs font-medium hover:bg-zinc-900 border border-zinc-800 hover:border-purple-500/50 flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-purple-500/10 hover:shadow-purple-500/20"
        >
          {isLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin text-purple-400" />
          ) : (
            <PlayCircle className="h-3.5 w-3.5" />
          )}
          <span>Run</span>
        </Button>
      </div>
      <div className="flex items-center justify-between mt-1.5 text-[11px] text-zinc-500">
        <span>Data is queried in read-only mode • PII stays in your warehouse.</span>
        <span>Enter to send • Shift + Enter for newline</span>
      </div>
    </form>
  );
}

export default function DataAnalystAgentPage() {
  const [messages, setMessages] = React.useState<AgentMessage[]>([
    {
      id: "welcome",
      role: "agent",
      content:
        "👋 Welcome to the ICP Analysis Agent! I can help you analyze your customer data and identify ideal customer profile matches.\n\n**To get started:**\n1. Upload your enrichment CSV using the sidebar\n2. Ask me questions about your data\n\nI'll connect to your signup database automatically and help you understand patterns, segments, and ICP fit."
    }
  ]);

  const [isLoading, setIsLoading] = React.useState(false);
  const [dataStatus, setDataStatus] = React.useState({
    enrichmentLoaded: false,
    enrichmentRows: 0,
    databaseConnected: false
  });

  // API base URL - use environment variable or default to localhost
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch data status on mount and periodically
  React.useEffect(() => {
    fetchDataStatus();
    const interval = setInterval(fetchDataStatus, 5000); // Every 5 seconds
    return () => clearInterval(interval);
  }, []);

  async function fetchDataStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      if (res.ok) {
        const data = await res.json();
        setDataStatus({
          enrichmentLoaded: data.enrichment_loaded,
          enrichmentRows: data.enrichment_rows,
          databaseConnected: data.database_connected
        });
      }
    } catch (e) {
      console.error("Failed to fetch data status:", e);
    }
  }

  async function handleUpload(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
        // Don't set Content-Type header - browser will set it with boundary for FormData
        credentials: "omit" // Don't send credentials with file uploads
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();

      // Add success message
      const successMessage: AgentMessage = {
        id: `a-${Date.now()}`,
        role: "agent",
        content: `✅ Successfully uploaded ${file.name}!\n\n**Data Summary:**\n- ${data.data.rows.toLocaleString()} rows\n- ${data.data.columns} columns\n- Columns: ${data.data.column_names.join(", ")}\n\nYou can now ask me questions about your data!`
      };

      setMessages((prev) => [...prev, successMessage]);

      // Refresh status
      await fetchDataStatus();
    } catch (e) {
      const errorMessage: AgentMessage = {
        id: `a-${Date.now()}`,
        role: "agent",
        content: `❌ Failed to upload file: ${e instanceof Error ? e.message : "Unknown error"}`
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSend(message: string) {
    const userMessage: AgentMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: message
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();

      const agentMessage: AgentMessage = {
        id: `a-${Date.now()}`,
        role: "agent",
        content: data.content,
        table: data.table,
        charts: data.charts,
        sql: data.sql
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (e) {
      const errorMessage: AgentMessage = {
        id: `a-${Date.now()}`,
        role: "agent",
        content:
          `❌ Something went wrong: ${e instanceof Error ? e.message : "Unknown error"}.\n\nMake sure the backend API is running at ${API_BASE}.`
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-black text-zinc-100 flex">
      <Sidebar onUpload={handleUpload} dataStatus={dataStatus} />

      <main className="flex-1 flex flex-col max-w-[1200px] mx-auto w-full">
        <header className="border-b border-purple-500/20 px-4 md:px-6 py-3 flex items-center justify-between gap-3 bg-gradient-to-r from-black via-purple-950/10 to-black backdrop-blur-sm">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm md:text-base font-medium text-white">
                ICP Analysis Agent
              </h1>
              <Badge className="bg-purple-950/40 border border-purple-500/30 text-[10px] uppercase tracking-wide text-purple-300">
                Chat Workspace
              </Badge>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Ask natural-language questions about your enrichment data and ICP fit.
            </p>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-zinc-400">
            <span className="hidden md:inline">Status:</span>
            <span className="inline-flex items-center gap-1">
              <span className={`h-1.5 w-1.5 rounded-full ${dataStatus.databaseConnected ? 'bg-purple-400 shadow-sm shadow-purple-400/50' : 'bg-zinc-600'}`} />
              Database
            </span>
            <span className="inline-flex items-center gap-1">
              <span className={`h-1.5 w-1.5 rounded-full ${dataStatus.enrichmentLoaded ? 'bg-purple-400 shadow-sm shadow-purple-400/50' : 'bg-zinc-600'}`} />
              Enrichment
            </span>
          </div>
        </header>

        <section className="flex-1 flex flex-col px-4 md:px-6 py-3 gap-3">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 text-xs text-zinc-300 bg-gradient-to-br from-purple-950/20 to-black/40 border border-purple-500/20 rounded-xl px-3 py-2.5">
              <div className="font-medium text-white mb-1 text-[11px] tracking-wide">
                Examples you can ask
              </div>
              <div className="grid md:grid-cols-3 gap-2">
                <div className="rounded-lg bg-black/60 border border-purple-500/20 px-2.5 py-2 hover:border-purple-500/40 hover:bg-black/80 transition-colors">
                  <div className="text-[11px] text-purple-400 mb-1 font-medium">
                    Conversion
                  </div>
                  <div className="text-zinc-200">
                    How do signup-to-activation rates compare for high vs. low
                    ICP fit?
                  </div>
                </div>
                <div className="rounded-lg bg-black/60 border border-purple-500/20 px-2.5 py-2 hover:border-purple-500/40 hover:bg-black/80 transition-colors">
                  <div className="text-[11px] text-purple-400 mb-1 font-medium">Channels</div>
                  <div className="text-zinc-200">
                    Which sources are bringing in the highest concentration of
                    high-fit founders?
                  </div>
                </div>
                <div className="rounded-lg bg-black/60 border border-purple-500/20 px-2.5 py-2 hover:border-purple-500/40 hover:bg-black/80 transition-colors">
                  <div className="text-[11px] text-purple-400 mb-1 font-medium">ICP</div>
                  <div className="text-zinc-200">
                    Break down signups by title, company size, and location for
                    high ICP accounts.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex-1 flex flex-col min-h-0 mt-1">
            <MessagesList messages={messages} isLoading={isLoading} />
            <InputBar onSend={handleSend} isLoading={isLoading} />
          </div>
        </section>
      </main>
    </div>
  );
}
