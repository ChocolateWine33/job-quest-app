const token = localStorage.getItem("jobQuestToken");

const dashboardMessage = document.querySelector("#dashboard-message");
const applicationsList = document.querySelector("#applications-list");
const applicationCount = document.querySelector("#application-count");
const cvForm = document.querySelector("#cv-form");
const cvResult = document.querySelector("#cv-result");
const currentCvName = document.querySelector("#current-cv-name");
const currentCvLink = document.querySelector("#current-cv-link");
const applicationForm = document.querySelector("#application-form");
const applicationResult = document.querySelector("#application-result");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatMessages = document.querySelector("#chat-messages");
const chatStatus = document.querySelector("#chat-status");

document.querySelector("#signed-in-email").textContent =
  localStorage.getItem("jobQuestEmail") || "Adventurer";

function showMessage(element, message, type = "") {
  element.textContent = message;
  element.classList.remove("success", "error");
  if (type) {
    element.classList.add(type);
  }
}

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => `${item.loc.slice(1).join(".")}: ${item.msg}`)
      .join("; ");
  }

  return typeof detail === "string" ? detail : "Please try again.";
}

function getCurrentCvStorageKey() {
  let email = localStorage.getItem("jobQuestEmail");
  if (!email) {
    try {
      const encodedPayload = token.split(".")[1]
        .replace(/-/g, "+")
        .replace(/_/g, "/")
        .padEnd(Math.ceil(token.split(".")[1].length / 4) * 4, "=");
      email = JSON.parse(atob(encodedPayload)).sub;
    } catch (error) {
      console.error("Could not read the account email from the login token.", error);
      return null;
    }
  }

  return typeof email === "string" && email
    ? `jobQuestCurrentCv:${email.trim().toLowerCase()}`
    : null;
}

function renderCurrentCv(cvRecord = null) {
  let cv = cvRecord;

  if (!cv) {
    const storageKey = getCurrentCvStorageKey();
    const savedCv = storageKey ? localStorage.getItem(storageKey) : null;
    if (savedCv) {
      try {
        cv = JSON.parse(savedCv);
      } catch (error) {
        console.error("Could not read the saved CV details.", error);
      }
    }
  }

  if (!cv) {
    currentCvName.textContent = "No CV uploaded in this browser yet";
    currentCvLink.hidden = true;
    return;
  }

  try {
    const url = new URL(cv.url);
    if (url.protocol !== "https:") {
      throw new Error("The saved CV link is not a secure URL.");
    }

    currentCvName.textContent = cv.name;
    currentCvLink.href = url.href;
    currentCvLink.hidden = false;
  } catch (error) {
    console.error("Could not display the saved CV link.", error);
    currentCvName.textContent = "Saved CV link unavailable";
    currentCvLink.hidden = true;
  }
}

async function apiRequest(path, { method = "GET", body } = {}) {
  const headers = {
    "Authorization": `Bearer ${token}`
  };
  let requestBody;

  if (body instanceof FormData) {
    requestBody = body;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(`${window.API_URL}${path}`, {
    method,
    headers,
    body: requestBody
  });
  const data = await response.json();

  if (response.status === 401) {
    localStorage.removeItem("jobQuestToken");
    localStorage.removeItem("jobQuestEmail");
    window.location.replace("login.html");
    throw new Error("Your session expired. Please log in again.");
  }

  if (!response.ok) {
    throw new Error(`Request failed (${response.status}): ${formatDetail(data.detail)}`);
  }

  return data;
}

function renderProgress(progress) {
  const level = progress.level.level;
  const currentXp = progress.level.current_xp;
  const unlockedTitles = progress.unlocked_titles || [];

  document.querySelector("#current-title").textContent =
    progress.title || "New Adventurer";
  document.querySelector("#titles-unlocked").textContent =
    `${unlockedTitles.length} title${unlockedTitles.length === 1 ? "" : "s"} unlocked`;
  document.querySelector("#current-level").textContent = `Level ${level}`;
  document.querySelector("#xp-label").textContent =
    `${currentXp} / 100 XP to the next level`;
  document.querySelector("#current-streak").textContent =
    `${progress.streak} ${progress.streak === 1 ? "day" : "days"}`;

  const xpProgress = document.querySelector("#xp-progress");
  xpProgress.setAttribute("aria-valuenow", String(currentXp));
  document.querySelector("#xp-fill").style.width = `${currentXp}%`;
}

function createStatusSelect(application) {
  const select = document.createElement("select");
  select.className = "status-select";
  select.setAttribute("aria-label", `Status for ${application.company_name}`);

  for (const status of ["Applied", "Interview", "Rejected", "Offer"]) {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = status;
    option.selected = application.status === status;
    select.append(option);
  }

  return select;
}

function addAnalysisList(parent, headingText, items, formatItem = (item) => item) {
  if (!items.length) {
    return;
  }

  const heading = document.createElement("h4");
  heading.textContent = headingText;
  const list = document.createElement("ul");

  for (const item of items) {
    const listItem = document.createElement("li");
    listItem.textContent = formatItem(item);
    list.append(listItem);
  }

  parent.append(heading, list);
}

function createAnalysisDetails(analysis) {
  const details = document.createElement("details");
  details.className = "analysis-details";
  details.open = true;

  const summary = document.createElement("summary");
  summary.textContent = "Job match analysis";
  const fitBadge = document.createElement("span");
  fitBadge.className = `fit-badge fit-${analysis.fit_level}`;
  fitBadge.textContent = `${analysis.fit_level} fit`;

  const fitReason = document.createElement("p");
  fitReason.textContent = analysis.fit_reason;
  details.append(summary, fitBadge, fitReason);

  addAnalysisList(details, "Matching strengths", analysis.strengths || []);
  addAnalysisList(
    details,
    "CV improvements",
    analysis.cv_edits || [],
    (edit) => `${edit.section}: ${edit.suggestion} Why: ${edit.reason}`
  );
  addAnalysisList(
    details,
    "Skills to build",
    analysis.skills_to_learn || [],
    (gap) => `${gap.skill}: ${gap.why_it_matters}`
  );

  const trackHeading = document.createElement("h4");
  trackHeading.textContent = analysis.is_track_mismatch
    ? "Career direction check"
    : "Career direction";
  const trackNote = document.createElement("p");
  trackNote.textContent = analysis.track_note;
  details.append(trackHeading, trackNote);

  return details;
}

function createAnalysisControls(application) {
  const container = document.createElement("div");
  const button = document.createElement("button");
  button.className = "button secondary small-button analysis-button";
  button.type = "button";
  const status = document.createElement("p");
  status.className = "inline-message";

  if (!application.job_description) {
    button.textContent = "Analysis needs a job description";
    button.disabled = true;
    status.textContent = "Add a job description when creating an application to analyze its match.";
  } else {
    button.textContent = "Analyze job match";
    if (application.application_analysis) {
      try {
        container.append(createAnalysisDetails(JSON.parse(application.application_analysis)));
        button.textContent = "Refresh analysis";
      } catch (error) {
        console.error("Could not read the saved application analysis.", error);
        status.textContent = "The saved analysis could not be displayed. You can generate a fresh one.";
      }
    }

    button.addEventListener("click", async () => {
      button.disabled = true;
      button.classList.add("is-loading");
      button.textContent = "Reading the stars…";
      showMessage(status, "Your companion is comparing your CV with this role…");

      try {
        const analysis = await apiRequest(
          `/application_analysis/${application.id}`,
          { method: "POST" }
        );
        container.querySelector(".analysis-details")?.remove();
        container.insertBefore(createAnalysisDetails(analysis), status);
        showMessage(status, "Analysis ready.", "success");
        button.textContent = "Refresh analysis";
      } catch (error) {
        showMessage(status, error.message, "error");
      } finally {
        button.disabled = false;
        button.classList.remove("is-loading");
        button.textContent = button.dataset.idleText;
      }
    });
    button.dataset.idleText = button.textContent;
  }

  container.append(button, status);
  return container;
}

function renderApplications(applications) {
  applicationsList.replaceChildren();
  applicationCount.textContent =
    `${applications.length} ${applications.length === 1 ? "quest" : "quests"}`;

  if (applications.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent =
      "No applications yet. Add your first quest and start building momentum.";
    applicationsList.append(emptyState);
    return;
  }

  for (const application of applications) {
    const card = document.createElement("article");
    card.className = "application-card";

    const cardHeader = document.createElement("div");
    cardHeader.className = "application-card-header";

    const details = document.createElement("div");
    const company = document.createElement("h3");
    company.textContent = application.company_name;
    const role = document.createElement("p");
    role.className = "application-role";
    role.textContent = application.role_name;
    details.append(company, role);

    const statusBadge = document.createElement("span");
    statusBadge.className = `status-badge status-${application.status.toLowerCase()}`;
    statusBadge.textContent = application.status;
    cardHeader.append(details, statusBadge);

    const date = document.createElement("p");
    date.className = "application-date";
    date.textContent =
      `Applied ${new Date(`${application.apply_date}T00:00:00`).toLocaleDateString()}`;

    const controls = document.createElement("div");
    controls.className = "application-controls";
    const statusSelect = createStatusSelect(application);
    const updateButton = document.createElement("button");
    updateButton.className = "button secondary small-button";
    updateButton.type = "button";
    updateButton.textContent = "Save status";
    updateButton.addEventListener("click", async () => {
      updateButton.disabled = true;
      try {
        await apiRequest(`/update_application/${application.id}`, {
          method: "PATCH",
          body: { status: statusSelect.value }
        });
        await Promise.all([loadApplications(), loadProgress()]);
        showMessage(dashboardMessage, "Quest status updated.", "success");
      } catch (error) {
        showMessage(dashboardMessage, error.message, "error");
      } finally {
        updateButton.disabled = false;
      }
    });

    const deleteButton = document.createElement("button");
    deleteButton.className = "text-button";
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", async () => {
      if (!window.confirm(`Delete the ${application.role_name} quest at ${application.company_name}?`)) {
        return;
      }

      deleteButton.disabled = true;
      try {
        await apiRequest(`/delete_application/${application.id}`, { method: "DELETE" });
        await Promise.all([loadApplications(), loadProgress()]);
        showMessage(dashboardMessage, "Quest deleted.", "success");
      } catch (error) {
        showMessage(dashboardMessage, error.message, "error");
      } finally {
        deleteButton.disabled = false;
      }
    });

    const descriptionDetails = document.createElement("details");
    descriptionDetails.className = "description-editor";
    const descriptionSummary = document.createElement("summary");
    descriptionSummary.textContent = application.job_description
      ? "Edit job description"
      : "Add job description";
    const descriptionForm = document.createElement("form");
    descriptionForm.className = "description-form";

    const descriptionLabel = document.createElement("label");
    descriptionLabel.textContent = "Job description (300–10,000 characters)";
    const descriptionInput = document.createElement("textarea");
    descriptionInput.name = "job_description";
    descriptionInput.rows = 5;
    descriptionInput.minLength = 300;
    descriptionInput.maxLength = 10000;
    descriptionInput.required = true;
    descriptionInput.value = application.job_description || "";
    descriptionLabel.append(descriptionInput);

    const descriptionSave = document.createElement("button");
    descriptionSave.className = "button secondary small-button";
    descriptionSave.type = "submit";
    descriptionSave.textContent = "Save description";
    const descriptionStatus = document.createElement("p");
    descriptionStatus.className = "inline-message";
    descriptionForm.append(descriptionLabel, descriptionSave, descriptionStatus);
    descriptionForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      descriptionSave.disabled = true;
      showMessage(descriptionStatus, "Updating this quest…");

      try {
        await apiRequest(`/update_application/${application.id}`, {
          method: "PATCH",
          body: { job_description: descriptionInput.value.trim() }
        });
        await loadApplications();
        showMessage(dashboardMessage, "Job description updated.", "success");
      } catch (error) {
        showMessage(descriptionStatus, error.message, "error");
      } finally {
        descriptionSave.disabled = false;
      }
    });
    descriptionDetails.append(descriptionSummary, descriptionForm);

    controls.append(statusSelect, updateButton, deleteButton);
    card.append(
      cardHeader,
      date,
      controls,
      descriptionDetails,
      createAnalysisControls(application)
    );
    applicationsList.append(card);
  }
}

async function loadProgress() {
  const progress = await apiRequest("/progress");
  renderProgress(progress);
}

async function loadApplications() {
  const applications = await apiRequest("/get_applications");
  renderApplications(applications);
}

document.querySelector("#logout-button").addEventListener("click", () => {
  localStorage.removeItem("jobQuestToken");
  localStorage.removeItem("jobQuestEmail");
  window.location.replace("login.html");
});

cvForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = cvForm.querySelector('button[type="submit"]');
  showMessage(cvResult, "Uploading your CV…");
  submitButton.disabled = true;

  try {
    const file = cvForm.elements.cv_file.files[0];
    const data = await apiRequest("/upload", {
      method: "POST",
      body: new FormData(cvForm)
    });
    const storageKey = getCurrentCvStorageKey();
    const currentCv = {
      name: file.name,
      url: data.cv_url
    };
    renderCurrentCv(currentCv);
    let browserNote = "";
    if (storageKey) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(currentCv));
      } catch (error) {
        console.error("CV uploaded, but its link could not be saved in this browser.", error);
        browserNote = " The upload succeeded, but this browser could not remember the CV link.";
      }
    } else {
      browserNote = " The upload succeeded, but this browser could not remember the CV link.";
    }
    showMessage(
      cvResult,
      `${data.message} Your CV is ready for Job Quest's AI features.${browserNote}`,
      "success"
    );
    cvForm.reset();
  } catch (error) {
    showMessage(cvResult, error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

applicationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = applicationForm.querySelector('button[type="submit"]');
  showMessage(applicationResult, "Adding your new quest…");
  submitButton.disabled = true;

  const description = applicationForm.elements.job_description.value.trim();

  try {
    await apiRequest("/add_application", {
      method: "POST",
      body: {
        company_name: applicationForm.elements.company_name.value.trim(),
        role: applicationForm.elements.role.value.trim(),
        job_description: description || null
      }
    });
    applicationForm.reset();
    showMessage(applicationResult, "Quest added. Nice progress!", "success");
    await Promise.all([loadApplications(), loadProgress()]);
  } catch (error) {
    showMessage(applicationResult, error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

function appendChatBubble(message, sender, isError = false) {
  const bubble = document.createElement("p");
  bubble.className = `chat-bubble ${sender}-bubble`;
  if (isError) {
    bubble.classList.add("chat-error");
  }
  bubble.textContent = message;
  chatMessages.append(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

const aiPanel = document.querySelector("#ai-panel");
const aiToggle = document.querySelector("#ai-toggle");

function setChatOpen(isOpen) {
  aiPanel.hidden = !isOpen;
  aiToggle.setAttribute("aria-expanded", String(isOpen));
  if (isOpen) {
    chatInput.focus();
  }
}

aiToggle.addEventListener("click", () => {
  setChatOpen(aiPanel.hidden);
});

document.querySelector("#ai-close").addEventListener("click", () => {
  setChatOpen(false);
  aiToggle.focus();
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) {
    return;
  }

  const submitButton = chatForm.querySelector('button[type="submit"]');
  appendChatBubble(message, "user");
  chatInput.value = "";
  submitButton.disabled = true;
  chatForm.setAttribute("aria-busy", "true");
  showMessage(chatStatus, "Your companion is thinking…");

  try {
    const data = await apiRequest("/ask", {
      method: "POST",
      body: { content: message }
    });
    appendChatBubble(data.AI_assistant, "assistant");
    showMessage(chatStatus, "");
  } catch (error) {
    appendChatBubble(error.message, "assistant", true);
    showMessage(chatStatus, "That reply didn't make it. You can try again.", "error");
  } finally {
    submitButton.disabled = false;
    chatForm.removeAttribute("aria-busy");
    chatInput.focus();
  }
});

async function initializeDashboard() {
  if (!token) {
    window.location.replace("login.html");
    return;
  }

  renderCurrentCv();

  try {
    await Promise.all([loadProgress(), loadApplications()]);
    showMessage(dashboardMessage, "Your quest board is ready.", "success");
  } catch (error) {
    showMessage(dashboardMessage, error.message, "error");
  }
}

initializeDashboard();
