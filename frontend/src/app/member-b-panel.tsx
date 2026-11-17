"use client";

import React, { useEffect, useState } from "react";
import AdminCatalogueManagement from "./admin-catalogue-management";
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

const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  if (process.env.NEXT_PUBLIC_API_BASE_URL) return process.env.NEXT_PUBLIC_API_BASE_URL;
  if (typeof window !== "undefined") {
    const host = window.location.hostname === "127.0.0.1" ? "127.0.0.1" : "localhost";
    return `http://${host}:8000/api/v1`;
  }
  return "http://localhost:8000/api/v1";
};
const API_BASE = getApiBaseUrl();

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
  background: "var(--accent-plum)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--radius-sm)",
  fontWeight: 600,
  cursor: "pointer",
};

interface MemberBPanelProps {
  token?: string | null;
  currentUser?: any;
  onLogout?: () => void;
}

export default function MemberBPanel({
  token: externalToken,
  currentUser: externalUser,
  onLogout,
}: MemberBPanelProps = {}) {
  const [email, setEmail] = useState("priya@example.com");
  const [password, setPassword] = useState("password123");
  const [token, setToken] = useState<string | null>(externalToken || null);
  const [currentUser, setCurrentUser] = useState<any>(externalUser || null);
  const [authStatus, setAuthStatus] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [registerName, setRegisterName] = useState("");
  const [reviews, setReviews] = useState<any[]>([]);
  const [reviewStatus, setReviewStatus] = useState("");

  const [reviewBrands, setReviewBrands] = useState<any[]>([]);
  const [reviewBrandId, setReviewBrandId] = useState("");
  const [reviewGarments, setReviewGarments] = useState<any[]>([]);
  const [reviewGarmentId, setReviewGarmentId] = useState("");
  const [reviewSizes, setReviewSizes] = useState<any[]>([]);

  const [form, setForm] = useState({
    garment_size_id: "",
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
  const [reviewCapacity, setReviewCapacity] = useState<{
    storage_type: string;
    max_bytes: number;
    enabled: boolean;
    supported: boolean;
    updates_enabled: boolean;
  } | null>(null);
  const [capacityStatus, setCapacityStatus] = useState("");
  const [capacityUpdating, setCapacityUpdating] = useState(false);

  useEffect(() => {
    if (!token || currentUser?.role !== "ADMIN") {
      setReviewCapacity(null);
      setCapacityStatus("");
      return;
    }
    const controller = new AbortController();
    fetch(`${API_BASE}/admin/review-settings`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Unable to load review settings.");
        setReviewCapacity(data);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setCapacityStatus(err.message);
      });
    return () => controller.abort();
  }, [token, currentUser?.role]);


  useEffect(() => {
    const activeTok =
      externalToken ||
      localStorage.getItem("fitcheck_member_b_token") ||
      localStorage.getItem("fitcheck_token");
    if (activeTok) {
      setToken(activeTok);
      if (externalUser) {
        setCurrentUser(externalUser);
      } else {
        fetchMe(activeTok);
      }
      fetchMyReviews(activeTok);
    } else {
      setToken(null);
      setCurrentUser(null);
      setReviews([]);
    }
  }, [externalToken, externalUser]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_BASE}/brands`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error("Unable to load brands.");
        return res.json();
      })
      .then(setReviewBrands)
      .catch((err) => {
        if (!controller.signal.aborted) setReviewStatus(err.message);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!reviewBrandId) return;
    const controller = new AbortController();
    fetch(`${API_BASE}/garments?brand_id=${reviewBrandId}`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error("Unable to load garments.");
        return res.json();
      })
      .then(setReviewGarments)
      .catch((err) => {
        if (!controller.signal.aborted) setReviewStatus(err.message);
      });
    return () => controller.abort();
  }, [reviewBrandId]);

  useEffect(() => {
    if (!reviewGarmentId) return;
    const controller = new AbortController();
    fetch(`${API_BASE}/garments/${reviewGarmentId}`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error("Unable to load garment sizes.");
        return res.json();
      })
      .then((data) => setReviewSizes(data.sizes || []))
      .catch((err) => {
        if (!controller.signal.aborted) setReviewStatus(err.message);
      });
    return () => controller.abort();
  }, [reviewGarmentId]);

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

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        setAuthStatus(errorData.detail || "Login failed. Check email and password.");
        return;
      }

      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem("fitcheck_member_b_token", data.access_token);
      localStorage.setItem("fitcheck_token", data.access_token);

      await fetchMe(data.access_token);
      await fetchMyReviews(data.access_token);
      setAuthStatus("Authenticated successfully.");
    } catch (err: any) {
      setAuthStatus(`Connection error: ${err.message}. Is backend running on port 8000?`);
    }
  };

  const register = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!registerName.trim()) {
      setAuthStatus("Name is required.");
      return;
    }

    setAuthStatus("Creating account...");

    try {
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
    } catch (err: any) {
      setAuthStatus(`Connection error: ${err.message}. Is backend running on port 8000?`);
    }
  };

  const logout = () => {
    localStorage.removeItem("fitcheck_member_b_token");
    localStorage.removeItem("fitcheck_token");
    setToken(null);
    setCurrentUser(null);
    setReviews([]);
    setAuditLogs([]);
    setAuthStatus("Logged out.");
    if (onLogout) {
      onLogout();
    }
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

    if (!form.garment_size_id) {
      setReviewStatus("Select a brand, garment and size before creating a review.");
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

  const updateReviewCapacity = async (enabled: boolean) => {
    setCapacityUpdating(true);
    setCapacityStatus("");
    try {
      const res = await fetch(`${API_BASE}/admin/review-settings`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({ enabled }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Unable to update review capacity.");
      setReviewCapacity(data);
      setCapacityStatus(`Extended Review Capacity is now ${data.enabled ? "ON" : "OFF"}. Storage type: ${data.storage_type}.`);
    } catch (err: any) {
      setCapacityStatus(err.message);
    } finally {
      setCapacityUpdating(false);
    }
  };

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      <div
        className="glass-panel"
        style={{ padding: "28px", borderColor: "var(--border-color)" }}
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
            <span className="badge badge-info">Verified Community Feedback</span>

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
              Authentic fit reviews and semantic vector search powered by high-dimensional embeddings.
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

      <div className="reviews-grid">
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
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "12px" }}>
              <div>
                <label htmlFor="review-brand" style={labelStyle}>Brand</label>
                <select
                  id="review-brand"
                  value={reviewBrandId}
                  onChange={(e) => {
                    setReviewBrandId(e.target.value);
                    setReviewGarments([]);
                    setReviewGarmentId("");
                    setReviewSizes([]);
                    setForm((prev) => ({ ...prev, garment_size_id: "" }));
                  }}
                  style={inputStyle}
                  required
                >
                  <option value="">Select brand...</option>
                  {reviewBrands.map((brand) => (
                    <option key={brand.brand_id} value={brand.brand_id}>{brand.brand_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="review-garment" style={labelStyle}>Garment</label>
                <select
                  id="review-garment"
                  value={reviewGarmentId}
                  onChange={(e) => {
                    setReviewGarmentId(e.target.value);
                    setReviewSizes([]);
                    setForm((prev) => ({ ...prev, garment_size_id: "" }));
                  }}
                  disabled={reviewGarments.length === 0}
                  style={inputStyle}
                  required
                >
                  <option value="">Select garment...</option>
                  {reviewGarments.map((garment) => (
                    <option key={garment.garment_id} value={garment.garment_id}>{garment.garment_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="review-size" style={labelStyle}>Size</label>
                <select
                  id="review-size"
                  value={form.garment_size_id}
                  onChange={(e) => setForm((prev) => ({ ...prev, garment_size_id: e.target.value }))}
                  disabled={reviewSizes.length === 0}
                  style={inputStyle}
                  required
                >
                  <option value="">Select size...</option>
                  {reviewSizes.map((size) => (
                    <option key={size.garment_size_id} value={size.garment_size_id}>{size.size_label}</option>
                  ))}
                </select>
              </div>
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
                  background: "var(--bg-card-subtle)",
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
                      background: "var(--danger)",
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
                background: "var(--bg-card-subtle)",
              }}
            >
              <strong>
                #{index + 1} {r.brand_name} • {r.garment_name} • Size{" "}
                {r.size_label}
              </strong>

              <div
                style={{
                  marginTop: "5px",
                  color: "var(--accent-plum)",
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

      {currentUser?.role === "ADMIN" && (
        <AdminCatalogueManagement token={token} apiBase={API_BASE} />
      )}

      {currentUser?.role === "ADMIN" && (
        <div className="glass-panel" style={{ padding: "28px" }}>
          <h3 style={{ marginBottom: "12px" }}>Review Settings</h3>
          <p style={{ color: "var(--text-secondary)", marginBottom: "14px" }}>
            Enable extended storage for longer fit experiences, or return to standard capacity when all existing reviews fit.
          </p>
          {reviewCapacity && (
            <>
              <p style={{ marginBottom: "14px" }}>
                Extended Review Capacity: {reviewCapacity.enabled ? "ON" : "OFF"}<br />
                Storage type: {reviewCapacity.storage_type} ({reviewCapacity.max_bytes.toLocaleString()} bytes)
              </p>
              <p style={{ color: "var(--text-muted)", marginBottom: "14px", fontSize: "0.85rem" }}>
                Capacity is measured in UTF-8 bytes; some characters use more than one byte. Disabling extended capacity requires every existing review to fit within 65,535 bytes.
              </p>
              <label htmlFor="review-capacity" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <input
                  id="review-capacity"
                  type="checkbox"
                  role="switch"
                  checked={reviewCapacity.enabled}
                  disabled={capacityUpdating || !reviewCapacity.updates_enabled || !reviewCapacity.supported}
                  onChange={(e) => updateReviewCapacity(e.target.checked)}
                />
                Extended Review Capacity{capacityUpdating ? " — Updating..." : ""}
              </label>
              {!reviewCapacity.supported && <p>This column definition cannot be changed safely through Review Settings.</p>}
              {!reviewCapacity.updates_enabled && (
                <p>Capacity updates require an administrative database connection to be configured.</p>
              )}
            </>
          )}
          {capacityStatus && <p role="status" style={{ marginTop: "12px", color: "var(--text-secondary)" }}>{capacityStatus}</p>}
        </div>
      )}

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
              background: "var(--bg-card-subtle)",
              border: "1px solid var(--border-color)",
              color: "var(--text-primary)",
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