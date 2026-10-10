export const exportTasksToCSV = (tasks = [], filename = "tasknova-academic-ledger.csv") => {
  if (!tasks.length) return;

  const headers = ["ID", "Title", "Course / Project", "Status", "Priority", "Due Date", "Description"];

  const escapeCsv = (str) => {
    if (str === null || str === undefined) return '""';
    let text = String(str);

    if (/^[=+\-@\t\r]/.test(text)) {
      text = `'${text}`;
    }
    const escaped = text.replace(/"/g, '""');
    return `"${escaped}"`;
  };

  const rows = tasks.map((t) => [
    escapeCsv(t.id),
    escapeCsv(t.title),
    escapeCsv(t.project_name || "Unassigned"),
    escapeCsv(t.status),
    escapeCsv(t.priority),
    escapeCsv(t.due_date ? new Date(t.due_date).toLocaleString() : "No Deadline"),
    escapeCsv(t.description || "")
  ]);

  const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const exportTasksToICS = (tasks = [], calendarName = "TaskNova Academic Deadlines") => {
  if (!tasks.length) return;

  const formatDateToICS = (date) => {
    const d = new Date(date);
    return d.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
  };

  const events = tasks
    .filter((t) => t.due_date)
    .map((t) => {
      const nowFormatted = formatDateToICS(new Date());
      const dueFormatted = formatDateToICS(t.due_date);
      const title = t.title.replace(/[\r\n]+/g, " ");
      const desc = (t.description || "").replace(/[\r\n]+/g, "\\n");
      const course = t.project_name || "General";

      return [
        "BEGIN:VEVENT",
        `UID:task-${t.id}@tasknova.academic`,
        `DTSTAMP:${nowFormatted}`,
        `DTSTART:${dueFormatted}`,
        `DTEND:${dueFormatted}`,
        `SUMMARY:[${course}] ${title}`,
        `DESCRIPTION:${desc}\\n\\nStatus: ${t.status}\\nPriority: ${t.priority}`,
        `CATEGORIES:${course},Academics`,
        "STATUS:CONFIRMED",
        "END:VEVENT"
      ].join("\r\n");
    });

  if (!events.length) {
    alert("No tasks with scheduled due dates were found to export to calendar.");
    return;
  }

  const icsContent = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//TaskNova//Academic Workplace//EN",
    `X-WR-CALNAME:${calendarName}`,
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    ...events,
    "END:VCALENDAR"
  ].join("\r\n");

  const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `${calendarName.toLowerCase().replace(/\s+/g, "-")}.ics`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const printAcademicLedger = (tasks = [], scopeName = "All Courses") => {
  if (!tasks || !tasks.length) return;

  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.right = "0";
  iframe.style.bottom = "0";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "0";
  document.body.appendChild(iframe);

  const doc = iframe.contentWindow.document;
  const nowStr = new Date().toLocaleString(undefined, { dateStyle: "full", timeStyle: "short" });

  const total = tasks.length;
  const done = tasks.filter((t) => t.status === "done").length;
  const inProgress = tasks.filter((t) => t.status === "in_progress").length;
  const todo = tasks.filter((t) => t.status === "todo").length;

  const escapeHtml = (text) => {
    if (!text) return "";
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  };

  const rowsHtml = tasks
    .map((t) => {
      const isDone = t.status === "done";
      const statusLabel = isDone ? "COMPLETED" : t.status === "in_progress" ? "IN PROGRESS" : "TO DO";
      const statusBg = isDone ? "#ecfdf5" : t.status === "in_progress" ? "#fef3c7" : "#f1f5f9";
      const statusColor = isDone ? "#047857" : t.status === "in_progress" ? "#b45309" : "#475569";
      const priorityColor = t.priority === "high" ? "#dc2626" : t.priority === "medium" ? "#d97706" : "#64748b";
      const dueDate = t.due_date ? new Date(t.due_date).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) : "No deadline";

      const descHtml = t.description ? `<div style="font-size: 8.5pt; color: #475569; margin-top: 4px; white-space: pre-wrap;">${escapeHtml(t.description)}</div>` : "";

      return `
        <tr style="page-break-inside: avoid; break-inside: avoid;">
          <td style="width: 32px; text-align: center; vertical-align: top; padding: 8px 6px; border-bottom: 1px solid #e2e8f0;">
            <div style="width: 14px; height: 14px; border: 1.5px solid #64748b; border-radius: 3px; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; color: #047857;">
              ${isDone ? "✓" : ""}
            </div>
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top;">
            <div style="font-weight: 700; font-size: 9.5pt; color: ${isDone ? '#64748b; text-decoration: line-through;' : '#0f172a;'}">${escapeHtml(t.title)}</div>
            ${descHtml}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; font-size: 8.5pt; font-weight: 600; color: #334155;">
            ${escapeHtml(t.project_name || "General")}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; font-size: 8pt; font-weight: 700; color: ${priorityColor}; text-transform: uppercase;">
            ${escapeHtml(t.priority || "MEDIUM")}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; font-size: 8.5pt; color: #334155; white-space: nowrap;">
            ${dueDate}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; white-space: nowrap;">
            <span style="display: inline-block; padding: 2px 6px; font-size: 7.5pt; font-weight: 700; border-radius: 4px; background: ${statusBg}; color: ${statusColor};">
              ${statusLabel}
            </span>
          </td>
        </tr>
      `;
    })
    .join("");

  doc.open();
  doc.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>TaskNova Academic Ledger - ${escapeHtml(scopeName)}</title>
        <style>
          @page {
            size: A4 portrait;
            margin: 12mm 15mm;
          }
          * { box-sizing: border-box; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a;
            background: #ffffff;
            margin: 0;
            padding: 0;
          }
          .header {
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 12px;
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
          }
          .brand-title {
            font-size: 16pt;
            font-weight: 800;
            color: #1e1b4b;
            letter-spacing: -0.5px;
          }
          .brand-sub {
            font-size: 9pt;
            font-weight: 600;
            color: #4f46e5;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 2px;
          }
          .meta {
            text-align: right;
            font-size: 8pt;
            color: #64748b;
          }
          .summary-bar {
            display: flex;
            gap: 12px;
            margin-bottom: 14px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 8.5pt;
          }
          .summary-item {
            font-weight: 600;
            color: #334155;
          }
          .summary-item strong {
            color: #0f172a;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            font-size: 9pt;
          }
          th {
            background: #f1f5f9;
            color: #334155;
            font-weight: 700;
            font-size: 8pt;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-align: left;
            padding: 7px 10px;
            border-top: 1px solid #cbd5e1;
            border-bottom: 2px solid #cbd5e1;
          }
          tr {
            page-break-inside: avoid;
            break-inside: avoid;
          }
          .footer {
            margin-top: 20px;
            border-top: 1px solid #e2e8f0;
            padding-top: 8px;
            font-size: 7.5pt;
            color: #94a3b8;
            display: flex;
            justify-content: space-between;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="brand-title">TaskNova · Academic Assignment Ledger</div>
            <div class="brand-sub">${escapeHtml(scopeName || "Comprehensive Course Roster")}</div>
          </div>
          <div class="meta">
            <div><strong>Generated:</strong> ${nowStr}</div>
            <div><strong>Status:</strong> Verified Academic Record</div>
          </div>
        </div>

        <div class="summary-bar">
          <div class="summary-item">Total Tasks: <strong>${total}</strong></div>
          <div class="summary-item">To Do: <strong>${todo}</strong></div>
          <div class="summary-item">In Progress: <strong>${inProgress}</strong></div>
          <div class="summary-item">Completed: <strong>${done}</strong></div>
        </div>

        <table>
          <thead>
            <tr>
              <th style="width: 32px; text-align: center;">✓</th>
              <th>Assignment & Syllabus Notes</th>
              <th>Course</th>
              <th>Priority</th>
              <th>Deadline</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>

        <div class="footer">
          <span>TaskNova Academic Workplace Suite</span>
          <span>Official Printable Assignment Document</span>
        </div>
      </body>
    </html>
  `);
  doc.close();

  setTimeout(() => {
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
    setTimeout(() => {
      document.body.removeChild(iframe);
    }, 2000);
  }, 250);
};

export const printDailyDigest = (digest = {}, dateStr = "") => {
  if (!digest) return;

  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.right = "0";
  iframe.style.bottom = "0";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "0";
  document.body.appendChild(iframe);

  const doc = iframe.contentWindow.document;
  const nowStr = new Date().toLocaleString(undefined, { dateStyle: "full", timeStyle: "short" });

  const total = digest.total_tasks || 0;
  const completed = digest.completed_tasks || 0;
  const inProgress = digest.in_progress_tasks || 0;
  const overdue = digest.overdue_tasks || 0;
  const rate = digest.completion_rate || (total > 0 ? Math.round((completed / total) * 100) : 0);
  const grade = digest.grade || "A";
  const momentum = digest.momentum || "Active Progress";
  const quote = digest.quote || "Consistent daily study sprints build unstoppable academic momentum.";
  const displayDate = dateStr || digest.report_date || "Today's Productivity Digest";

  const escapeHtml = (text) => {
    if (!text) return "";
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  };

  const courses = Array.isArray(digest.courses) ? digest.courses : [];
  const courseRowsHtml = courses
    .map((c) => {
      const cTotal = c.total || 0;
      const cComp = c.completed || 0;
      const cRate = c.completion_rate || (cTotal > 0 ? Math.round((cComp / cTotal) * 100) : 0);
      const cOverdue = c.overdue || 0;
      return `
        <tr style="page-break-inside: avoid; break-inside: avoid;">
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-weight: 700; color: #0f172a; font-size: 9pt;">
            ${escapeHtml(c.name || "Course")}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: center; font-size: 9pt; color: #334155;">
            ${cTotal}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: center; font-size: 9pt; font-weight: 700; color: #047857;">
            ${cComp}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: center; font-size: 9pt; font-weight: 700; color: ${cOverdue > 0 ? '#dc2626' : '#64748b'};">
            ${cOverdue}
          </td>
          <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-size: 9pt; font-weight: 700; color: #4338ca;">
            ${cRate}%
          </td>
        </tr>
      `;
    })
    .join("");

  const courseTableHtml = courses.length
    ? `
      <div style="margin-top: 18px;">
        <div style="font-size: 9pt; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; margin-bottom: 8px;">
          Course Breakdown
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 8.5pt;">
          <thead>
            <tr style="background: #f8fafc;">
              <th style="padding: 6px 10px; text-align: left; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #475569;">Course</th>
              <th style="padding: 6px 10px; text-align: center; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #475569;">Total</th>
              <th style="padding: 6px 10px; text-align: center; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #475569;">Completed</th>
              <th style="padding: 6px 10px; text-align: center; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #475569;">Overdue</th>
              <th style="padding: 6px 10px; text-align: right; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #475569;">Progress</th>
            </tr>
          </thead>
          <tbody>
            ${courseRowsHtml}
          </tbody>
        </table>
      </div>
    `
    : "";

  doc.open();
  doc.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Daily Productivity Digest · TaskNova</title>
        <style>
          @page {
            size: portrait;
            margin: 12mm 14mm;
          }
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a;
            background: #ffffff;
            line-height: 1.4;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 12px;
            margin-bottom: 14px;
          }
          .brand-title {
            font-size: 15pt;
            font-weight: 900;
            color: #1e1b4b;
            letter-spacing: -0.02em;
          }
          .brand-sub {
            font-size: 9pt;
            color: #4f46e5;
            font-weight: 700;
            margin-top: 2px;
          }
          .meta {
            text-align: right;
            font-size: 8pt;
            color: #64748b;
          }
          .grade-badge {
            display: inline-block;
            background: #4f46e5;
            color: #ffffff;
            font-weight: 900;
            font-size: 12pt;
            padding: 3px 10px;
            border-radius: 6px;
            margin-top: 4px;
          }
          .quote-box {
            background: #f1f5f9;
            border-left: 4px solid #6366f1;
            padding: 10px 14px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 14px;
          }
          .quote-title {
            font-size: 8pt;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #4f46e5;
            margin-bottom: 2px;
          }
          .quote-text {
            font-size: 9pt;
            font-style: italic;
            color: #334155;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 14px;
          }
          .card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
          }
          .card-label {
            font-size: 7.5pt;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 2px;
          }
          .card-val {
            font-size: 16pt;
            font-weight: 900;
            color: #0f172a;
          }
          .card-sub {
            font-size: 7.5pt;
            color: #64748b;
          }
          .progress-bar-container {
            background: #e2e8f0;
            border-radius: 9999px;
            height: 8px;
            overflow: hidden;
            margin: 6px 0 14px 0;
          }
          .progress-bar-fill {
            background: linear-gradient(90deg, #6366f1, #10b981);
            height: 100%;
            border-radius: 9999px;
          }
          .footer {
            margin-top: 20px;
            border-top: 1px solid #e2e8f0;
            padding-top: 8px;
            font-size: 7.5pt;
            color: #94a3b8;
            display: flex;
            justify-content: space-between;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="brand-title">TaskNova · Daily Productivity Digest</div>
            <div class="brand-sub">${escapeHtml(displayDate)}</div>
          </div>
          <div class="meta">
            <div>Academic Grade:</div>
            <div class="grade-badge">${escapeHtml(grade)}</div>
          </div>
        </div>

        <div class="quote-box">
          <div class="quote-title">Study Velocity: ${escapeHtml(momentum)}</div>
          <div class="quote-text">"${escapeHtml(quote)}"</div>
        </div>

        <div class="grid">
          <div class="card">
            <div class="card-label">Total Workload</div>
            <div class="card-val">${total}</div>
            <div class="card-sub">assignments</div>
          </div>
          <div class="card" style="border-color: #a7f3d0; background: #ecfdf5;">
            <div class="card-label" style="color: #047857;">Completed</div>
            <div class="card-val" style="color: #047857;">${completed}</div>
            <div class="card-sub" style="color: #059669; font-weight: 700;">${rate}% achieved</div>
          </div>
          <div class="card" style="border-color: #c7d2fe; background: #eef2ff;">
            <div class="card-label" style="color: #4338ca;">In Progress</div>
            <div class="card-val" style="color: #4338ca;">${inProgress}</div>
            <div class="card-sub" style="color: #4f46e5;">active study</div>
          </div>
          <div class="card" style="border-color: #fecdd3; background: #fff1f2;">
            <div class="card-label" style="color: #be123c;">Overdue</div>
            <div class="card-val" style="color: #be123c;">${overdue}</div>
            <div class="card-sub" style="color: #e11d48;">urgent action</div>
          </div>
        </div>

        <div style="font-size: 8pt; font-weight: 700; color: #475569; display: flex; justify-content: space-between;">
          <span>Semester Workload Completion</span>
          <span>${rate}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" style="width: ${Math.min(100, Math.max(0, rate))}%;"></div>
        </div>

        ${courseTableHtml}

        <div class="footer">
          <span>TaskNova Academic Workplace Suite</span>
          <span>Official Productivity Snapshot &bull; Printed ${nowStr}</span>
        </div>
      </body>
    </html>
  `);
  doc.close();

  setTimeout(() => {
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
    setTimeout(() => {
      document.body.removeChild(iframe);
    }, 2000);
  }, 250);
};
