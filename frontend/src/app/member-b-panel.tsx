"use client";

import React, { useEffect, useState } from "react";
import {
  Search,
  MessageSquare,
  LogIn,
  LogOut,
  Trash2,
  Save,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const inputStyle: React.CSSProperties = {
  width: "100%",
  background: "var(--bg-secondary)",
  border: "1px solid var(--border-color)",
  color: "var(--text-primary)",
  padding: "10px 12px",
  borderRadius: "var(--radius-sm)",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "0.82rem",
  color: "var(--text-secondary)",
  marginBottom: "6px",
  fontWeight: 600,
};

const buttonStyle: React.CSSProperties = {
  padding: "10px 18px",
  background: "var(--accent-gradient)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--radius-sm)",
  fontWeight: 600,
  cursor: "pointer",
};

export default function MemberBPanel() {
  const [email, setEmail] = useState("priya@example.com");
  const [password, setPassword] = useState("password123");
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [authStatus, setAuthStatus] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [registerName, setRegisterName] = useState("");
  const [reviews, setReviews] = useState<any[]>([]);
  const [reviewStatus, setReviewStatus] = useState("");

  const [form, setForm] = useState({
    garment_size_id: "3",
    overall_fit: "TRUE_TO_SIZE",
    waist_fit: "GOOD",
    hip_fit: "GOOD",
    thigh_fit: "GOOD",
    length_fit: "GOOD",
    review_text: "",
  });

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingText, setEditingText] = useState("");

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchStatus, setSearchStatus] = useState("");

  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [auditStatus, setAuditStatus] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("fitcheck_member_b_token");
    if (saved) {
      setToken(saved);
      fetchMe(saved);
      fetchMyReviews(saved);
    }
  }, []);

  const authHeaders = (activeToken?: string | null) => ({
    "Content-Type": "application/json",
    ...(activeToken || token
      ? { Authorization: `Bearer ${activeToken || token}` }
      : {}),
  });

  const fetchMe = async (activeToken: string) => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: authHeaders(activeToken),
    });

    if (res.ok) {
      setCurrentUser(await res.json());
    }
  };

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthStatus("Signing in...");

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      setAuthStatus("Login failed. Check email/password.");
      return;
    }

    const data = await res.json();

    setToken(data.access_token);
    localStorage.setItem("fitcheck_member_b_token", data.access_token);

    await fetchMe(data.access_token);
    await fetchMyReviews(data.access_token);

    setAuthStatus("Authenticated successfully.");
  };

  const register = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!registerName.trim()) {
      setAuthStatus("Name is required.");
      return;
    }

    setAuthStatus("Creating account...");

    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: registerName.trim(),
        email,
        password,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const detail =
        typeof err.detail === "string"
          ? err.detail
          : "Registration failed. Check the entered details.";

      setAuthStatus(`Registration failed: ${detail}`);
      return;
    }

    setRegisterName("");
    setAuthMode("login");
    setAuthStatus("Registration successful. You can now log in.");
  };

  const logout = () => {
    localStorage.removeItem("fitcheck_member_b_token");
    setToken(null);
    setCurrentUser(null);
    setReviews([]);
    setAuditLogs([]);
    setAuthStatus("Logged out.");
  };

  const fetchMyReviews = async (activeToken?: string | null) => {
    const t = activeToken || token;
    if (!t) return;

    const res = await fetch(`${API_BASE}/reviews/mine`, {
      headers: authHeaders(t),
    });

    if (res.ok) {
      setReviews(await res.json());
    }
  };

  const createReview = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setReviewStatus("Login before creating a review.");
      return;
    }

    if (!form.review_text.trim()) {
      setReviewStatus("Review text cannot be blank.");
      return;
    }

    setReviewStatus("Saving review to MySQL and Redis...");

    const res = await fetch(`${API_BASE}/reviews`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        ...form,
        garment_size_id: Number(form.garment_size_id),
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      setReviewStatus(`Error: ${err.detail || "Review creation failed"}`);
      return;
    }

    setReviewStatus("Review saved and vector indexed successfully.");
    setForm({ ...form, review_text: "" });
    await fetchMyReviews();
  };

  const updateReview = async (reviewId: number) => {
    if (!token || !editingText.trim()) return;

    const res = await fetch(`${API_BASE}/reviews/${reviewId}`, {
      method: "PATCH",
      headers: authHeaders(),
      body: JSON.stringify({ review_text: editingText }),
    });

    if (res.ok) {
      setEditingId(null);
      setEditingText("");
      setReviewStatus("Review updated and Redis vector refreshed.");
      await fetchMyReviews();
    } else {
      const err = await res.json();
      setReviewStatus(`Update failed: ${err.detail}`);
    }
  };

  const deleteReview = async (reviewId: number) => {
    if (!token) return;

    if (!window.confirm(`Delete review #${reviewId}?`)) return;

    const res = await fetch(`${API_BASE}/reviews/${reviewId}`, {
      method: "DELETE",
      headers: authHeaders(),
    });

    if (res.ok) {
      setReviewStatus("Review deleted from MySQL and Redis.");
      await fetchMyReviews();
    } else {
      const err = await res.json();
      setReviewStatus(`Delete failed: ${err.detail}`);
    }
  };

  const semanticSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!searchQuery.trim()) return;

    setSearching(true);
    setSearchStatus("Searching Redis vectors...");
    setSearchResults([]);

    try {
      const res = await fetch(`${API_BASE}/reviews/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          limit: 5,
        }),
      });

      if (!res.ok) {
        setSearchStatus("Semantic search failed.");
        return;
      }

      const data = await res.json();
      setSearchResults(data);

      setSearchStatus(
        data.length
          ? `${data.length} semantic matches returned from Redis + MySQL.`
          : "No semantic matches returned."
      );
    } finally {
      setSearching(false);
    }
  };

  const fetchAuditLogs = async () => {
    if (!token) return;

    setAuditStatus("Loading review activity audit trail...");

    const res = await fetch(`${API_BASE}/admin/audit-logs`, {
      headers: authHeaders(),
    });

    if (res.status === 403) {
      setAuditStatus("403 Forbidden — ADMIN role required.");
      setAuditLogs([]);
      return;
    }

    if (!res.ok) {
      setAuditStatus("Could not load audit logs.");
      return;
    }

    const data = await res.json();
    setAuditLogs(data);
    setAuditStatus(`${data.length} audit records loaded.`);
  };

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      <div
        className="glass-panel"
        style={{ padding: "28px", borderColor: "rgba(117,70,111,0.5)" }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: "20px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <span className="badge badge-info">Member B Contribution</span>

            <h2
              style={{
                fontSize: "1.5rem",
                fontWeight: 800,
                marginTop: "10px",
              }}
            >
              Authentication, Fit Reviews & Semantic Search
            </h2>

            <p
              style={{
                color: "var(--text-secondary)",
                marginTop: "6px",
              }}
            >
              MySQL review source of truth + Redis Stack vector retrieval.
            </p>
          </div>

          {currentUser && (
            <div style={{ textAlign: "right" }}>
              <strong>{currentUser.name}</strong>
              <div
                style={{
                  color: "var(--text-muted)",
                  fontSize: "0.85rem",
                }}
              >
                {currentUser.email}
              </div>

              <span
                className="badge badge-success"
                style={{ marginTop: "6px" }}
              >
                {currentUser.role}
              </span>
            </div>
          )}
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(300px, 0.8fr) minmax(420px, 1.2fr)",
          gap: "28px",
          alignItems: "start",
        }}
      >
        <div
          className="glass-panel"
          style={{ padding: "28px" }}
        >
          <h3
            style={{
              display: "flex",
              gap: "8px",
              alignItems: "center",
              marginBottom: "18px",
            }}
          >
            <LogIn size={20} />
            Authentication
          </h3>

          {!token ? (
            <form
              onSubmit={authMode === "login" ? login : register}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "12px",
              }}
            >
              {authMode === "register" && (
                <div>
                  <label htmlFor="register-name" style={labelStyle}>
                    Name
                  </label>
                  <input
                    id="register-name"
                    type="text"
                    value={registerName}
                    onChange={(e) => setRegisterName(e.target.value)}
                    placeholder="Enter your name"
                    style={inputStyle}
                    required
                  />
                </div>
              )}

              <div>
                <label htmlFor="auth-email" style={labelStyle}>
                  Email
                </label>
                <input
                  id="auth-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  style={inputStyle}
                  required
                />
              </div>

              <div>
                <label htmlFor="auth-password" style={labelStyle}>
                  Password
                </label>
                <input
                  id="auth-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  style={inputStyle}
                  required
                />
              </div>

              <button type="submit" style={buttonStyle}>
                {authMode === "login" ? "Login" : "Register"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setAuthMode(authMode === "login" ? "register" : "login");
                  setAuthStatus("");
                }}
                style={{
                  background: "transparent",
                  border: "1px solid var(--border-color)",
                  color: "var(--text-secondary)",
                  padding: "9px 12px",
                  borderRadius: "var(--radius-sm)",
                  cursor: "pointer",
                }}
              >
                {authMode === "login"
                  ? "Create a new account"
                  : "Already have an account? Login"}
              </button>
            </form>
          ) : (
            <button
              type="button"
              onClick={logout}
              style={buttonStyle}
            >
              <LogOut
                size={16}
                style={{ verticalAlign: "middle", marginRight: "6px" }}
              />
              Logout
            </button>
          )}

          {authStatus && (
            <p
              style={{
                marginTop: "12px",
                color: "var(--text-secondary)",
                fontSize: "0.85rem",
              }}
            >
              {authStatus}
            </p>
          )}

          <div
            style={{
              marginTop: "18px",
              paddingTop: "18px",
              borderTop: "1px solid var(--border-color)",
              fontSize: "0.82rem",
              color: "var(--text-muted)",
            }}
          >
            Demo USER: priya@example.com / password123
            <br />
            Demo ADMIN: admin@fitcheck.com / password123
          </div>
        </div>

        <div
          className="glass-panel"
          style={{ padding: "28px" }}
        >
          <h3
            style={{
              display: "flex",
              gap: "8px",
              alignItems: "center",
              marginBottom: "18px",
            }}
          >
            <MessageSquare size={20} />
            Submit Fit Review
          </h3>

          <form
            onSubmit={createReview}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "14px",
            }}
          >
            <div>
              <label htmlFor="garment-size-id" style={labelStyle}>
                Garment Size ID
              </label>
              <input
                id="garment-size-id"
                type="number"
                min="1"
                max="70"
                value={form.garment_size_id}
                onChange={(e) =>
                  setForm({
                    ...form,
                    garment_size_id: e.target.value,
                  })
                }
                placeholder="e.g. 3"
                style={inputStyle}
                required
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "14px",
              }}
            >
              <div>
                <label htmlFor="overall-fit" style={labelStyle}>
                  Overall Fit
                </label>
                <select
                  id="overall-fit"
                  value={form.overall_fit}
                  onChange={(e) =>
                    setForm({ ...form, overall_fit: e.target.value })
                  }
                  style={inputStyle}
                >
                  <option value="TOO_SMALL">Too Small</option>
                  <option value="SLIGHTLY_SMALL">Slightly Small</option>
                  <option value="TRUE_TO_SIZE">True to Size</option>
                  <option value="SLIGHTLY_LARGE">Slightly Large</option>
                  <option value="TOO_LARGE">Too Large</option>
                </select>
              </div>

              <div>
                <label htmlFor="waist-fit" style={labelStyle}>
                  Waist Fit
                </label>
                <select
                  id="waist-fit"
                  value={form.waist_fit}
                  onChange={(e) =>
                    setForm({ ...form, waist_fit: e.target.value })
                  }
                  style={inputStyle}
                >
                  <option value="TIGHT">Tight</option>
                  <option value="GOOD">Good</option>
                  <option value="LOOSE">Loose</option>
                </select>
              </div>

              <div>
                <label htmlFor="hip-fit" style={labelStyle}>
                  Hip Fit
                </label>
                <select
                  id="hip-fit"
                  value={form.hip_fit}
                  onChange={(e) =>
                    setForm({ ...form, hip_fit: e.target.value })
                  }
                  style={inputStyle}
                >
                  <option value="TIGHT">Tight</option>
                  <option value="GOOD">Good</option>
                  <option value="LOOSE">Loose</option>
                </select>
              </div>

              <div>
                <label htmlFor="thigh-fit" style={labelStyle}>
                  Thigh Fit
                </label>
                <select
                  id="thigh-fit"
                  value={form.thigh_fit}
                  onChange={(e) =>
                    setForm({ ...form, thigh_fit: e.target.value })
                  }
                  style={inputStyle}
                >
                  <option value="TIGHT">Tight</option>
                  <option value="GOOD">Good</option>
                  <option value="LOOSE">Loose</option>
                </select>
              </div>

              <div>
                <label htmlFor="length-fit" style={labelStyle}>
                  Length Fit
                </label>
                <select
                  id="length-fit"
                  value={form.length_fit}
                  onChange={(e) =>
                    setForm({ ...form, length_fit: e.target.value })
                  }
                  style={inputStyle}
                >
                  <option value="SHORT">Short</option>
                  <option value="GOOD">Good</option>
                  <option value="LONG">Long</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="fit-experience" style={labelStyle}>
                Fit Experience
              </label>
              <textarea
                id="fit-experience"
                value={form.review_text}
                onChange={(e) =>
                  setForm({ ...form, review_text: e.target.value })
                }
                placeholder="Describe how the garment fits..."
                rows={4}
                style={inputStyle}
                required
              />
            </div>

            <button
              type="submit"
              style={buttonStyle}
              disabled={!token}
            >
              Save Review + Vector
            </button>
          </form>

          {reviewStatus && (
            <p
              style={{
                marginTop: "12px",
                color: "var(--text-secondary)",
                fontSize: "0.85rem",
              }}
            >
              {reviewStatus}
            </p>
          )}
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "28px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "18px",
          }}
        >
          <h3>My Reviews</h3>

          <button
            onClick={() => fetchMyReviews()}
            disabled={!token}
            style={buttonStyle}
            aria-label="Refresh my reviews"
            title="Refresh my reviews"
          >
            <RefreshCw size={15} />
          </button>
        </div>

        {!token ? (
          <p style={{ color: "var(--text-muted)" }}>
            Login to view your reviews.
          </p>
        ) : reviews.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>
            No reviews for this account.
          </p>
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            {reviews.map((r) => (
              <div
                key={r.review_id}
                style={{
                  padding: "16px",
                  border: "1px solid var(--border-color)",
                  borderRadius: "var(--radius-sm)",
                  background: "rgba(0,0,0,0.2)",
                }}
              >
                <strong>
                  {r.brand_name} • {r.garment_name} • Size {r.size_label}
                </strong>

                <div
                  style={{
                    marginTop: "5px",
                    fontSize: "0.8rem",
                    color: "var(--text-muted)",
                  }}
                >
                  Review #{r.review_id} • {r.overall_fit} • Waist{" "}
                  {r.waist_fit}
                </div>

                {editingId === r.review_id ? (
                  <>
                    <label
                      htmlFor={`edit-review-${r.review_id}`}
                      style={{ ...labelStyle, marginTop: "10px" }}
                    >
                      Edit Fit Experience
                    </label>
                    <textarea
                      id={`edit-review-${r.review_id}`}
                      rows={3}
                      value={editingText}
                      onChange={(e) => setEditingText(e.target.value)}
                      style={inputStyle}
                    />

                    <button
                      onClick={() => updateReview(r.review_id)}
                      style={{ ...buttonStyle, marginTop: "8px" }}
                    >
                      <Save size={15} /> Save Update
                    </button>
                  </>
                ) : (
                  <p
                    style={{
                      marginTop: "10px",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {r.review_text}
                  </p>
                )}

                <div
                  style={{
                    display: "flex",
                    gap: "8px",
                    marginTop: "12px",
                  }}
                >
                  <button
                    onClick={() => {
                      setEditingId(r.review_id);
                      setEditingText(r.review_text);
                    }}
                    style={buttonStyle}
                  >
                    Edit
                  </button>

                  <button
                    onClick={() => deleteReview(r.review_id)}
                    style={{
                      ...buttonStyle,
                      background: "#7f1d1d",
                    }}
                  >
                    <Trash2 size={15} /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="glass-panel" style={{ padding: "28px" }}>
        <h3
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginBottom: "16px",
          }}
        >
          <Search size={20} />
          Semantic Fit Experience Search
        </h3>

        <form
          onSubmit={semanticSearch}
          style={{ display: "flex", gap: "10px", alignItems: "end" }}
        >
          <div style={{ flex: 1 }}>
            <label htmlFor="semantic-search-query" style={labelStyle}>
              Search Fit Experiences
            </label>
            <input
              id="semantic-search-query"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g. waist gaps but thighs feel tight"
              style={inputStyle}
            />
          </div>

          <button type="submit" style={buttonStyle}>
            {searching ? "Searching..." : "Vector Search"}
          </button>
        </form>

        {searchStatus && (
          <p
            style={{
              marginTop: "10px",
              color: "var(--text-muted)",
              fontSize: "0.85rem",
            }}
          >
            {searchStatus}
          </p>
        )}

        <div
          style={{
            marginTop: "18px",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >
          {searchResults.map((r, index) => (
            <div
              key={r.review_id}
              style={{
                padding: "16px",
                border: "1px solid var(--border-color)",
                borderRadius: "var(--radius-sm)",
              }}
            >
              <strong>
                #{index + 1} {r.brand_name} • {r.garment_name} • Size{" "}
                {r.size_label}
              </strong>

              <div
                style={{
                  marginTop: "5px",
                  color: "var(--accent-purple)",
                  fontWeight: 700,
                }}
              >
                Similarity: {(Number(r.similarity_score) * 100).toFixed(1)}%
              </div>

              <p
                style={{
                  marginTop: "8px",
                  color: "var(--text-secondary)",
                }}
              >
                {r.review_text}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "28px" }}>
        <h3
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginBottom: "12px",
          }}
        >
          <ShieldCheck size={20} />
          Review Activity Audit Trail
        </h3>

        <p
          style={{
            color: "var(--text-secondary)",
            fontSize: "0.85rem",
            marginBottom: "14px",
          }}
        >
          ADMIN-only database audit records for review creation, updates, and
          deletions. Click the button to refresh the latest activity.
        </p>

        <button
          onClick={fetchAuditLogs}
          disabled={!token}
          style={buttonStyle}
        >
          Load Audit Trail
        </button>

        {auditStatus && (
          <p
            style={{
              marginTop: "10px",
              color: "var(--text-secondary)",
            }}
          >
            {auditStatus}
          </p>
        )}

        {auditLogs.slice(0, 10).map((log, index) => (
          <pre
            key={index}
            style={{
              marginTop: "10px",
              padding: "10px",
              overflowX: "auto",
              background: "rgba(0,0,0,0.25)",
              borderRadius: "6px",
              fontSize: "0.78rem",
            }}
          >
            {JSON.stringify(log, null, 2)}
          </pre>
        ))}
      </div>
    </section>
  );
}