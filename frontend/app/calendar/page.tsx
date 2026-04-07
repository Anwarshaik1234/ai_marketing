"use client";

import { DragDropContext, Draggable, Droppable, DropResult } from "@hello-pangea/dnd";
import { useEffect, useMemo, useState } from "react";
import { api, apiUrl } from "@/lib/api";

type Piece = {
  id: string;
  platform: string;
  format_key: string;
  title: string;
  body?: string;
  status?: string;
  scheduled_date?: string | null;
};

const STATUS_OPTIONS = ["Draft", "Ready", "Scheduled", "Published"] as const;

function addDays(d: Date, n: number) {
  const x = new Date(d);
  x.setDate(x.getDate() + n);
  return x;
}

export default function CalendarPage() {
  const [campaignId, setCampaignId] = useState("");
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [platformFilter, setPlatformFilter] = useState("All");
  const [alerts, setAlerts] = useState<string[]>([]);
  const start = useMemo(() => new Date(), []);

  const visiblePieces = useMemo(() => {
    if (platformFilter === "All") return pieces;
    return pieces.filter((p) => p.platform === platformFilter);
  }, [pieces, platformFilter]);

  const platformOptions = useMemo(() => {
    const u = new Set(pieces.map((p) => p.platform));
    return ["All", ...Array.from(u).sort()];
  }, [pieces]);

  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addDays(start, i)), [start]);

  async function load() {
    if (!campaignId) return;
    const data = await api<Piece[]>(`/content/campaign/${campaignId}`);
    setPieces(data);
    const g = await api<{ alerts: string[] }>(`/calendar/gaps/${campaignId}`);
    setAlerts(g.alerts);
  }

  useEffect(() => {
    setCampaignId(localStorage.getItem("lastCampaignId") || "");
  }, []);

  useEffect(() => {
    if (campaignId) load();
  }, [campaignId]);

  function bucketForPiece(p: Piece): string {
    if (!p.scheduled_date) return "unscheduled";
    const iso = p.scheduled_date.slice(0, 10);
    const key = `day-${iso}`;
    const inWeek = days.some((d) => d.toISOString().slice(0, 10) === iso);
    if (!inWeek) return "unscheduled";
    return key;
  }

  const columns = useMemo(() => {
    const map: Record<string, Piece[]> = { unscheduled: [] };
    days.forEach((d) => {
      const key = `day-${d.toISOString().slice(0, 10)}`;
      map[key] = [];
    });
    visiblePieces.forEach((p) => {
      const b = bucketForPiece(p);
      if (!map[b]) map.unscheduled.push(p);
      else map[b].push(p);
    });
    return map;
  }, [visiblePieces, days]);

  async function onDragEnd(result: DropResult) {
    if (!result.destination) return;
    const pid = result.draggableId;
    const dest = result.destination.droppableId;
    if (dest === "unscheduled") {
      await api("/calendar/move", {
        method: "POST",
        body: JSON.stringify({ content_piece_id: pid, scheduled_date: null }),
      });
      await load();
      return;
    }
    if (dest.startsWith("day-")) {
      const date = dest.replace("day-", "");
      await api("/calendar/move", {
        method: "POST",
        body: JSON.stringify({ content_piece_id: pid, scheduled_date: date }),
      });
      await load();
    }
  }

  async function aiSchedule() {
    await api(`/calendar/suggest/${campaignId}`, { method: "POST" });
    await load();
  }

  async function updateStatus(pieceId: string, status: string) {
    await api(`/content/piece/${pieceId}/status?status=${encodeURIComponent(status)}`, { method: "PATCH" });
    await load();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Campaign calendar</h1>
        <p className="text-slate-600">Drag cards onto a day. AI can propose a schedule; export CSV or printable HTML.</p>
      </div>
      <div className="flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <label className="space-y-1">
          <span className="text-sm font-medium">Campaign ID</span>
          <input value={campaignId} onChange={(e) => setCampaignId(e.target.value)} className="rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1">
          <span className="text-sm font-medium">Filter by platform</span>
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="rounded-lg border px-3 py-2 text-sm"
          >
            {platformOptions.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <button onClick={load} className="self-end rounded-xl border px-4 py-2 text-sm">
          Refresh
        </button>
        <button onClick={aiSchedule} className="self-end rounded-xl bg-accent px-4 py-2 text-sm text-white">
          AI schedule
        </button>
        <a className="self-end text-sm text-accent underline" href={apiUrl(`/calendar/export?campaign_id=${campaignId}&format=csv`)} target="_blank" rel="noreferrer">
          Export CSV
        </a>
        <a className="self-end text-sm text-accent underline" href={apiUrl(`/calendar/export?campaign_id=${campaignId}&format=pdf`)} target="_blank" rel="noreferrer">
          Print / PDF
        </a>
      </div>
      {alerts.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <p className="font-semibold">Gap highlights</p>
          <ul className="mt-2 list-disc pl-5">
            {alerts.slice(0, 6).map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      )}
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="flex gap-3 overflow-x-auto pb-4">
          <Droppable droppableId="unscheduled">
            {(prov) => (
              <div ref={prov.innerRef} {...prov.droppableProps} className="min-w-[260px] rounded-2xl border border-dashed border-slate-300 bg-white p-3">
                <p className="mb-2 text-sm font-semibold">Unscheduled</p>
                {columns.unscheduled?.map((p, idx) => (
                  <Draggable draggableId={p.id} index={idx} key={p.id}>
                    {(pprov) => (
                      <div ref={pprov.innerRef} {...pprov.draggableProps} {...pprov.dragHandleProps} className="mb-2 rounded-xl border bg-slate-50 p-2 text-sm">
                        <p className="font-semibold">{p.platform}</p>
                        <p className="text-xs text-slate-600">{p.format_key}</p>
                        <select
                          value={p.status || "Draft"}
                          onClick={(ev) => ev.stopPropagation()}
                          onMouseDown={(ev) => ev.stopPropagation()}
                          onChange={(ev) => updateStatus(p.id, ev.target.value)}
                          className="mt-2 w-full rounded border border-slate-200 bg-white px-1 py-0.5 text-xs"
                        >
                          {STATUS_OPTIONS.map((s) => (
                            <option key={s} value={s}>
                              {s}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                  </Draggable>
                ))}
                {prov.placeholder}
              </div>
            )}
          </Droppable>
          {days.map((d) => {
            const key = `day-${d.toISOString().slice(0, 10)}`;
            const list = columns[key] || [];
            return (
              <Droppable droppableId={key} key={key}>
                {(prov) => (
                  <div ref={prov.innerRef} {...prov.droppableProps} className="min-w-[220px] rounded-2xl border border-slate-200 bg-white p-3">
                    <p className="mb-2 text-sm font-semibold">{d.toDateString().slice(0, 10)}</p>
                    {list.map((p, idx) => (
                      <Draggable draggableId={p.id} index={idx} key={p.id}>
                        {(pprov) => (
                          <div ref={pprov.innerRef} {...pprov.draggableProps} {...pprov.dragHandleProps} className="mb-2 rounded-xl border bg-slate-50 p-2 text-sm">
                            <p className="font-semibold">{p.platform}</p>
                            <p className="text-xs text-slate-600">{p.format_key}</p>
                            <select
                              value={p.status || "Draft"}
                              onClick={(ev) => ev.stopPropagation()}
                              onMouseDown={(ev) => ev.stopPropagation()}
                              onChange={(ev) => updateStatus(p.id, ev.target.value)}
                              className="mt-2 w-full rounded border border-slate-200 bg-white px-1 py-0.5 text-xs"
                            >
                              {STATUS_OPTIONS.map((s) => (
                                <option key={s} value={s}>
                                  {s}
                                </option>
                              ))}
                            </select>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {prov.placeholder}
                  </div>
                )}
              </Droppable>
            );
          })}
        </div>
      </DragDropContext>
    </div>
  );
}
