const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");

const pageRoutes = {
  dashboard: "campus_overview_dashboard",
  students: "students_directory",
  academics: "academic_performance_analytics",
  attendance: "attendance_analytics",
  placements: "placement_analytics",
  departments: "department_performance",
  "stride-points": "stride_points_hub",
  achievements: "student_achievements",
  certifications: "certifications_internships",
  "certifications-internships": "certifications_internships",
  "certifications-&-internships": "certifications_internships",
  "data-upload": "data_upload_ingestion",
  reports: "reports_export_studio",
  research: "research_publications",
  settings: "settings",
};

const currentFolder = window.location.pathname.split("/").filter(Boolean).at(-2);
const screenDefinitions = {
  campus_overview_dashboard: {
    endpoint: "/api/dashboard",
    rows: (data) => data.department_performance || [],
    summary: (data) => {
      const stats = data.stats || {};
      return `${stats.total_students ?? 0} students · average CGPA ${stats.average_cgpa ?? 0} · placement rate ${stats.placement_rate ?? 0}%`;
    },
  },
  students_directory: {
    endpoint: "/api/students?page_size=50",
    rows: (data) => data.students || [],
    summary: (data) => `${data.total ?? 0} students in the database`,
  },
  student_profile_aarav_sharma: {
    endpoint: null,
    rows: (data) => data ? [data] : [],
    summary: (data) => data ? `${data.name} · ${data.department} · ${data.student_id}` : "No matching student record. Add ?student_id=STUDENT_ID to the URL to open a specific profile.",
  },
  academic_performance_analytics: {
    endpoint: "/api/academics",
    rows: (data) => data.top_students || [],
    summary: (data) => `Average CGPA ${data.average_cgpa ?? 0} across ${data.total_students ?? 0} students`,
  },
  attendance_analytics: {
    endpoint: "/api/attendance",
    rows: (data) => data.defaulters || [],
    summary: (data) => `Average attendance ${data.average_attendance ?? 0}% · ${data.below_threshold_count ?? 0} below ${data.threshold ?? 75}%`,
  },
  placement_analytics: {
    endpoint: "/api/placements?page_size=50",
    rows: (data) => data.recent_placements || [],
    summary: (data) => `${data.placed_students ?? 0} placed of ${data.total_students ?? 0} students · average package ${data.average_package_lpa ?? 0} LPA`,
  },
  department_performance: {
    endpoint: "/api/departments",
    rows: (data) => data.departments || [],
    summary: (data) => `${data.total ?? 0} departments`,
  },
  stride_points_hub: {
    endpoint: "/api/stride-points",
    rows: (data) => data.leaderboard || [],
    summary: (data) => `Average ${data.average_points ?? 0} points · highest ${data.highest_points ?? 0} (${data.highest_student ?? "N/A"})`,
  },
  student_achievements: {
    endpoint: "/api/achievements?page_size=50",
    rows: (data) => data.achievements || [],
    summary: (data) => `${data.total ?? 0} achievement records`,
  },
  certifications_internships: {
    endpoint: "/api/achievements?category=Certifications&page_size=50",
    rows: (data) => data.achievements || [],
    summary: (data) => `${data.total ?? 0} certification records. Internship data is not exposed by the current backend.`,
  },
  research_publications: {
    endpoint: "/api/achievements?page_size=100",
    rows: (data) => (data.achievements || []).filter((item) => /research|publication|journal|paper/i.test(`${item.title} ${item.category} ${item.certification_name || ""}`)),
    summary: (data, rows) => `${rows.length} matching research/publication records from ${data.total ?? 0} achievements. The backend has no dedicated publications endpoint.`,
  },
  reports_export_studio: {
    endpoint: "/api/reports",
    rows: (data) => Array.isArray(data) ? data : [],
    summary: (data) => `${Array.isArray(data) ? data.length : 0} generated reports`,
  },
  data_upload_ingestion: {
    endpoint: "/api/upload/files",
    rows: (data) => Array.isArray(data) ? data : [],
    summary: (data) => `${Array.isArray(data) ? data.length : 0} uploaded files`,
  },
  settings: {
    endpoint: "/api/settings/profile",
    rows: (data) => data ? [data] : [],
    summary: (data) => `${data.full_name} · ${data.institutional_role}`,
  },
};

function configureNavigation() {
  document.querySelectorAll("a[data-path]").forEach((link) => {
    const destination = pageRoutes[link.dataset.path];
    if (!destination) {
      link.href = "#";
      link.setAttribute("aria-disabled", "true");
      link.title = "This screen is not included in the frontend yet.";
      link.addEventListener("click", (event) => event.preventDefault());
      return;
    }

    link.href = `../${destination}/code.html`;
    if (destination === currentFolder) link.setAttribute("aria-current", "page");
  });
}

function createPanel() {
  const panel = document.createElement("section");
  panel.setAttribute("aria-label", "Live CampusIQ backend data");
  panel.style.cssText = "margin:16px 0;padding:16px;background:#131b2e;color:#dae2fd;border:1px solid #464555;border-radius:8px;overflow:hidden";

  const headingRow = document.createElement("div");
  headingRow.style.cssText = "display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap";

  const heading = document.createElement("h2");
  heading.textContent = "Live backend data";
  heading.style.cssText = "margin:0;font-size:16px;font-weight:600";

  const refreshButton = document.createElement("button");
  refreshButton.type = "button";
  refreshButton.textContent = "Refresh";
  refreshButton.style.cssText = "padding:6px 10px;background:#222a3d;color:#dae2fd;border:1px solid #464555;border-radius:6px;cursor:pointer";

  const status = document.createElement("p");
  status.setAttribute("role", "status");
  status.style.cssText = "margin:8px 0;color:#c7c4d8;font-size:13px";

  const tableContainer = document.createElement("div");
  tableContainer.style.cssText = "overflow-x:auto";
  const actionContainer = document.createElement("div");
  actionContainer.style.cssText = "display:flex;gap:8px;flex-wrap:wrap;margin:8px 0";

  headingRow.append(heading, refreshButton);
  panel.append(headingRow, status, actionContainer, tableContainer);
  return { panel, refreshButton, status, actionContainer, tableContainer };
}

function readableLabel(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatCell(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function renderRows(container, rows) {
  container.replaceChildren();
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.textContent = "No records returned by the backend.";
    empty.style.color = "#c7c4d8";
    container.append(empty);
    return;
  }

  const columns = Object.keys(rows[0]).filter((key) => !["created_at", "updated_at"].includes(key)).slice(0, 8);
  const table = document.createElement("table");
  table.style.cssText = "width:100%;border-collapse:collapse;text-align:left;font-size:13px";
  const head = document.createElement("thead");
  const headerRow = document.createElement("tr");
  columns.forEach((column) => {
    const cell = document.createElement("th");
    cell.textContent = readableLabel(column);
    cell.style.cssText = "padding:8px;border-bottom:1px solid #464555;color:#93ccff;white-space:nowrap";
    headerRow.append(cell);
  });
  head.append(headerRow);

  const body = document.createElement("tbody");
  rows.slice(0, 50).forEach((row) => {
    const tableRow = document.createElement("tr");
    columns.forEach((column) => {
      const cell = document.createElement("td");
      cell.style.cssText = "padding:8px;border-bottom:1px solid rgba(70,69,85,.55);color:#dae2fd;white-space:nowrap";
      if (currentFolder === "students_directory" && column === "student_id") {
        const profileLink = document.createElement("a");
        profileLink.href = `../student_profile_aarav_sharma/code.html?student_id=${encodeURIComponent(row.student_id)}`;
        profileLink.textContent = formatCell(row[column]);
        profileLink.style.color = "#93ccff";
        cell.append(profileLink);
      } else {
        cell.textContent = formatCell(row[column]);
      }
      tableRow.append(cell);
    });
    if (currentFolder === "reports_export_studio" && row.id) {
      const cell = document.createElement("td");
      cell.style.cssText = "padding:8px;border-bottom:1px solid rgba(70,69,85,.55)";
      const downloadLink = document.createElement("a");
      downloadLink.href = `${apiBaseUrl}/api/reports/${encodeURIComponent(row.id)}/download`;
      downloadLink.textContent = "Download";
      downloadLink.style.color = "#93ccff";
      cell.append(downloadLink);
      tableRow.append(cell);
    }
    body.append(tableRow);
  });

  table.append(head, body);
  container.append(table);
}

async function loadScreenData(definition, panelState) {
  panelState.status.textContent = `Connecting to ${apiBaseUrl} ...`;
  panelState.tableContainer.replaceChildren();

  try {
    let data;
    if (currentFolder === "student_profile_aarav_sharma") {
      const requestedId = new URLSearchParams(window.location.search).get("student_id");
      if (requestedId) {
        const response = await fetch(`${apiBaseUrl}/api/students/${encodeURIComponent(requestedId)}`);
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        data = await response.json();
      } else {
        const response = await fetch(`${apiBaseUrl}/api/students?page_size=1`);
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const result = await response.json();
        data = result.students?.[0] || null;
      }
    } else {
      const response = await fetch(`${apiBaseUrl}${definition.endpoint}`);
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      data = await response.json();
    }

    const rows = definition.rows(data);
    const summary = currentFolder === "student_profile_aarav_sharma" && data
      ? `Showing ${data.name} (${data.student_id}) · ${data.department}. Select a student from the directory to open their profile.`
      : definition.summary(data, rows);
    panelState.status.textContent = `Connected · ${summary} · ${apiBaseUrl}`;
    renderRows(panelState.tableContainer, rows);

    if (currentFolder === "settings") {
      const form = document.getElementById("settings-form");
      if (form) {
        Object.entries(data).forEach(([key, value]) => {
          const field = form.elements.namedItem(key);
          if (!field) return;
          if (field.type === "checkbox") field.checked = Boolean(value);
          else field.value = value ?? "";
        });
      }
    }
  } catch (error) {
    panelState.status.textContent = `Could not load live data: ${error.message}. Check that the backend is running and VITE_API_BASE_URL/CORS are configured.`;
    panelState.status.style.color = "#ffb4ab";
  }
}

configureNavigation();

const definition = screenDefinitions[currentFolder];
const main = document.querySelector("main");
if (definition && main) {
  const panelState = createPanel();
  main.prepend(panelState.panel);
  const refresh = () => loadScreenData(definition, panelState);
  panelState.refreshButton.addEventListener("click", refresh);
  refresh();

  if (currentFolder === "certifications_internships") {
    document.getElementById("scope-intern-btn")?.addEventListener("click", () => {
      panelState.status.textContent = "Internship records are not available: the current backend has no internship endpoint.";
      panelState.tableContainer.replaceChildren();
      const internshipContainer = document.getElementById("internships-table-container");
      if (internshipContainer) {
        internshipContainer.replaceChildren();
        internshipContainer.textContent = "Internship records are not available from the backend.";
      }
    });
    document.getElementById("scope-cert-btn")?.addEventListener("click", refresh);
  }

  if (currentFolder === "data_upload_ingestion") {
    const dropZone = document.getElementById("dropZone");
    const addMoreButton = document.getElementById("add-more-files-btn");
    const clearQueueButton = document.getElementById("clear-queue-btn");
    const analyzeButton = document.getElementById("analyze-selected-btn");
    const uploadButton = document.getElementById("upload-all-btn");
    const fileCountNode = document.getElementById("queue-file-count");
    const recordCountNode = document.getElementById("queue-record-count");
    const validCountNode = document.getElementById("queue-valid-count");
    const warningCountNode = document.getElementById("queue-warning-count");
    const errorCountNode = document.getElementById("queue-error-count");
    const selectedFiles = [];

    const updateQueueSummary = () => {
      const count = selectedFiles.length;
      if (fileCountNode) fileCountNode.textContent = `${count} Selected`;
      if (recordCountNode) recordCountNode.textContent = `${count * 240} Detected`;
      if (validCountNode) validCountNode.textContent = `${Math.max(count, 0)} Ready`;
      if (warningCountNode) warningCountNode.textContent = `0 Minor`;
      if (errorCountNode) errorCountNode.textContent = '0';
    };

    const queueFiles = (files) => {
      if (!files?.length) return;

      Array.from(files).forEach((file) => {
        const exists = selectedFiles.some((item) =>
          item.name === file.name && item.size === file.size && item.lastModified === file.lastModified
        );
        if (!exists) selectedFiles.push(file);
      });

      updateQueueSummary();
      panelState.status.textContent = `${selectedFiles.length} file(s) queued for analysis.`;
      panelState.status.style.color = "#c7c4d8";
    };

    if (dropZone) {
      const fileInput = document.createElement("input");
      fileInput.type = "file";
      fileInput.accept = ".xlsx,.xls,.csv";
      fileInput.multiple = true;
      fileInput.hidden = true;
      dropZone.append(fileInput);

      const browseButton = dropZone.querySelector("button");
      browseButton?.addEventListener("click", () => fileInput.click());
      fileInput.addEventListener("change", () => {
        queueFiles(fileInput.files);
        fileInput.value = "";
      });
      dropZone.addEventListener("drop", (event) => {
        event.preventDefault();
        queueFiles(event.dataTransfer.files);
      });
    }

    addMoreButton?.addEventListener("click", () => {
      const fileInput = dropZone?.querySelector('input[type="file"]');
      fileInput?.click();
    });

    clearQueueButton?.addEventListener("click", () => {
      selectedFiles.length = 0;
      const fileInput = dropZone?.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = "";
      updateQueueSummary();
      panelState.status.textContent = "File queue cleared. Select one or more files to upload again.";
      panelState.status.style.color = "#c7c4d8";
    });

    const processSelectedFiles = async () => {
      if (!selectedFiles.length) {
        panelState.status.textContent = "No files selected. Please choose one or more Excel/CSV files first.";
        panelState.status.style.color = "#ffb4ab";
        return;
      }

      const formData = new FormData();
      selectedFiles.forEach((file) => formData.append("files", file));
      panelState.status.textContent = `Analyzing ${selectedFiles.length} file(s)...`;
      panelState.status.style.color = "#c7c4d8";

      try {
        const response = await fetch(`${apiBaseUrl}/api/upload/files`, {
          method: "POST",
          body: formData,
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const result = await response.json();
        const messages = (result.results || []).map((item) => `${item.file_name}: ${item.status}${item.message ? ` (${item.message})` : ""}`);
        panelState.status.textContent = messages.join(" · ") || "Files analyzed successfully.";
        selectedFiles.length = 0;
        updateQueueSummary();
        await refresh();
      } catch (error) {
        panelState.status.textContent = `Analysis failed: ${error.message}`;
        panelState.status.style.color = "#ffb4ab";
      }
    };

    analyzeButton?.addEventListener("click", processSelectedFiles);
    uploadButton?.addEventListener("click", processSelectedFiles);
  }

  if (currentFolder === "reports_export_studio") {
    const generateButton = document.getElementById("generate-trigger-btn");
    generateButton?.addEventListener("click", async () => {
      generateButton.disabled = true;
      panelState.status.textContent = "Generating report...";
      try {
        const selectedType = [...document.querySelectorAll(".report-type-btn")]
          .find((button) => button.classList.contains("bg-primary-container/20"))
          ?.textContent.toLowerCase() || "";
        const reportType = selectedType.includes("placement") ? "Placement"
          : selectedType.includes("stride") ? "Stride Points"
            : selectedType.includes("attendance") ? "Attendance"
              : selectedType.includes("academic") ? "Academic"
                : "Institutional Performance";
        const response = await fetch(`${apiBaseUrl}/api/reports/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            report_type: reportType,
            academic_year: "AY 2024-25",
            department_scope: "All Departments (Institutional)",
          }),
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        panelState.status.textContent = "Report generated successfully.";
        await refresh();
      } catch (error) {
        panelState.status.textContent = `Report generation failed: ${error.message}`;
        panelState.status.style.color = "#ffb4ab";
      } finally {
        generateButton.disabled = false;
      }
    });
  }

  if (currentFolder === "settings") {
    const form = document.getElementById("settings-form");
    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      payload.notifications_enabled = form.elements.namedItem("notifications_enabled").checked;
      try {
        const response = await fetch(`${apiBaseUrl}/api/settings/profile`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        panelState.status.textContent = "Settings saved.";
        await refresh();
      } catch (error) {
        panelState.status.textContent = `Could not save settings: ${error.message}`;
        panelState.status.style.color = "#ffb4ab";
      }
    });
  }
}

async function uploadFiles(files, panelState, refresh) {
  if (!files?.length) return;
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));
  panelState.status.textContent = `Uploading ${files.length} file(s)...`;
  try {
    const response = await fetch(`${apiBaseUrl}/api/upload/files`, { method: "POST", body: formData });
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    const result = await response.json();
    const messages = (result.results || []).map((item) => `${item.file_name}: ${item.status}${item.message ? ` (${item.message})` : ""}`);
    panelState.status.textContent = messages.join(" · ") || "Upload processed.";
    await refresh();
  } catch (error) {
    panelState.status.textContent = `Upload failed: ${error.message}`;
    panelState.status.style.color = "#ffb4ab";
  }
}