const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const loginFeedback = document.getElementById("loginFeedback");
const registerFeedback = document.getElementById("registerFeedback");
const uploadZone = document.getElementById("uploadZone");
const resumeInput = document.getElementById("resumeInput");
const chooseFileButton = document.getElementById("chooseFileButton");
const uploadPreview = document.getElementById("uploadPreview");
const jobText = document.getElementById("jobText");
const analyzeButton = document.getElementById("analyzeButton");
const resultsDashboard = document.getElementById("resultsDashboard");
const scoreValue = document.getElementById("scoreValue");
const resumeSkillsCount = document.getElementById("resumeSkillsCount");
const jobSkillsCount = document.getElementById("jobSkillsCount");
const matchedSkillsCount = document.getElementById("matchedSkillsCount");
const resumeSkillsList = document.getElementById("resumeSkillsList");
const jobSkillsList = document.getElementById("jobSkillsList");
const resumeExperience = document.getElementById("resumeExperience");
const resumeEducation = document.getElementById("resumeEducation");
const jobExperience = document.getElementById("jobExperience");
const jobTitle = document.getElementById("jobTitle");
const suggestions = document.getElementById("suggestions");
const scrollToAnalyzer = document.getElementById("scrollToAnalyzer");

let selectedResumeFile = null;

function showToast(message, variant = "success") {
  const wrapper = document.createElement("div");
  wrapper.className = `alert alert-${variant} alert-fixed shadow-lg d-flex align-items-center gap-2`;
  wrapper.role = "alert";
  
  // Add dynamic icons to toasts based on variant
  const icon = variant === 'success' ? 'fa-circle-check' : (variant === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-xmark');
  wrapper.innerHTML = `<i class="fa-solid ${icon}"></i> <div>${message}</div>`;
  
  wrapper.style.transition = "opacity 0.25s ease";
  document.body.appendChild(wrapper);

  setTimeout(() => {
    wrapper.style.opacity = "0";
    setTimeout(() => wrapper.remove(), 300);
  }, 3000);
}

function setLoading(isLoading) {
  analyzeButton.disabled = isLoading;
  if (isLoading) {
    analyzeButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing...';
  } else {
    // Restores the original button text and icon from the new HTML
    analyzeButton.innerHTML = '<i class="fa-solid fa-magnifying-glass-chart me-2"></i> Calculate ATS Match';
  }
}

function setSelectedFile(file) {
  selectedResumeFile = file;
  if (file) {
    uploadPreview.innerHTML = `<i class="fa-solid fa-file-check me-1"></i> ${file.name} <span class="text-muted ms-1">(${(file.size / 1024).toFixed(1)} KB)</span>`;
  } else {
    uploadPreview.textContent = "";
  }
}

async function registerUser(email, password) {
  const response = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Registration failed");
  }

  return response.json();
}

async function loginUser(email, password) {
  const data = new FormData();
  data.append("username", email);
  data.append("password", password);

  const response = await fetch("/api/auth/login", {
    method: "POST",
    body: data,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Login failed");
  }

  return response.json();
}

function getAuthHeaders() {
  const token = localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function uploadResume(file) {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch("/api/resumes/upload", {
    method: "POST",
    body: form,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Resume upload failed");
  }

  return response.json();
}

async function pasteJob(text) {
  const form = new FormData();
  form.append("text", text);

  const response = await fetch("/api/jobs/paste", {
    method: "POST",
    body: form,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Job description submission failed");
  }

  return response.json();
}

// Updated to render Bootstrap Badges instead of plain list items
function updateList(element, items, fallback = "None detected") {
  element.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    const item = document.createElement("span");
    item.className = "text-muted small fst-italic";
    item.textContent = fallback;
    element.appendChild(item);
    return;
  }

  items.forEach((value) => {
    const badge = document.createElement("span");
    badge.className = "badge bg-primary bg-opacity-10 text-primary border border-primary-subtle px-3 py-2 fw-medium rounded-pill shadow-sm";
    badge.textContent = value;
    element.appendChild(badge);
  });
}

function calculateScore(resumeData, jobData) {
  const resumeSkills = Array.isArray(resumeData.skills) ? resumeData.skills : [];
  const jobSkills = Array.isArray(jobData.skills) ? jobData.skills : [];
  const sharedSkills = resumeSkills.filter((skill) => jobSkills.includes(skill));

  let score = 45 + sharedSkills.length * 12;
  const experienceGap = (jobData.experience_years || 0) - (resumeData.experience_years || 0);

  if (experienceGap <= 0) {
    score += 10;
  } else {
    score -= Math.min(experienceGap * 5, 20);
  }

  if (resumeSkills.length === 0) {
    score -= 10;
  }

  return Math.max(0, Math.min(100, Math.round(score)));
}

// Updated to return objects containing specific icons for dynamic rendering
function renderSuggestions(resumeData, jobData, sharedSkills) {
  const lines = [];
  if (sharedSkills.length === 0) {
    lines.push({
      icon: "fa-triangle-exclamation text-danger",
      text: "Your resume does not currently mention any of the job's detected skills. Add relevant keywords to improve ATS alignment."
    });
  } else {
    lines.push({
      icon: "fa-circle-check text-success",
      text: `Great! These skills match the job description: <span class="fw-bold">${sharedSkills.join(", ")}</span>.`
    });
  }

  const expGap = (jobData.experience_years || 0) - (resumeData.experience_years || 0);
  if (expGap > 0) {
    lines.push({
      icon: "fa-arrow-trend-up text-warning",
      text: `The job expects <strong>${jobData.experience_years} years</strong> of experience, but your resume shows <strong>${resumeData.experience_years}</strong>. Consider emphasizing related experience.`
    });
  } else if (jobData.experience_years > 0) {
    lines.push({
      icon: "fa-star text-warning",
      text: "Your experience level appears well matched for this job posting."
    });
  }

  if (!resumeData.education || resumeData.education.length === 0) {
    lines.push({
      icon: "fa-graduation-cap text-info",
      text: "Include degree or certification details if they are relevant to this role."
    });
  }

  return lines;
}

function updateDashboard(resumeResponse, jobResponse) {
  const resumeParsed = resumeResponse.parsed || {};
  const jobParsed = jobResponse.parsed || {};
  const resumeSkills = Array.isArray(resumeParsed.skills) ? resumeParsed.skills : [];
  const jobSkills = Array.isArray(jobParsed.skills) ? jobParsed.skills : [];
  const sharedSkills = resumeSkills.filter((skill) => jobSkills.includes(skill));

  const score = calculateScore(resumeParsed, jobParsed);

  // 1. Update the score number (Removed the % here because it is hardcoded in the HTML)
  scoreValue.textContent = score;
  
  // 2. Target the exact element with the .score-ring class to inject the CSS variable for the animation
  document.querySelector('.score-ring').style.setProperty("--score", score);
  
  resumeSkillsCount.textContent = resumeSkills.length;
  jobSkillsCount.textContent = jobSkills.length;
  matchedSkillsCount.textContent = sharedSkills.length;
  resumeExperience.textContent = `${resumeParsed.experience_years || 0} years`;
  resumeEducation.textContent = resumeParsed.education && resumeParsed.education.length ? resumeParsed.education.join(", ") : "Not detected";
  jobExperience.textContent = `${jobParsed.experience_years || 0} years`;
  jobTitle.textContent = jobParsed.title || "Not detected";

  updateList(resumeSkillsList, resumeSkills, "No skills extracted from resume.");
  updateList(jobSkillsList, jobSkills, "No skills extracted from the job description.");

  // 3. Inject structured HTML for suggestions with icons
  const suggestionLines = renderSuggestions(resumeParsed, jobParsed, sharedSkills);
  suggestions.innerHTML = "";
  suggestionLines.forEach((item) => {
    const node = document.createElement("div");
    node.className = "list-group-item d-flex gap-3 py-3 align-items-start border-0 border-bottom bg-transparent";
    node.innerHTML = `
      <i class="fa-solid ${item.icon} mt-1 fs-5"></i>
      <div>
        <p class="mb-0">${item.text}</p>
      </div>
    `;
    suggestions.appendChild(node);
  });

  resultsDashboard.classList.remove("d-none");
  resultsDashboard.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Event Listeners
loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginFeedback.textContent = "";
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();

  try {
    const result = await loginUser(email, password);
    localStorage.setItem("auth_token", result.access_token);
    loginFeedback.className = "text-success small mb-3 text-center";
    loginFeedback.innerHTML = '<i class="fa-solid fa-check-circle me-1"></i> Logged in successfully.';
    
    // Auto-close modal after successful login
    setTimeout(() => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        if (modal) modal.hide();
    }, 1000);
    
  } catch (error) {
    loginFeedback.className = "text-danger small mb-3 text-center";
    loginFeedback.innerHTML = `<i class="fa-solid fa-circle-exclamation me-1"></i> ${error.message}`;
  }
});

registerForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  registerFeedback.textContent = "";
  const email = document.getElementById("registerEmail").value.trim();
  const password = document.getElementById("registerPassword").value.trim();

  try {
    await registerUser(email, password);
    registerFeedback.className = "text-success small mb-3 text-center";
    registerFeedback.innerHTML = '<i class="fa-solid fa-check-circle me-1"></i> Account created! Please log in.';
  } catch (error) {
    registerFeedback.className = "text-danger small mb-3 text-center";
    registerFeedback.innerHTML = `<i class="fa-solid fa-circle-exclamation me-1"></i> ${error.message}`;
  }
});

chooseFileButton?.addEventListener("click", () => resumeInput.click());

resumeInput?.addEventListener("change", (event) => {
  const file = event.target.files[0];
  setSelectedFile(file);
});

["dragenter", "dragover"].forEach((eventName) => {
  uploadZone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  uploadZone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.remove("dragover");
  });
});

uploadZone?.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (file) {
    setSelectedFile(file);
  }
});

analyzeButton?.addEventListener("click", async () => {
  if (!selectedResumeFile) {
    showToast("Please upload a resume before analyzing.", "warning");
    return;
  }

  const jobTextValue = jobText.value.trim();
  if (!jobTextValue) {
    showToast("Please paste a job description before analyzing.", "warning");
    return;
  }

  setLoading(true);

  try {
    const [resumeResponse, jobResponse] = await Promise.all([
      uploadResume(selectedResumeFile),
      pasteJob(jobTextValue),
    ]);

    updateDashboard(resumeResponse, jobResponse);
    showToast("Analysis completed successfully.", "success");
  } catch (error) {
    showToast(error.message || "Analysis failed. Please try again.", "danger");
  } finally {
    setLoading(false);
  }
});

scrollToAnalyzer?.addEventListener("click", () => {
  document.querySelector("main")?.scrollIntoView({ behavior: "smooth" });
});

setSelectedFile(null);