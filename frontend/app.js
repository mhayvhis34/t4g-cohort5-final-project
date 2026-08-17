// Registrar frontend — talks to the FastAPI backend.
// Change this if your API runs somewhere other than localhost:8000.

const API_BASE_URL = ""; // Leave blank so it uses the current live domain



let students = [];
let courses = [];
let activeStudentId = null;

// ---------- helpers ----------

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const message = (data && data.detail) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.remove("hidden");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.add("hidden"), 3000);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------- students ----------

async function loadStudents() {
  students = await api("/students");
  renderStudentList();
}

function renderStudentList() {
  const list = document.getElementById("studentList");
  document.getElementById("studentCount").textContent = students.length;

  if (students.length === 0) {
    list.innerHTML = `<li class="empty-state">No students yet — add one above.</li>`;
    return;
  }

  list.innerHTML = students
    .map(
      (s) => `
      <li data-id="${s.id}">
        <div class="r-meta">
          <strong>${escapeHtml(s.first_name)} ${escapeHtml(s.last_name)}</strong>
          <span>${escapeHtml(s.email)}</span>
        </div>
        <button class="remove" data-id="${s.id}">Remove</button>
      </li>`
    )
    .join("");

  list.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", (e) => {
      if (e.target.closest("button")) return;
      openTranscript(Number(li.dataset.id));
    });
  });

  list.querySelectorAll("button.remove").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteStudent(Number(btn.dataset.id));
    });
  });
}

async function deleteStudent(id) {
  if (!confirm("Remove this student? Their enrollments will be removed too.")) return;
  try {
    await api(`/students/${id}`, { method: "DELETE" });
    showToast("Student removed");
    await loadStudents();
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("studentForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    first_name: document.getElementById("firstName").value.trim(),
    last_name: document.getElementById("lastName").value.trim(),
    email: document.getElementById("email").value.trim(),
    date_of_birth: document.getElementById("dob").value || null,
    phone: document.getElementById("phone").value.trim() || null,
  };

  try {
    await api("/students", { method: "POST", body: JSON.stringify(payload) });
    e.target.reset();
    showToast("Student enrolled");
    await loadStudents();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---------- courses ----------

async function loadCourses() {
  courses = await api("/courses");
  renderCourseList();
  renderEnrollSelect();
}

function renderCourseList() {
  const list = document.getElementById("courseList");
  document.getElementById("courseCount").textContent = courses.length;

  if (courses.length === 0) {
    list.innerHTML = `<li class="empty-state">No courses yet — add one above.</li>`;
    return;
  }

  list.innerHTML = courses
    .map(
      (c) => `
      <li>
        <div class="r-meta">
          <strong>${escapeHtml(c.code)} — ${escapeHtml(c.title)}</strong>
          <span>${escapeHtml(c.description || "")}</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="r-badge">${c.credits} cr</span>
          <button class="remove" data-id="${c.id}">Remove</button>
        </div>
      </li>`
    )
    .join("");

  list.querySelectorAll("button.remove").forEach((btn) => {
    btn.addEventListener("click", () => deleteCourse(Number(btn.dataset.id)));
  });
}

function renderEnrollSelect() {
  const select = document.getElementById("enrollCourse");
  select.innerHTML =
    `<option value="" disabled selected>Enroll  in course…</option>` +
    courses.map((c) => `<option value="${c.id}">${escapeHtml(c.code)} — ${escapeHtml(c.title)}</option>`).join("");
}

async function deleteCourse(id) {
  if (!confirm("Remove this course? All related enrollments will be removed too.")) return;
  try {
    await api(`/courses/${id}`, { method: "DELETE" });
    showToast("Course removed");
    await loadCourses();
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("courseForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    code: document.getElementById("courseCode").value.trim(),
    title: document.getElementById("courseTitle").value.trim(),
    credits: Number(document.getElementById("courseCredits").value),
    description: document.getElementById("courseDescription").value.trim() || null,
  };

  try {
    await api("/courses", { method: "POST", body: JSON.stringify(payload) });
    e.target.reset();
    document.getElementById("courseCredits").value = 3;
    showToast("Course added");
    await loadCourses();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---------- transcript (student detail + enrollments) ----------

async function openTranscript(studentId) {
  try {
    const student = await api(`/students/${studentId}`);
    activeStudentId = studentId;

    document.getElementById("detailName").textContent = `${student.first_name} ${student.last_name}`;
    document.getElementById("detailEmail").textContent = student.email;

    renderLedger(student.enrollments);
    document.getElementById("detailOverlay").classList.remove("hidden");
  } catch (err) {
    showToast(err.message, true);
  }
}

function renderLedger(enrollments) {
  const body = document.getElementById("ledgerBody");

  if (!enrollments || enrollments.length === 0) {
    body.innerHTML = `<tr><td colspan="6" class="empty-state">Not enrolled in any courses yet.</td></tr>`;
    return;
  }

  body.innerHTML = enrollments
    .map(
      (e) => `
      <tr data-enrollment-id="${e.id}">
        <td>${escapeHtml(e.course?.code || "")}</td>
        <td>${escapeHtml(e.course?.title || "")}</td>
        <td>${e.course?.credits ?? ""}</td>
        <td>${e.enrolled_on ?? ""}</td>
        <td>
          <input
            class="grade-input"
            data-enrollment-id="${e.id}"
            maxlength="2"
            value="${escapeHtml(e.grade || "")}"
            placeholder="—"
          />
        </td>
        <td><button class="unenroll-btn" data-enrollment-id="${e.id}">Unenrol</button></td>
      </tr>`
    )
    .join("");

  body.querySelectorAll(".grade-input").forEach((input) => {
    input.addEventListener("change", () => updateGrade(Number(input.dataset.enrollmentId), input.value));
  });

  body.querySelectorAll(".unenroll-btn").forEach((btn) => {
    btn.addEventListener("click", () => unenroll(Number(btn.dataset.enrollmentId)));
  });
}

async function updateGrade(enrollmentId, grade) {
  try {
    await api(`/enrollments/${enrollmentId}`, {
      method: "PUT",
      body: JSON.stringify({ grade: grade.trim() || null }),
    });
    showToast("Grade updated");
  } catch (err) {
    showToast(err.message, true);
  }
}

async function unenroll(enrollmentId) {
  if (!confirm("Unenroll the student from this course?")) return;
  try {
    await api(`/enrollments/${enrollmentId}`, { method: "DELETE" });
    showToast("Unenrolled");
    const student = await api(`/students/${activeStudentId}`);
    renderLedger(student.enrollments);
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("enrollForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const courseId = Number(document.getElementById("enrollCourse").value);
  if (!activeStudentId || !courseId) return;

  try {
    await api("/enrollments", {
      method: "POST",
      body: JSON.stringify({ student_id: activeStudentId, course_id: courseId }),
    });
    e.target.reset();
    showToast("Enrolled");
    const student = await api(`/students/${activeStudentId}`);
    renderLedger(student.enrollments);
  } catch (err) {
    showToast(err.message, true);
  }
});

document.getElementById("closeDetail").addEventListener("click", () => {
  document.getElementById("detailOverlay").classList.add("hidden");
  activeStudentId = null;
});

document.getElementById("deleteStudentBtn").addEventListener("click", async () => {
  if (!activeStudentId || !confirm("Remove this student entirely?")) return;
  try {
    await api(`/students/${activeStudentId}`, { method: "DELETE" });
    document.getElementById("detailOverlay").classList.add("hidden");
    showToast("Student removed");
    activeStudentId = null;
    await loadStudents();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---------- init ----------

async function init() {
  try {
    await api("/health");
    document.getElementById("apiStatus").textContent = "Connected to API";
  } catch {
    document.getElementById("apiStatus").textContent =
      "Cannot reach API — is it running on port 8000?";
  }

  try {
    await loadStudents();
    await loadCourses();
  } catch (err) {
    showToast(err.message, true);
  }
}

init();
