import { useEffect, useState } from "react";
import axios from "axios";

import {
  signUp,
  confirmSignUp,
  signIn,
  signOut,
  getCurrentUser,
  fetchAuthSession,
} from "aws-amplify/auth";

import { apiRequest } from "./api";

export default function App() {
  const [authLoading, setAuthLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Signup/Login state
  const [mode, setMode] = useState("login"); // login | signup | confirm
  const [authError, setAuthError] = useState("");
  const [authMessage, setAuthMessage] = useState("");

  // Signup fields
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [confirmCode, setConfirmCode] = useState("");

  // Login fields
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Health check
  const [healthStatus, setHealthStatus] = useState("...");
  const [healthError, setHealthError] = useState("");

  // Incidents
  const [incidents, setIncidents] = useState([]);
  const [incidentsLoading, setIncidentsLoading] = useState(false);
  const [incidentsError, setIncidentsError] = useState("");

  // Create incident
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [selectedPriority, setSelectedPriority] = useState("LOW");

  // Selected incident detail
  const [incidentDetail, setIncidentDetail] = useState(null);
  const [incidentLoading, setIncidentLoading] = useState(false);

  // Comment
  const [commentText, setCommentText] = useState("");

  // Upload attachment
  const [uploadFile, setUploadFile] = useState(null);

  // -------------------------------
  // AUTH CHECK
  // -------------------------------
  async function checkUser(retry = 0) {
    try {
      const currentUser = await getCurrentUser();
      const session = await fetchAuthSession();
      const email =
      session.tokens?.idToken?.payload?.email ||
      currentUser.username; // fallback
      // setUser(currentUser);
       setUser({
      ...currentUser,
      email: email,
    });
    } catch (err) {
      if (retry < 2) {
        setTimeout(() => checkUser(retry + 1), 300);
        return;
      }
      setUser(null);
    } finally {
      setAuthLoading(false);
    }
  }

  // -------------------------------
  // HEALTH CHECK
  // -------------------------------
  async function checkHealth() {
    const API_BASE_URL = import.meta.env.VITE_API_URL;
    try {
      setHealthError("");
      const data = await axios.get(`${API_BASE_URL}/health`);
      setHealthStatus(data.status || "ok");
    } catch (err) {
      setHealthError(err.message);
      setHealthStatus("FAILED");
    }
  }

  // -------------------------------
  // LOAD INCIDENTS
  // -------------------------------
  async function loadIncidents() {
    setIncidentsError("");
    try {
      setIncidentsError("");
      setIncidentsLoading(true);

      const resp = await apiRequest("GET", "/incidents");
      setIncidents(resp.data.incidents || []);
      
    } catch (err) {
      setIncidentsError(err.message);
    } finally {
      setIncidentsLoading(false);
    }
  }

  // -------------------------------
  // LOAD INCIDENT DETAIL
  // -------------------------------
  async function loadIncidentDetail(id) {
    try {
      setIncidentLoading(true);

      const resp = await apiRequest("GET", `/incidents/${id}`);
      const incident = resp.data.incident;

      incident.comments = incident.comments || [];
      incident.attachments = incident.attachments || [];

      setIncidentDetail(incident);
    } catch (err) {
      setIncidentsError(err.message);
    } finally {
      setIncidentLoading(false);
    }
  }

  // -------------------------------
  // CREATE INCIDENT
  // -------------------------------
  async function createIncident() {
    setIncidentsError("");

    if (!newTitle.trim()) {
      setIncidentsError("Incident title is required.");
      return;
    }

    if (!newDescription.trim()) {
      setIncidentsError("Incident description is required.");
      return;
    }

    try {
      await apiRequest("POST", "/incidents", {
        title: newTitle,
        description: newDescription,
        priority: selectedPriority,
      });

      setNewTitle("");
      setNewDescription("");
      setSelectedPriority("LOW");

      await loadIncidents();
    } catch (err) {
      setIncidentsError(err.message);
    }
  }

  // -------------------------------
  // UPDATE STATUS
  // -------------------------------
  async function updateStatus(id, status) {
    try {
      await apiRequest("PATCH", `/incidents/${id}`, { status });
      await loadIncidentDetail(id);
      await loadIncidents();
    } catch (err) {
      setIncidentsError(err.message);
    }
  }

  // -------------------------------
  // ADD COMMENT
  // -------------------------------
  async function addComment(id) {
    setIncidentsError("");

    if (!commentText.trim()) {
      setIncidentsError("Comment text is required.");
      return;
    }

    try {
      await apiRequest("POST", `/incidents/${id}/comments`, {
        text: commentText,
      });

      setCommentText("");
      await loadIncidentDetail(id);
    } catch (err) {
      setIncidentsError(err.message);
    }
  }

  // -------------------------------
  // UPLOAD ATTACHMENT
  // -------------------------------
  async function uploadAttachment(id) {
    setIncidentsError("");

    if (!uploadFile) {
      setIncidentsError("Please choose a file to upload.");
      return;
    }

    try {
      const contentType = uploadFile.type || "application/octet-stream";

      const presignData = await apiRequest(
        "POST",
        `/incidents/${id}/attachments/presign`,
        {
          filename: uploadFile.name,
          content_type: contentType,
        }
      );

      const presignedUrl = presignData.data.presigned_url;

      if (!presignedUrl) {
        throw new Error("Backend did not return presigned_url");
      }

      await axios.put(presignedUrl, uploadFile, {
        headers: {
          "Content-Type": contentType,
        },
      });
    

      setUploadFile(null);

      await loadIncidentDetail(id);
      const updatedIncident = presignData.data.incident;
      if (updatedIncident) {                              
        setIncidentDetail(updatedIncident);
      }
      alert("Upload successful!");
    } catch (err) {
      setIncidentsError(err.message);
    }
  }

  // -------------------------------
  // DOWNLOAD ATTACHMENT
  // -------------------------------
  // function downloadAttachment(attachment) {
  //   const bucket = import.meta.env.VITE_UPLOAD_BUCKET_NAME;
  //   const region = import.meta.env.VITE_AWS_REGION;

  //   if (!bucket) {
  //     alert("Missing VITE_UPLOAD_BUCKET_NAME in .env");
  //     return;
  //   }
  //   const url = `https://${bucket}.s3.${region}.amazonaws.com/${attachment.object_key}`;
  //   window.open(url, "_blank");
  // }
  async function downloadAttachment(incident_id, attachment_id) {
  try {
    const resp = await apiRequest(
      "GET",
      `/incidents/${incident_id}/attachments/${attachment_id}/download`
    );

    const url = resp.data.download_url;
    console.log("download resp:", resp.data);
    console.log("download_url:", resp.data.download_url);
    window.open(url, "_blank");
  } catch (err) {
    console.error(err);
    setIncidentsError(err.message || "Download failed");
  }
}
  // -------------------------------
  // AUTH HANDLERS
  // -------------------------------
  async function handleSignup(e) {
    e.preventDefault();
    setAuthError("");
    setAuthMessage("");

    try {
      await signUp({
        username: signupEmail,
        password: signupPassword,
      });

      setAuthMessage("Signup successful. Please check email for confirmation code.");
      setMode("confirm");
    } catch (err) {
      setAuthError(err.message || "Signup failed");
    }
  }

  async function handleConfirm(e) {
    e.preventDefault();
    setAuthError("");
    setAuthMessage("");

    try {
      await confirmSignUp({
        username: signupEmail,
        confirmationCode: confirmCode,
      });

      setAuthMessage("Confirm successful. You can login now.");
      setMode("login");
    } catch (err) {
      setAuthError(err.message || "Confirm failed");
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    setAuthError("");
    setAuthMessage("");

    try {
      await signIn({
        username: loginEmail,
        password: loginPassword,
      });

      await checkUser();
      await checkHealth();
      await loadIncidents();
    } catch (err) {
      const msg = err?.message || "";

      if (
        err?.name === "UserAlreadyAuthenticatedException" ||
        msg.includes("already a signed in user")
      ) {
        await checkUser();
        await checkHealth();
        await loadIncidents();
        return;
      }

      setAuthError(err.message || "Login failed");
    }
  }

  async function handleLogout() {
    await signOut();
    setUser(null);
    setIncidents([]);
    setIncidentDetail(null);
    setMode("login");
  }

  // -------------------------------
  // INIT
  // -------------------------------
  useEffect(() => {
    (async () => {
      await checkUser();
      await checkHealth();
      if (user) await loadIncidents();
    })();
  }, []);

  useEffect(() => {
    if (user) {
      loadIncidents();
    }
  }, [user]);

  // -------------------------------
  // UI
  // -------------------------------
  if (authLoading) {
    return (
      <div className="container">
        <h2>Loading...</h2>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container">
        <h1 className="title">Cloud Incident Dashboard</h1>

        <div className="card">
          <h3>Backend Health Check</h3>
          <p>Status: {healthStatus}</p>
          {healthError && <p className="error">FAILED - {healthError}</p>}
        </div>

        <div className="card">
          {mode === "login" && (
            <>
              <h2>Login</h2>

              <form onSubmit={handleLogin}>
                <label>Email</label>
                <input
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  type="email"
                />

                <label>Password</label>
                <input
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  type="password"
                />

                <button type="submit">Login</button>
              </form>

              <p className="small-text">
                No account?{" "}
                <span className="link" onClick={() => setMode("signup")}>
                  Sign up
                </span>
              </p>
            </>
          )}

          {mode === "signup" && (
            <>
              <h2>Sign Up</h2>

              <form onSubmit={handleSignup}>
                <label>Email</label>
                <input
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  type="email"
                />

                <label>Password</label>
                <input
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  type="password"
                />

                <button type="submit">Sign Up</button>
              </form>

              <p className="small-text">
                Already have an account?{" "}
                <span className="link" onClick={() => setMode("login")}>
                  Login
                </span>
              </p>
            </>
          )}

          {mode === "confirm" && (
            <>
              <h2>Confirm Signup</h2>

              <form onSubmit={handleConfirm}>
                <label>Confirmation Code</label>
                <input
                  value={confirmCode}
                  onChange={(e) => setConfirmCode(e.target.value)}
                  type="text"
                />

                <button type="submit">Confirm</button>
              </form>
            </>
          )}

          {authError && <p className="error">{authError}</p>}
          {authMessage && <p className="success">{authMessage}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="topbar">
        <h1 className="title">Incident Dashboard</h1>

        <div className="user-info">
          <p className="small-text">
            Logged in as: <b>{user.email}</b>
          </p>
          <button className="secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="grid">
        {/* LEFT COLUMN */}
        <div className="card">
          <h2>Create Incident</h2>

          <label>Title</label>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Incident title"
          />

          <label>Description</label>
          <textarea
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            placeholder="Describe the issue..."
          />

          <label>Priority</label>
          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
          >
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
          </select>

          <button onClick={createIncident}>Create</button>

          {incidentsError && <p className="error">{incidentsError}</p>}
        </div>

        <div className="card">
          <h2>Incident List</h2>

          <button className="secondary" onClick={loadIncidents}>
            Refresh Incidents
          </button>

          {incidentsLoading && <p>Loading...</p>}

          {incidents.length === 0 && !incidentsLoading && (
            <p className="small-text">No incidents found.</p>
          )}

          <div className="incident-list">
            {incidents.map((i) => (
              <div
                key={i.incident_id}
                className="incident-item"
                onClick={() => loadIncidentDetail(i.incident_id)}
              >
                <div>
                  <p className="incident-title">{i.title}</p>
                  <p className="small-text">
                    {i.status} • {i.priority}
                  </p>
                </div>

                <span className="small-text">
                  {new Date(i.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="card full">
          <h2>Incident Detail</h2>

          {!incidentDetail && (
            <p className="small-text">
              Select an incident from the list to view details.
            </p>
          )}

          {incidentLoading && <p>Loading incident...</p>}

          {incidentDetail && (
            <>
              <h3>{incidentDetail.title}</h3>

              <p className="small-text">
                ID: <b>{incidentDetail.incident_id}</b>
              </p>

              <p>{incidentDetail.description}</p>

              <div className="badges">
                <span className="badge">{incidentDetail.status}</span>
                <span className="badge">{incidentDetail.priority}</span>
                {incidentDetail.jira_issue_key && (
                  <span className="badge">JIRA: {incidentDetail.jira_issue_key}</span>
                )}
              </div>

              <div className="actions">
                <button
                  className="secondary"
                  onClick={() => updateStatus(incidentDetail.incident_id, "OPEN")}
                >
                  OPEN
                </button>
                <button
                  className="secondary"
                  onClick={() =>
                    updateStatus(incidentDetail.incident_id, "IN_PROGRESS")
                  }
                >
                  IN_PROGRESS
                </button>
                <button
                  className="secondary"
                  onClick={() =>
                    updateStatus(incidentDetail.incident_id, "RESOLVED")
                  }
                >
                  RESOLVED
                </button>
              </div>

              <hr />

              <h3>Add Comment</h3>

              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Write a comment..."
              />

              <button
                onClick={() => addComment(incidentDetail.incident_id)}
              >
                Submit Comment
              </button>

              <hr />

              <h3>Comments</h3>

              {(!incidentDetail?.comments || incidentDetail.comments.length === 0) && (
                <p className="small-text">No comments yet.</p>
              )}

              {incidentDetail?.comments?.map((c) => (
                <div key={c.comment_id} className="comment-box">
                  <p className="comment-text">{c.text}</p>
                  <p className="small-text">
                    {new Date(c.created_at).toLocaleString()}
                  </p>
                </div>
              ))}

              <hr />

              <h3>Upload Attachment</h3>

              <input
                type="file"
                onChange={(e) => setUploadFile(e.target.files[0])}
              />

              <button
                disabled={!uploadFile}
                onClick={() => uploadAttachment(incidentDetail.incident_id)}
              >
                Upload
              </button>

              <hr />

              <h3>Attachments</h3>

              {(!incidentDetail?.attachments || incidentDetail.attachments.length === 0) && (
                <p className="small-text">No attachments uploaded.</p>
              )}

              {incidentDetail.attachments?.map((a) => (
                <div key={a.attachment_id} className="attachment-box">
                  <div>
                    <p className="attachment-name">{a.file_name}</p>
                    <p className="small-text">
                      {a.content_type} •{" "}
                      {new Date(a.uploaded_at).toLocaleString()}
                    </p>
                  </div>

                  <button
                    className="secondary"
                    onClick={() => downloadAttachment(incidentDetail.incident_id,a.attachment_id)}
                  >
                    Download
                  </button>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}