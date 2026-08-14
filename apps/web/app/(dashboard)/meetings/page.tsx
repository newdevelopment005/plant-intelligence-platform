"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Meeting {
  id: string;
  title: string;
  description: string | null;
  starts_at: string;
  ends_at: string | null;
  location: string | null;
  meeting_link: string | null;
  reminder_minutes_before: number;
  created_by: string;
  created_at: string;
  attendees?: { id: string; user_id: string | null; email: string | null; status: string }[];
}

const REMINDER_OPTIONS = [
  { value: "at_time", label: "At start time" },
  { value: "5m", label: "5 minutes before" },
  { value: "10m", label: "10 minutes before" },
  { value: "15m", label: "15 minutes before" },
  { value: "30m", label: "30 minutes before" },
  { value: "1h", label: "1 hour before" },
  { value: "1d", label: "1 day before" },
];

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showUpcomingOnly, setShowUpcomingOnly] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [form, setForm] = useState({
    title: "",
    description: "",
    starts_at: "",
    ends_at: "",
    location: "",
    meeting_link: "",
    reminder_option: "30m",
    attendee_emails: "",
  });
  const [creating, setCreating] = useState(false);
  const [sendingReminders, setSendingReminders] = useState(false);

  useEffect(() => {
    loadMeetings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadMeetings = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiClient.listMeetings();
      setMeetings(data?.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load meetings");
    } finally {
      setLoading(false);
    }
  };

  const loadMeetingDetail = async (meetingId: string) => {
    setLoadingDetail(true);
    setError("");
    try {
      const data = await apiClient.getMeeting(meetingId);
      setSelectedMeeting(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load meeting");
    } finally {
      setLoadingDetail(false);
    }
  };

  const notify = (message: string) => {
    setSuccess(message);
    setTimeout(() => setSuccess(""), 3500);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.starts_at) return;
    setCreating(true);
    setError("");
    try {
      const emails = form.attendee_emails
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const startsIso = form.starts_at ? new Date(form.starts_at).toISOString() : "";
      const endsIso = form.ends_at ? new Date(form.ends_at).toISOString() : undefined;
      await apiClient.createMeeting({
        title: form.title.trim(),
        starts_at: startsIso,
        description: form.description.trim() || undefined,
        ends_at: endsIso,
        location: form.location.trim() || undefined,
        meeting_link: form.meeting_link.trim() || undefined,
        reminder_option: form.reminder_option,
        attendee_emails: emails.length ? emails : undefined,
      });
      setForm({
        title: "",
        description: "",
        starts_at: "",
        ends_at: "",
        location: "",
        meeting_link: "",
        reminder_option: "30m",
        attendee_emails: "",
      });
      setShowCreateForm(false);
      notify("Meeting created");
      loadMeetings();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create meeting");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (meeting: Meeting) => {
    if (!window.confirm(`Delete meeting "${meeting.title}"?`)) return;
    setError("");
    try {
      await apiClient.deleteMeeting(meeting.id);
      notify("Meeting deleted");
      setSelectedMeeting(null);
      loadMeetings();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete meeting");
    }
  };

  const handleSendReminders = async () => {
    if (!selectedMeeting) return;
    setSendingReminders(true);
    setError("");
    try {
      const res = await apiClient.sendMeetingReminders(selectedMeeting.id);
      notify(res?.message || "Reminders sent");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send reminders");
    } finally {
      setSendingReminders(false);
    }
  };

  const handleUpdateAttendee = async (attendeeId: string, status: string) => {
    if (!selectedMeeting) return;
    setError("");
    try {
      await apiClient.updateAttendeeStatus(selectedMeeting.id, attendeeId, status);
      await loadMeetingDetail(selectedMeeting.id);
      notify(`Invitation ${status}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update invitation");
    }
  };

  const visibleMeetings = showUpcomingOnly
    ? meetings.filter((m) => new Date(m.starts_at) >= new Date())
    : meetings;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Meetings</h1>
          <p className="text-sm text-muted-foreground">
            Schedule team meetings and get email reminders.
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          {showCreateForm ? "Cancel" : "+ New Meeting"}
        </button>
      </div>

      {success && (
        <div className="rounded-md bg-green-50 p-4 text-sm text-green-800 dark:bg-green-900/20 dark:text-green-300">
          {success}
        </div>
      )}
      {error && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-300">
          {error}
        </div>
      )}

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={showUpcomingOnly}
          onChange={(e) => setShowUpcomingOnly(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300"
        />
        Show upcoming only
      </label>

      {showCreateForm && (
        <form
          onSubmit={handleCreate}
          className="space-y-4 rounded-lg border bg-card p-5 shadow-sm"
        >
          <h2 className="text-lg font-semibold">Schedule a meeting</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium">Title *</label>
              <input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
                placeholder="e.g. Weekly lab catch-up"
                required
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium">Description</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
                rows={2}
                placeholder="Agenda, objectives, notes..."
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Start *</label>
              <input
                type="datetime-local"
                value={form.starts_at}
                onChange={(e) => setForm({ ...form, starts_at: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">End</label>
              <input
                type="datetime-local"
                value={form.ends_at}
                onChange={(e) => setForm({ ...form, ends_at: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Location</label>
              <input
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
                placeholder="e.g. Lab 4 or Green 213"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Meeting link</label>
              <input
                value={form.meeting_link}
                onChange={(e) => setForm({ ...form, meeting_link: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
                placeholder="https://meet.example.com/..."
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Reminder</label>
              <select
                value={form.reminder_option}
                onChange={(e) => setForm({ ...form, reminder_option: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
              >
                {REMINDER_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Attendees (emails)</label>
              <input
                value={form.attendee_emails}
                onChange={(e) => setForm({ ...form, attendee_emails: e.target.value })}
                className="w-full rounded-md border px-3 py-2 text-sm"
                placeholder="name1@lab.edu, name2@lab.edu"
              />
            </div>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={creating}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {creating ? "Creating..." : "Schedule"}
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          {loading ? (
            <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
              Loading meetings...
            </div>
          ) : visibleMeetings.length === 0 ? (
            <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
              No meetings yet. Schedule one to get started.
            </div>
          ) : (
            visibleMeetings.map((meeting) => {
              const upcoming = new Date(meeting.starts_at) >= new Date();
              return (
                <div
                  key={meeting.id}
                  className="cursor-pointer rounded-lg border bg-card p-4 shadow-sm transition hover:border-primary/40"
                  onClick={() => loadMeetingDetail(meeting.id)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{meeting.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(meeting.starts_at)}
                        {meeting.location ? ` · ${meeting.location}` : ""}
                      </p>
                    </div>
                    <span
                      className={
                        upcoming
                          ? "inline-flex rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
                          : "inline-flex rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground"
                      }
                    >
                      {upcoming ? "Upcoming" : "Past"}
                    </span>
                  </div>
                  {meeting.description && (
                    <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
                      {meeting.description}
                    </p>
                  )}
                  <p className="mt-2 text-xs text-muted-foreground">
                    Reminder:{" "}
                    {meeting.reminder_minutes_before === 0
                      ? "at start time"
                      : meeting.reminder_minutes_before >= 1440
                        ? "1 day before"
                        : meeting.reminder_minutes_before >= 60
                          ? `${Math.round(meeting.reminder_minutes_before / 60)}h before`
                          : `${meeting.reminder_minutes_before}m before`}
                  </p>
                </div>
              );
            })
          )}
        </div>

        <div className="lg:col-span-1">
          {selectedMeeting ? (
            <div className="sticky top-6 space-y-4 rounded-lg border bg-card p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{selectedMeeting.title}</h3>
                <button
                  onClick={() => handleDelete(selectedMeeting)}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Delete
                </button>
              </div>
              <dl className="space-y-2 text-sm">
                <div>
                  <dt className="text-muted-foreground">When</dt>
                  <dd>{formatDate(selectedMeeting.starts_at)}</dd>
                </div>
                {selectedMeeting.location && (
                  <div>
                    <dt className="text-muted-foreground">Where</dt>
                    <dd>{selectedMeeting.location}</dd>
                  </div>
                )}
                {selectedMeeting.meeting_link && (
                  <div>
                    <dt className="text-muted-foreground">Link</dt>
                    <dd>
                      <a
                        href={selectedMeeting.meeting_link}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary underline"
                      >
                        Join
                      </a>
                    </dd>
                  </div>
                )}
                {selectedMeeting.description && (
                  <div>
                    <dt className="text-muted-foreground">Notes</dt>
                    <dd className="whitespace-pre-wrap">{selectedMeeting.description}</dd>
                  </div>
                )}
              </dl>
              <button
                onClick={handleSendReminders}
                disabled={sendingReminders}
                className="w-full rounded-lg bg-primary/10 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/20 disabled:opacity-50"
              >
                {sendingReminders ? "Sending..." : "Send reminders by email"}
              </button>

              <div>
                <p className="mb-2 text-sm font-medium">Attendees</p>
                {loadingDetail ? (
                  <p className="text-sm text-muted-foreground">Loading...</p>
                ) : selectedMeeting.attendees && selectedMeeting.attendees.length > 0 ? (
                  <ul className="space-y-2">
                    {selectedMeeting.attendees.map((a) => (
                      <li
                        key={a.id}
                        className="flex items-center justify-between gap-2 rounded-md border px-3 py-2 text-sm"
                      >
                        <span className="min-w-0 truncate">
                          {a.email || (a.user_id ? "Registered user" : "No email")}
                        </span>
                        {a.status === "pending" && (
                          <span className="flex shrink-0 gap-1">
                            <button
                              onClick={() => handleUpdateAttendee(a.id, "accepted")}
                              className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 hover:bg-green-200"
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => handleUpdateAttendee(a.id, "declined")}
                              className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 hover:bg-red-200"
                            >
                              Decline
                            </button>
                          </span>
                        )}
                        {a.status === "accepted" && (
                          <span className="shrink-0 text-xs font-medium text-green-600">Accepted</span>
                        )}
                        {a.status === "declined" && (
                          <span className="shrink-0 text-xs font-medium text-red-600">Declined</span>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">No attendees invited.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
              Select a meeting to view details and manage reminders.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}