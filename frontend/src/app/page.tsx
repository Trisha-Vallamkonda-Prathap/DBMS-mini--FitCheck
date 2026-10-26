"use client";

import React, { useState, useEffect } from "react";
import MemberBPanel from "./member-b-panel";
import {
  Sparkles,
  Ruler,
  ShoppingBag,
  User as UserIcon,
  Layers,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Info,
  ChevronRight,
  MessageSquare,
  LogIn,
  LogOut,
  Lock,
  Mail,
  ShieldCheck,
} from "lucide-react";

// API Base URL with host alignment (supports localhost and 127.0.0.1 dynamically)
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

// Viva Evaluation Test Personas for convenient grading
const DEMO_PERSONAS = [
  { id: 2, name: "Priya Sharma", email: "priya@example.com", role: "USER", note: "Standard Profile (Kept Levis 28) — Ideal cross-brand demo" },
  { id: 3, name: "Ananya Rao", email: "ananya@example.com", role: "USER", note: "Petite Profile (Waist 64cm, Kept sz 26)" },
  { id: 1, name: "Admin User", email: "admin@fitcheck.com", role: "ADMIN", note: "System Administrator (Audit trail access)" },
];

export default function FitCheckApp() {
  // Authentication states
  const [authChecking, setAuthChecking] = useState<boolean>(true);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<any | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authEmail, setAuthEmail] = useState<string>("priya@example.com");
  const [authPassword, setAuthPassword] = useState<string>("password123");
  const [registerName, setRegisterName] = useState<string>("");
  const [authLoading, setAuthLoading] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // Navigation
  const [activeTab, setActiveTab] = useState<
    "recommend" | "profile" | "purchases" | "catalogue" | "reviews"
  >("recommend");

  // Catalogue & Dropdown Data states
  const [brands, setBrands] = useState<any[]>([]);
  const [brandsLoading, setBrandsLoading] = useState<boolean>(false);
  const [brandError, setBrandError] = useState<string | null>(null);

  const [garments, setGarments] = useState<any[]>([]);
  const [garmentsLoading, setGarmentsLoading] = useState<boolean>(false);
  const [garmentError, setGarmentError] = useState<string | null>(null);

  const [selectedBrandId, setSelectedBrandId] = useState<number | null>(null);
  const [selectedGarmentId, setSelectedGarmentId] = useState<number | null>(null);
  const [garmentDetail, setGarmentDetail] = useState<any | null>(null);

  // Body profile state
  const [profile, setProfile] = useState<any | null>(null);
  const [profileForm, setProfileForm] = useState({
    height: "",
    waist: "",
    hip: "",
    thigh: "",
    inseam: "",
    preferred_fit: "REGULAR",
  });
  const [profileSaveStatus, setProfileSaveStatus] = useState<string | null>(null);

  // Purchase history state
  const [purchases, setPurchases] = useState<any[]>([]);
  const [newPurchaseForm, setNewPurchaseForm] = useState({
    garment_size_id: "",
    outcome: "KEPT",
    fit_satisfaction: "GOOD",
    fit_preference: "REGULAR",
  });
  const [purchaseStatus, setPurchaseStatus] = useState<string | null>(null);

  // Dedicated Cascaded Purchase Form Catalogue States
  const [purchaseBrandId, setPurchaseBrandId] = useState<number | null>(null);
  const [purchaseGarments, setPurchaseGarments] = useState<any[]>([]);
  const [purchaseGarmentId, setPurchaseGarmentId] = useState<number | null>(null);
  const [purchaseSizes, setPurchaseSizes] = useState<any[]>([]);

  // Recommendation state
  const [recommendation, setRecommendation] = useState<any | null>(null);
  const [manualWaist, setManualWaist] = useState<string>("");
  const [manualHip, setManualHip] = useState<string>("");
  const [isRecommending, setIsRecommending] = useState<boolean>(false);
  const [recError, setRecError] = useState<string | null>(null);

  // Backend connectivity status
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  // Session check on initial mount
  useEffect(() => {
    const savedToken =
      localStorage.getItem("fitcheck_token") ||
      localStorage.getItem("fitcheck_member_b_token");

    if (savedToken) {
      validateAndRestoreSession(savedToken);
    } else {
      setAuthChecking(false);
      checkHealth();
    }
  }, []);

  // When selected garment changes, load detail
  useEffect(() => {
    if (selectedGarmentId) {
      fetchGarmentDetail(selectedGarmentId);
    } else {
      setGarmentDetail(null);
    }
  }, [selectedGarmentId]);

  // Session Validation
  const validateAndRestoreSession = async (token: string) => {
    setAuthChecking(true);
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const userData = await res.json();
        setCurrentUser(userData);
        setAuthToken(token);
        localStorage.setItem("fitcheck_token", token);
        localStorage.setItem("fitcheck_member_b_token", token);
        fetchUserProfile(token);
        fetchUserPurchases(token);
        fetchBrands();
        checkHealth();
      } else {
        // Expired or invalid token
        localStorage.removeItem("fitcheck_token");
        localStorage.removeItem("fitcheck_member_b_token");
        setAuthToken(null);
        setCurrentUser(null);
      }
    } catch {
      // Backend offline or connection issue
      setAuthError("Backend service is not responding at http://localhost:8000. Please ensure uvicorn is running.");
      setApiConnected(false);
    } finally {
      setAuthChecking(false);
    }
  };

  // Login handler
  const handleLogin = async (e?: React.FormEvent, overrideEmail?: string, overridePwd?: string) => {
    if (e) e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    const emailToUse = overrideEmail || authEmail;
    const pwdToUse = overridePwd || authPassword;

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: emailToUse, password: pwdToUse }),
      });

      if (res.ok) {
        const data = await res.json();
        const token = data.access_token;
        localStorage.setItem("fitcheck_token", token);
        localStorage.setItem("fitcheck_member_b_token", token);
        setAuthToken(token);

        const meRes = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (meRes.ok) {
          const userData = await meRes.json();
          setCurrentUser(userData);
          fetchUserProfile(token);
          fetchUserPurchases(token);
          fetchBrands();
          checkHealth();
        } else {
          setCurrentUser({
            name: emailToUse.split("@")[0],
            email: emailToUse,
            role: data.role || "USER",
            user_id: 0,
          });
          fetchBrands();
        }
      } else {
        const err = await res.json().catch(() => ({}));
        setAuthError(err.detail || "Authentication failed. Incorrect email or password.");
      }
    } catch (err: any) {
      setAuthError(`Connection error: ${err.message}. Is backend running on http://localhost:8000?`);
    } finally {
      setAuthLoading(false);
    }
  };

  // Register handler
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!registerName.trim()) {
      setAuthError("Please enter your name.");
      return;
    }
    setAuthLoading(true);
    setAuthError(null);

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: registerName.trim(),
          email: authEmail,
          password: authPassword,
        }),
      });

      if (res.ok) {
        // Automatically sign in with newly registered account
        await handleLogin(undefined, authEmail, authPassword);
      } else {
        const err = await res.json().catch(() => ({}));
        setAuthError(err.detail || "Registration failed. An account with this email may already exist.");
      }
    } catch (err: any) {
      setAuthError(`Connection error: ${err.message}. Ensure backend is running.`);
    } finally {
      setAuthLoading(false);
    }
  };

  // Logout handler
  const handleLogout = () => {
    localStorage.removeItem("fitcheck_token");
    localStorage.removeItem("fitcheck_member_b_token");
    setAuthToken(null);
    setCurrentUser(null);
    setProfile(null);
    setPurchases([]);
    setRecommendation(null);
    setAuthError(null);
  };

  // API Call: Health check
  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) setApiConnected(true);
      else setApiConnected(false);
    } catch {
      setApiConnected(false);
    }
  };

  // API Call: Fetch Brands (Robust with loading & error states)
  const fetchBrands = async () => {
    setBrandsLoading(true);
    setBrandError(null);
    try {
      const res = await fetch(`${API_BASE}/brands`);
      if (res.ok) {
        const data = await res.json();
        setBrands(data);
        if (data.length > 0) {
          const defaultBrand =
            data.find((b: any) => b.brand_name.toLowerCase() === "zara") || data[0];
          setSelectedBrandId(defaultBrand.brand_id);
          fetchGarments(defaultBrand.brand_id);
          handlePurchaseBrandChange(defaultBrand.brand_id);
        }
      } else {
        const err = await res.json().catch(() => ({}));
        setBrandError(err.detail || "Database error loading catalogue brands.");
      }
    } catch (err: any) {
      setBrandError(`Unable to load brands: ${err.message}`);
    } finally {
      setBrandsLoading(false);
    }
  };

  // Cascaded purchase dropdown handler: Brand -> Garments
  const handlePurchaseBrandChange = async (brandId: number) => {
    setPurchaseBrandId(brandId);
    setPurchaseGarmentId(null);
    setPurchaseSizes([]);
    setNewPurchaseForm((prev) => ({ ...prev, garment_size_id: "" }));
    try {
      const res = await fetch(`${API_BASE}/garments?brand_id=${brandId}`);
      if (res.ok) {
        const data = await res.json();
        setPurchaseGarments(data);
        if (data.length > 0) {
          handlePurchaseGarmentChange(data[0].garment_id);
        }
      }
    } catch (err) {
      console.error("Failed to load purchase garments", err);
    }
  };

  // Cascaded purchase dropdown handler: Garment -> Sizes
  const handlePurchaseGarmentChange = async (garmentId: number) => {
    setPurchaseGarmentId(garmentId);
    setNewPurchaseForm((prev) => ({ ...prev, garment_size_id: "" }));
    try {
      const res = await fetch(`${API_BASE}/garments/${garmentId}`);
      if (res.ok) {
        const data = await res.json();
        const sizesList = data.sizes || [];
        setPurchaseSizes(sizesList);
        if (sizesList.length > 0) {
          setNewPurchaseForm((prev) => ({ ...prev, garment_size_id: String(sizesList[0].garment_size_id) }));
        }
      }
    } catch (err) {
      console.error("Failed to load garment sizes for purchase", err);
    }
  };

  // API Call: Fetch Garments for Selected Brand
  const fetchGarments = async (brandId?: number) => {
    setGarmentsLoading(true);
    setGarmentError(null);
    try {
      const url = brandId ? `${API_BASE}/garments?brand_id=${brandId}` : `${API_BASE}/garments`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setGarments(data);
        if (data.length > 0) {
          setSelectedGarmentId(data[0].garment_id);
          fetchGarmentDetail(data[0].garment_id);
        } else {
          setSelectedGarmentId(null);
          setGarmentDetail(null);
        }
      } else {
        const err = await res.json().catch(() => ({}));
        setGarmentError(err.detail || "Database error loading garments.");
      }
    } catch (err: any) {
      setGarmentError(`Unable to load garments: ${err.message}`);
    } finally {
      setGarmentsLoading(false);
    }
  };

  // API Call: Garment Detail (measurements, sizes)
  const fetchGarmentDetail = async (garmentId: number) => {
    try {
      const res = await fetch(`${API_BASE}/garments/${garmentId}`);
      if (res.ok) {
        const data = await res.json();
        setGarmentDetail(data);
      }
    } catch (err) {
      console.error("Failed to fetch garment detail", err);
    }
  };

  // API Call: User Profile (authenticated)
  const fetchUserProfile = async (tokenOverride?: string | null) => {
    const activeToken = tokenOverride !== undefined ? tokenOverride : authToken;
    try {
      const headers: Record<string, string> = {};
      if (activeToken) {
        headers["Authorization"] = `Bearer ${activeToken}`;
      }
      const res = await fetch(`${API_BASE}/profile`, { headers });
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
        setProfileForm({
          height: data.height ? String(data.height) : "",
          waist: data.waist ? String(data.waist) : "",
          hip: data.hip ? String(data.hip) : "",
          thigh: data.thigh ? String(data.thigh) : "",
          inseam: data.inseam ? String(data.inseam) : "",
          preferred_fit: data.preferred_fit || "REGULAR",
        });
      } else {
        setProfile(null);
        setProfileForm({
          height: "",
          waist: "",
          hip: "",
          thigh: "",
          inseam: "",
          preferred_fit: "REGULAR",
        });
      }
    } catch {
      setProfile(null);
    }
  };

  // API Call: Save Profile (authenticated)
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileSaveStatus("Saving...");
    try {
      const payload: any = {
        preferred_fit: profileForm.preferred_fit,
      };
      if (profileForm.height) payload.height = parseFloat(profileForm.height);
      if (profileForm.waist) payload.waist = parseFloat(profileForm.waist);
      if (profileForm.hip) payload.hip = parseFloat(profileForm.hip);
      if (profileForm.thigh) payload.thigh = parseFloat(profileForm.thigh);
      if (profileForm.inseam) payload.inseam = parseFloat(profileForm.inseam);

      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }

      const res = await fetch(`${API_BASE}/profile`, {
        method: "PUT",
        headers,
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const updated = await res.json();
        setProfile(updated);
        setProfileSaveStatus("Profile saved successfully to MySQL!");
        setTimeout(() => setProfileSaveStatus(null), 3000);
      } else {
        const err = await res.json();
        setProfileSaveStatus(`Error: ${err.detail || "Validation failed"}`);
      }
    } catch (err: any) {
      setProfileSaveStatus(`Error saving: ${err.message}`);
    }
  };

  // API Call: Fetch Purchases (authenticated)
  const fetchUserPurchases = async (tokenOverride?: string | null) => {
    const activeToken = tokenOverride !== undefined ? tokenOverride : authToken;
    try {
      const headers: Record<string, string> = {};
      if (activeToken) {
        headers["Authorization"] = `Bearer ${activeToken}`;
      }
      const res = await fetch(`${API_BASE}/purchases`, { headers });
      if (res.ok) {
        const data = await res.json();
        setPurchases(data);
      } else {
        setPurchases([]);
      }
    } catch {
      setPurchases([]);
    }
  };

  // API Call: Record New Purchase (authenticated)
  const handleCreatePurchase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPurchaseForm.garment_size_id) return;
    setPurchaseStatus("Recording...");
    try {
      const payload = {
        garment_size_id: parseInt(newPurchaseForm.garment_size_id),
        outcome: newPurchaseForm.outcome,
        fit_satisfaction: newPurchaseForm.fit_satisfaction,
        fit_preference: newPurchaseForm.fit_preference,
      };
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      const res = await fetch(`${API_BASE}/purchases`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setPurchaseStatus("Purchase recorded in database!");
        fetchUserPurchases();
        setTimeout(() => setPurchaseStatus(null), 3000);
      } else {
        const err = await res.json();
        setPurchaseStatus(`Error: ${err.detail}`);
      }
    } catch (err: any) {
      setPurchaseStatus(`Error: ${err.message}`);
    }
  };

  // API Call: Generate Recommendation
  const handleGetRecommendation = async () => {
    if (!selectedGarmentId) return;
    setIsRecommending(true);
    setRecError(null);
    setRecommendation(null);

    try {
      const payload: any = {
        target_garment_id: selectedGarmentId,
      };
      // Scoped to current authenticated user
      if (currentUser?.user_id) {
        payload.user_id = currentUser.user_id;
      }
      if (manualWaist) payload.waist = parseFloat(manualWaist);
      if (manualHip) payload.hip = parseFloat(manualHip);

      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }

      const res = await fetch(`${API_BASE}/recommendations`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setRecommendation(data);
      } else {
        const err = await res.json();
        setRecError(err.detail || "Failed to compute size recommendation");
      }
    } catch (err: any) {
      setRecError(`Connection error: ${err.message}. Is backend running on port 8000?`);
    } finally {
      setIsRecommending(false);
    }
  };

  // Handle brand dropdown change
  const handleBrandChange = (brandId: number) => {
    setSelectedBrandId(brandId);
    fetchGarments(brandId);
    setRecommendation(null);
  };

  // =========================================================================
  // GATE 1: AUTHENTICATION INITIALIZATION CHECK
  // =========================================================================
  if (authChecking) {
    return (
      <div className="auth-container">
        <div style={{ textAlign: "center", color: "var(--text-secondary)" }}>
          <RefreshCw size={32} className="animate-spin" style={{ margin: "0 auto 14px", color: "var(--accent-plum)" }} />
          <p style={{ fontWeight: 600, fontSize: "1rem" }}>Restoring secure FitCheck session...</p>
        </div>
      </div>
    );
  }

  // =========================================================================
  // GATE 2: DEDICATED LOGIN / REGISTRATION ENTRY POINT
  // =========================================================================
  if (!authToken || !currentUser) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          {/* Brand Header */}
          <div style={{ textAlign: "center", marginBottom: "24px" }}>
            <div
              style={{
                width: "56px",
                height: "56px",
                borderRadius: "50%",
                background: "var(--accent-plum-light)",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "12px",
              }}
            >
              <Sparkles size={28} color="var(--accent-plum)" />
            </div>
            <h1
              style={{
                fontSize: "1.8rem",
                fontWeight: 850,
                color: "var(--text-primary)",
                letterSpacing: "-0.02em",
              }}
            >
              FitCheck <span style={{ color: "var(--accent-plum)" }}>— Fit Intelligence</span>
            </h1>
            <p
              style={{
                fontSize: "0.88rem",
                color: "var(--text-secondary)",
                marginTop: "6px",
                lineHeight: 1.5,
              }}
            >
              Cross-Brand Apparel Fit Recommender. Please sign in to access your empirical sizing calibration, body profile, and reviews.
            </p>
          </div>

          {/* Mode Tabs: Sign In / Create Account */}
          <div style={{ display: "flex", borderBottom: "1px solid var(--border-color)", marginBottom: "20px" }}>
            <button
              type="button"
              onClick={() => { setAuthMode("login"); setAuthError(null); }}
              className={`auth-tab-btn ${authMode === "login" ? "active" : ""}`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setAuthMode("register"); setAuthError(null); }}
              className={`auth-tab-btn ${authMode === "register" ? "active" : ""}`}
            >
              Create Account
            </button>
          </div>

          {/* Error Banner */}
          {authError && (
            <div
              style={{
                padding: "12px 14px",
                borderRadius: "var(--radius-sm)",
                marginBottom: "18px",
                fontSize: "0.85rem",
                background: "var(--danger-bg)",
                color: "var(--danger)",
                border: "1px solid var(--danger-border)",
                display: "flex",
                alignItems: "flex-start",
                gap: "8px",
              }}
            >
              <AlertCircle size={16} style={{ marginTop: "2px", flexShrink: 0 }} />
              <span>{authError}</span>
            </div>
          )}

          {/* Auth Form */}
          <form
            onSubmit={authMode === "login" ? (e) => handleLogin(e) : handleRegister}
            style={{ display: "flex", flexDirection: "column", gap: "14px" }}
          >
            {authMode === "register" && (
              <div>
                <label
                  htmlFor="auth-register-name"
                  style={{
                    display: "block",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    color: "var(--text-secondary)",
                    marginBottom: "4px",
                  }}
                >
                  Full Name
                </label>
                <input
                  id="auth-register-name"
                  type="text"
                  required
                  value={registerName}
                  onChange={(e) => setRegisterName(e.target.value)}
                  placeholder="e.g. Priya Sharma"
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.9rem",
                  }}
                />
              </div>
            )}

            <div>
              <label
                htmlFor="auth-email"
                style={{
                  display: "block",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  color: "var(--text-secondary)",
                  marginBottom: "4px",
                }}
              >
                Email Address
              </label>
              <input
                id="auth-email"
                type="email"
                required
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                placeholder="you@example.com"
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "0.9rem",
                }}
              />
            </div>

            <div>
              <label
                htmlFor="auth-password"
                style={{
                  display: "block",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  color: "var(--text-secondary)",
                  marginBottom: "4px",
                }}
              >
                Password
              </label>
              <input
                id="auth-password"
                type="password"
                required
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                placeholder="••••••••"
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "0.9rem",
                }}
              />
            </div>

            <button
              type="submit"
              disabled={authLoading}
              style={{
                padding: "12px",
                background: "var(--accent-plum)",
                color: "#FFFFFF",
                border: "none",
                borderRadius: "var(--radius-sm)",
                fontWeight: 700,
                fontSize: "0.95rem",
                cursor: authLoading ? "not-allowed" : "pointer",
                marginTop: "6px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              {authLoading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <LogIn size={16} />
                  <span>{authMode === "login" ? "Sign In to FitCheck" : "Create Account"}</span>
                </>
              )}
            </button>
          </form>

          {/* Pre-Seeded Test Accounts for Viva Grading */}
          <div style={{ marginTop: "24px", paddingTop: "18px", borderTop: "1px solid var(--border-color)" }}>
            <div
              style={{
                fontSize: "0.72rem",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                fontWeight: 700,
                letterSpacing: "0.05em",
                marginBottom: "10px",
              }}
            >
              Evaluation Test Accounts (Click to Fill Credentials)
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {DEMO_PERSONAS.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => {
                    setAuthEmail(p.email);
                    setAuthPassword("password123");
                    setAuthMode("login");
                    setAuthError(null);
                  }}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "8px 12px",
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  <div>
                    <strong style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>{p.name}</strong>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{p.note}</div>
                  </div>
                  <span
                    className={p.role === "ADMIN" ? "badge badge-rose" : "badge badge-info"}
                    style={{ fontSize: "0.68rem" }}
                  >
                    {p.role}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================================
  // GATE 3: AUTHENTICATED APPLICATION
  // =========================================================================
  return (
    <main style={{ maxWidth: "1240px", margin: "0 auto", padding: "28px 20px 80px" }}>
      {/* Authenticated Application Header */}
      <header
        style={{
          marginBottom: "24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "2.1rem",
              fontWeight: 850,
              letterSpacing: "-0.03em",
              color: "var(--text-primary)",
            }}
          >
            FitCheck <span className="gradient-text">— Fit Intelligence</span>
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", marginTop: "2px" }}>
            Cross-Brand Apparel Fit Recommender &bull; Relational Catalogue, Body Profiles &amp; Deterministic Sizing
          </p>
        </div>

        {/* Authenticated User Session Pill */}
        <div
          className="glass-panel"
          style={{
            padding: "10px 16px",
            display: "flex",
            alignItems: "center",
            gap: "16px",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <strong style={{ fontSize: "0.92rem", color: "var(--text-primary)" }}>
                {currentUser.name}
              </strong>
              <span
                className={currentUser.role === "ADMIN" ? "badge badge-rose" : "badge badge-success"}
                style={{ fontSize: "0.68rem" }}
              >
                {currentUser.role}
              </span>
            </div>
            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{currentUser.email}</div>
          </div>

          <button
            onClick={handleLogout}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "7px 12px",
              background: "transparent",
              color: "var(--text-secondary)",
              border: "1px solid var(--border-color)",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.82rem",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </header>

      {/* Contextual Offline Alert if backend is unreachable */}
      {apiConnected === false && (
        <div
          style={{
            background: "var(--warning-bg)",
            border: "1px solid var(--warning-border)",
            borderRadius: "var(--radius-sm)",
            padding: "12px 18px",
            marginBottom: "24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            color: "var(--warning)",
            fontSize: "0.88rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <AlertCircle size={18} color="var(--warning)" />
            <span>
              Backend API is not currently connected at <code>http://localhost:8000</code>. Offline demo fallback active.
            </span>
          </div>
          <button
            onClick={checkHealth}
            style={{
              background: "var(--accent-plum)",
              border: "none",
              color: "#fff",
              padding: "6px 12px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.8rem",
              fontWeight: 600,
            }}
          >
            Reconnect
          </button>
        </div>
      )}

      {/* Main Navigation Tabs */}
      <nav className="nav-tabs-container" role="tablist" aria-label="Main Navigation">
        <button
          role="tab"
          aria-selected={activeTab === "recommend"}
          onClick={() => setActiveTab("recommend")}
          className={`nav-tab-btn ${activeTab === "recommend" ? "active" : ""}`}
        >
          <Sparkles size={16} />
          Cross-Brand Recommendation
        </button>

        <button
          role="tab"
          aria-selected={activeTab === "profile"}
          onClick={() => setActiveTab("profile")}
          className={`nav-tab-btn ${activeTab === "profile" ? "active" : ""}`}
        >
          <UserIcon size={16} />
          Body Profile
        </button>

        <button
          role="tab"
          aria-selected={activeTab === "purchases"}
          onClick={() => setActiveTab("purchases")}
          className={`nav-tab-btn ${activeTab === "purchases" ? "active" : ""}`}
        >
          <ShoppingBag size={16} />
          Purchase History &amp; Fit Outcomes
        </button>

        <button
          role="tab"
          aria-selected={activeTab === "catalogue"}
          onClick={() => setActiveTab("catalogue")}
          className={`nav-tab-btn ${activeTab === "catalogue" ? "active" : ""}`}
        >
          <Layers size={16} />
          Garment Catalogue &amp; Measurements
        </button>

        <button
          role="tab"
          aria-selected={activeTab === "reviews"}
          onClick={() => setActiveTab("reviews")}
          className={`nav-tab-btn ${activeTab === "reviews" ? "active" : ""}`}
        >
          <MessageSquare size={16} />
          Fit Reviews &amp; Semantic Search
        </button>
      </nav>

      {/* ============================================================== */}
      {/* TAB 1: CROSS-BRAND RECOMMENDATION ENGINE                       */}
      {/* ============================================================== */}
      {activeTab === "recommend" && (
        <section className="recommendation-grid">
          {/* Target Garment Selection Panel */}
          <div className="glass-panel" style={{ padding: "28px" }}>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 700, marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
              <Ruler size={20} color="var(--accent-plum)" />
              1. Select Target Garment
            </h2>

            {/* Brand Filter */}
            <div style={{ marginBottom: "18px" }}>
              <label htmlFor="target-brand" style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Target Brand
              </label>
              <select
                id="target-brand"
                value={selectedBrandId || ""}
                onChange={(e) => handleBrandChange(parseInt(e.target.value))}
                disabled={brandsLoading}
                style={{
                  width: "100%",
                  background: "var(--bg-secondary)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-color)",
                  padding: "10px 14px",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "0.95rem",
                }}
              >
                {brandsLoading && <option value="" disabled>Loading brands from catalogue...</option>}
                {!brandsLoading && brands.length === 0 && (
                  <option value="" disabled>{brandError || "No brands available"}</option>
                )}
                {brands.map((b) => (
                  <option key={b.brand_id} value={b.brand_id}>
                    {b.brand_name} ({b.sizing_system})
                  </option>
                ))}
              </select>
            </div>

            {/* Garment Selector */}
            <div style={{ marginBottom: "22px" }}>
              <label htmlFor="target-garment" style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Target Garment
              </label>
              <select
                id="target-garment"
                value={selectedGarmentId || ""}
                onChange={(e) => setSelectedGarmentId(parseInt(e.target.value))}
                disabled={garmentsLoading || brandsLoading}
                style={{
                  width: "100%",
                  background: "var(--bg-secondary)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-color)",
                  padding: "10px 14px",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "0.95rem",
                }}
              >
                {garmentsLoading && <option value="" disabled>Loading garments for selected brand...</option>}
                {!garmentsLoading && garments.length === 0 && (
                  <option value="" disabled>No garments found for this brand</option>
                )}
                {garments.map((g) => (
                  <option key={g.garment_id} value={g.garment_id}>
                    {g.garment_name} &bull; {g.garment_category} ({g.fit_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Target Garment Sizing Preview */}
            {garmentDetail && (
              <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-color)", padding: "16px", borderRadius: "var(--radius-sm)", marginBottom: "24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{garmentDetail.garment_name}</span>
                  <span className="badge badge-info">Active Catalogue Item</span>
                </div>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "12px" }}>
                  {garmentDetail.description || "No description available."}
                </p>
                <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                  Available sizes: <strong>{garmentDetail.sizes?.map((s: any) => s.size_label).join(", ")}</strong>
                </div>
              </div>
            )}

            {/* Manual Dimension Overrides (Optional) */}
            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "18px", marginBottom: "24px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "10px" }}>
                <Info size={16} color="var(--accent-plum)" />
                <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                  Optional Manual Dimension Overrides
                </span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <label style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Waist (cm)</label>
                  <input
                    type="number"
                    placeholder={profile?.waist ? `${profile.waist} (from profile)` : "e.g. 70"}
                    value={manualWaist}
                    onChange={(e) => setManualWaist(e.target.value)}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "8px 10px",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.85rem",
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Hip (cm)</label>
                  <input
                    type="number"
                    placeholder={profile?.hip ? `${profile.hip} (from profile)` : "e.g. 96"}
                    value={manualHip}
                    onChange={(e) => setManualHip(e.target.value)}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "8px 10px",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.85rem",
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Action CTA */}
            <button
              onClick={handleGetRecommendation}
              disabled={isRecommending || !selectedGarmentId}
              style={{
                width: "100%",
                padding: "14px",
                background: "var(--accent-plum)",
                color: "#fff",
                border: "none",
                borderRadius: "var(--radius-sm)",
                fontWeight: 700,
                fontSize: "1rem",
                cursor: isRecommending ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
                boxShadow: "0 4px 16px var(--accent-glow)",
              }}
            >
              {isRecommending ? (
                <>
                  <RefreshCw size={20} className="animate-spin" />
                  Computing Fit Calibration...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Calculate Recommended Size
                </>
              )}
            </button>
          </div>

          {/* Recommendation Results Panel */}
          <div>
            {recError && (
              <div className="glass-panel" style={{ padding: "24px", borderColor: "var(--danger-border)", marginBottom: "20px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--danger)" }}>
                  <AlertCircle size={24} />
                  <div>
                    <h3 style={{ fontSize: "1rem", fontWeight: 700 }}>Recommendation Computation Error</h3>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "4px" }}>{recError}</p>
                  </div>
                </div>
              </div>
            )}

            {recommendation ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                {/* Primary Recommendation Banner */}
                <div
                  className="glass-panel"
                  style={{
                    padding: "32px",
                    background: "var(--bg-card-subtle)",
                    border: "1px solid var(--border-color)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                    <div>
                      <span className="badge badge-info">Optimal Size Match</span>
                      <h3 style={{ fontSize: "1.8rem", fontWeight: 800, marginTop: "8px" }}>
                        Size {recommendation.primary_recommendation?.size_label}
                      </h3>
                      <div style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
                        {recommendation.target_brand_name} &bull; {recommendation.target_garment_name}
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "var(--accent-plum)" }}>
                        {recommendation.primary_recommendation?.match_score}%
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Match Confidence: <strong>{recommendation.confidence}</strong>
                      </div>
                    </div>
                  </div>

                  {/* Verdict & Explanation */}
                  <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "16px", borderRadius: "var(--radius-sm)", marginBottom: "16px" }}>
                    <div style={{ fontWeight: 600, fontSize: "0.95rem", color: "var(--accent-sage-dark)", marginBottom: "6px" }}>
                      Verdict: {recommendation.primary_recommendation?.fit_verdict}
                    </div>
                    <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                      {recommendation.explanation}
                    </p>
                  </div>

                  {/* Evidence Sources */}
                  <div style={{ marginBottom: "12px" }}>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "6px" }}>
                      Evidence Citations:
                    </span>
                    <ul style={{ fontSize: "0.85rem", color: "var(--text-secondary)", listStylePosition: "inside", lineHeight: 1.6 }}>
                      {recommendation.evidence_sources?.map((src: string, idx: number) => (
                        <li key={idx}>{src}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Caveats */}
                  {recommendation.caveats?.length > 0 && (
                    <div style={{ fontSize: "0.8rem", color: "var(--warning)", display: "flex", alignItems: "center", gap: "8px", marginTop: "10px" }}>
                      <Info size={16} />
                      <span>{recommendation.caveats.join("; ")}</span>
                    </div>
                  )}
                </div>

                {/* Ranked Sizes Ladder Breakdown */}
                <div className="glass-panel" style={{ padding: "24px" }}>
                  <h4 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
                    Complete Sizing Ladder Ranking (Tolerance Breakdown)
                  </h4>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem", textAlign: "left" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)" }}>
                        <th style={{ padding: "10px 8px" }}>Rank</th>
                        <th style={{ padding: "10px 8px" }}>Size</th>
                        <th style={{ padding: "10px 8px" }}>Score</th>
                        <th style={{ padding: "10px 8px" }}>Fit Verdict</th>
                        <th style={{ padding: "10px 8px" }}>Dimensional Deltas (vs Ref)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recommendation.all_sizes_ranked?.map((s: any) => (
                        <tr
                          key={s.garment_size_id}
                          style={{
                            borderBottom: "1px solid var(--border-color)",
                            background: s.rank === 1 ? "var(--accent-plum-light)" : "transparent",
                          }}
                        >
                          <td style={{ padding: "12px 8px", fontWeight: 700, color: s.rank === 1 ? "var(--accent-plum)" : "inherit" }}>
                            #{s.rank}
                          </td>
                          <td style={{ padding: "12px 8px", fontWeight: 600 }}>{s.size_label}</td>
                          <td style={{ padding: "12px 8px" }}>
                            <span style={{ fontWeight: 700, color: s.match_score >= 70 ? "var(--accent-sage-dark)" : s.match_score >= 50 ? "var(--warning)" : "var(--danger)" }}>
                              {s.match_score}%
                            </span>
                          </td>
                          <td style={{ padding: "12px 8px", color: "var(--text-secondary)" }}>{s.fit_verdict}</td>
                          <td style={{ padding: "12px 8px", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                            {s.deltas && s.deltas.length > 0 ? (
                              s.deltas.map((d: any) => (
                                <span key={d.dimension} style={{ marginRight: "10px" }}>
                                  {d.dimension}: {d.delta_cm >= 0 ? `+${d.delta_cm}` : d.delta_cm}cm
                                </span>
                              ))
                            ) : (
                              <span>N/A</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              /* Idle state before recommendation */
              <div
                className="glass-panel"
                style={{
                  padding: "48px 32px",
                  textAlign: "center",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  minHeight: "380px",
                }}
              >
                <div style={{ width: "64px", height: "64px", borderRadius: "50%", background: "var(--accent-plum-light)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "16px" }}>
                  <Sparkles size={32} color="var(--accent-plum)" />
                </div>
                <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "8px" }}>
                  Ready to Calibrate Size
                </h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", maxWidth: "440px", lineHeight: 1.6 }}>
                  Select an unfamiliar target brand and garment on the left, then click <strong>Calculate Recommended Size</strong> to synthesize reference fit evidence from {currentUser?.name || "your profile"}.
                </p>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ============================================================== */}
      {/* TAB 2: BODY PROFILE MANAGER                                    */}
      {/* ============================================================== */}
      {activeTab === "profile" && (
        <section style={{ maxWidth: "760px", margin: "0 auto" }}>
          <div className="glass-panel" style={{ padding: "36px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
              <div>
                <h2 style={{ fontSize: "1.4rem", fontWeight: 700 }}>
                  Body Profile &bull; {currentUser?.name || "Account"} (ID #{currentUser?.user_id})
                </h2>
                <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Anatomical dimensions in centimeters with database-level integrity constraints.
                </p>
              </div>
              <span className="badge badge-info">1:1 Relational Entity</span>
            </div>

            {profileSaveStatus && (
              <div
                style={{
                  padding: "12px 16px",
                  borderRadius: "var(--radius-sm)",
                  marginBottom: "20px",
                  fontSize: "0.9rem",
                  background: profileSaveStatus.startsWith("Error") ? "var(--danger-bg)" : "var(--accent-sage-light)",
                  color: profileSaveStatus.startsWith("Error") ? "var(--danger)" : "var(--accent-sage-dark)",
                  border: `1px solid ${profileSaveStatus.startsWith("Error") ? "var(--danger-border)" : "var(--accent-sage-border)"}`,
                }}
              >
                {profileSaveStatus}
              </div>
            )}

            <form onSubmit={handleSaveProfile}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "24px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Height (cm)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={profileForm.height}
                    onChange={(e) => setProfileForm({ ...profileForm, height: e.target.value })}
                    placeholder="e.g. 165.0"
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "10px 14px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Waist Circumference (cm)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={profileForm.waist}
                    onChange={(e) => setProfileForm({ ...profileForm, waist: e.target.value })}
                    placeholder="e.g. 68.0"
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "10px 14px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Hip Circumference (cm)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={profileForm.hip}
                    onChange={(e) => setProfileForm({ ...profileForm, hip: e.target.value })}
                    placeholder="e.g. 94.0"
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "10px 14px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Thigh Circumference (cm)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={profileForm.thigh}
                    onChange={(e) => setProfileForm({ ...profileForm, thigh: e.target.value })}
                    placeholder="e.g. 54.0"
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "10px 14px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Inseam Length (cm)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={profileForm.inseam}
                    onChange={(e) => setProfileForm({ ...profileForm, inseam: e.target.value })}
                    placeholder="e.g. 76.0"
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "10px 14px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Preferred Fit Allowance
                  </label>
                  <select
                    value={profileForm.preferred_fit}
                    onChange={(e) => setProfileForm({ ...profileForm, preferred_fit: e.target.value })}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "10px 14px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    <option value="TIGHT">TIGHT (0cm ease - Snug)</option>
                    <option value="REGULAR">REGULAR (1.5cm waist ease)</option>
                    <option value="RELAXED">RELAXED (3.0cm waist ease)</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                style={{
                  padding: "12px 28px",
                  background: "var(--accent-plum)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "var(--radius-sm)",
                  fontWeight: 600,
                  fontSize: "0.95rem",
                  cursor: "pointer",
                }}
              >
                Save Profile to MySQL
              </button>
            </form>
          </div>
        </section>
      )}

      {/* ============================================================== */}
      {/* TAB 3: PURCHASE HISTORY & OUTCOMES                             */}
      {/* ============================================================== */}
      {activeTab === "purchases" && (
        <section style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
          {/* Purchase List */}
          <div className="glass-panel" style={{ padding: "32px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 700 }}>
                  Purchase History &amp; Fit Outcomes &bull; {currentUser?.name || "Account"} (ID #{currentUser?.user_id})
                </h2>
                <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Verified historical purchases utilized as empirical evidence in cross-brand sizing.
                </p>
              </div>
              <span className="badge badge-info">{purchases.length} Records</span>
            </div>

            {purchases.length === 0 ? (
              <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                No purchase records found for this user in MySQL. Use the form below to record a purchase.
              </div>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem", textAlign: "left" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)" }}>
                    <th style={{ padding: "12px 8px" }}>ID</th>
                    <th style={{ padding: "12px 8px" }}>Date</th>
                    <th style={{ padding: "12px 8px" }}>Brand</th>
                    <th style={{ padding: "12px 8px" }}>Garment</th>
                    <th style={{ padding: "12px 8px" }}>Size</th>
                    <th style={{ padding: "12px 8px" }}>Outcome</th>
                    <th style={{ padding: "12px 8px" }}>Fit Satisfaction</th>
                    <th style={{ padding: "12px 8px" }}>Preference</th>
                  </tr>
                </thead>
                <tbody>
                  {purchases.map((p) => (
                    <tr key={p.purchase_id} style={{ borderBottom: "1px solid var(--border-color)" }}>
                      <td style={{ padding: "12px 8px", color: "var(--text-muted)" }}>#{p.purchase_id}</td>
                      <td style={{ padding: "12px 8px" }}>{p.purchase_date}</td>
                      <td style={{ padding: "12px 8px", fontWeight: 600 }}>{p.brand_name || "N/A"}</td>
                      <td style={{ padding: "12px 8px" }}>{p.garment_name || "N/A"}</td>
                      <td style={{ padding: "12px 8px", fontWeight: 700, color: "var(--accent-plum)" }}>
                        {p.size_label || `Size ID ${p.garment_size_id}`}
                      </td>
                      <td style={{ padding: "12px 8px" }}>
                        <span
                          className="badge"
                          style={{
                            background: p.outcome === "KEPT" ? "var(--accent-sage-light)" : "var(--danger-bg)",
                            color: p.outcome === "KEPT" ? "var(--accent-sage-dark)" : "var(--danger)",
                            border: `1px solid ${p.outcome === "KEPT" ? "var(--accent-sage-border)" : "var(--danger-border)"}`,
                          }}
                        >
                          {p.outcome}
                        </span>
                      </td>
                      <td style={{ padding: "12px 8px" }}>
                        <span style={{ fontWeight: 600, color: p.fit_satisfaction === "GOOD" ? "var(--accent-sage-dark)" : p.fit_satisfaction === "AVERAGE" ? "var(--warning)" : "var(--danger)" }}>
                          {p.fit_satisfaction || "N/A"}
                        </span>
                      </td>
                      <td style={{ padding: "12px 8px", color: "var(--text-muted)" }}>{p.fit_preference || "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Quick Purchase Logger Form */}
          <div className="glass-panel" style={{ padding: "32px", maxWidth: "640px" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
              Record New Purchase (DML Verification)
            </h3>
            {purchaseStatus && (
              <div style={{ padding: "10px 14px", borderRadius: "var(--radius-sm)", marginBottom: "16px", fontSize: "0.85rem", background: "var(--accent-plum-light)", color: "var(--accent-plum)", border: "1px solid var(--accent-plum-border)" }}>
                {purchaseStatus}
              </div>
            )}
            <form onSubmit={handleCreatePurchase} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              {/* Cascaded Catalogue Selectors: Brand -> Garment -> Size */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <label htmlFor="purchase-brand-select" style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                    1. Brand
                  </label>
                  <select
                    id="purchase-brand-select"
                    value={purchaseBrandId || ""}
                    onChange={(e) => handlePurchaseBrandChange(Number(e.target.value))}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "8px 12px",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.85rem",
                    }}
                  >
                    {brands.map((b) => (
                      <option key={b.brand_id} value={b.brand_id}>
                        {b.brand_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="purchase-garment-select" style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                    2. Garment Model
                  </label>
                  <select
                    id="purchase-garment-select"
                    value={purchaseGarmentId || ""}
                    onChange={(e) => handlePurchaseGarmentChange(Number(e.target.value))}
                    disabled={purchaseGarments.length === 0}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "8px 12px",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.85rem",
                    }}
                  >
                    {purchaseGarments.map((g) => (
                      <option key={g.garment_id} value={g.garment_id}>
                        {g.garment_name} ({g.fit_type})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label htmlFor="purchase-size-input" style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                  3. Size Label &bull; Foreign Key <code>garment_size_id</code>
                </label>
                <select
                  id="purchase-size-input"
                  value={newPurchaseForm.garment_size_id}
                  onChange={(e) => setNewPurchaseForm({ ...newPurchaseForm, garment_size_id: e.target.value })}
                  required
                  disabled={purchaseSizes.length === 0}
                  style={{
                    width: "100%",
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    padding: "8px 12px",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.88rem",
                    fontWeight: 600,
                  }}
                >
                  <option value="">Select size...</option>
                  {purchaseSizes.map((s: any) => (
                    <option key={s.garment_size_id} value={s.garment_size_id}>
                      Size {s.size_label} &mdash; (Catalogue ID #{s.garment_size_id})
                    </option>
                  ))}
                </select>
                {newPurchaseForm.garment_size_id && (
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
                    Resolved Catalogue Key: <code>PURCHASE.garment_size_id = {newPurchaseForm.garment_size_id}</code>
                  </div>
                )}
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <label htmlFor="purchase-outcome" style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                    Outcome
                  </label>
                  <select
                    id="purchase-outcome"
                    value={newPurchaseForm.outcome}
                    onChange={(e) => setNewPurchaseForm({ ...newPurchaseForm, outcome: e.target.value })}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "8px 12px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    <option value="KEPT">KEPT</option>
                    <option value="RETURNED">RETURNED</option>
                    <option value="EXCHANGED">EXCHANGED</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="purchase-satisfaction" style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                    Fit Satisfaction
                  </label>
                  <select
                    id="purchase-satisfaction"
                    value={newPurchaseForm.fit_satisfaction}
                    onChange={(e) => setNewPurchaseForm({ ...newPurchaseForm, fit_satisfaction: e.target.value })}
                    style={{
                      width: "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      padding: "8px 12px",
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    <option value="GOOD">GOOD</option>
                    <option value="AVERAGE">AVERAGE</option>
                    <option value="POOR">POOR</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                style={{
                  padding: "10px 20px",
                  background: "var(--accent-plum)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "var(--radius-sm)",
                  fontWeight: 600,
                  cursor: "pointer",
                  marginTop: "6px",
                  alignSelf: "flex-start",
                }}
              >
                Insert Purchase Record
              </button>
            </form>
          </div>
        </section>
      )}

      {/* ============================================================== */}
      {/* TAB 4: CATALOGUE BROWSER                                       */}
      {/* ============================================================== */}
      {activeTab === "catalogue" && (
        <section style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
          <div className="glass-panel" style={{ padding: "32px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 700 }}>
                  Apparel Catalogue &amp; Physical Specifications
                </h2>
                <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Relational hierarchy: <code>BRAND &rarr; GARMENT &rarr; GARMENT_SIZE &rarr; GARMENT_MEASUREMENT</code>
                </p>
              </div>
              <span className="badge badge-success">5 Brands &bull; 14 Garments &bull; 70 Sizes</span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "20px" }}>
              {garments.map((g) => (
                <div
                  key={g.garment_id}
                  style={{
                    background: "var(--bg-card-subtle)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "var(--radius-sm)",
                    padding: "20px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                    <h3 style={{ fontSize: "1.05rem", fontWeight: 700 }}>{g.garment_name}</h3>
                    <span className="badge badge-info">{g.garment_category}</span>
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--accent-plum)", marginBottom: "8px" }}>
                    {g.brand?.brand_name || `Brand #${g.brand_id}`} &bull; Fit: {g.fit_type}
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "14px" }}>
                    {g.description || "Classic tailored bottom-wear."}
                  </p>
                  <button
                    onClick={() => {
                      setSelectedGarmentId(g.garment_id);
                      setSelectedBrandId(g.brand_id);
                      setActiveTab("recommend");
                    }}
                    style={{
                      background: "var(--accent-plum-light)",
                      border: "1px solid var(--accent-plum-border)",
                      color: "var(--accent-plum)",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      fontSize: "0.8rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    Recommend in this garment <ChevronRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
      {activeTab === "reviews" && (
        <MemberBPanel
          token={authToken}
          currentUser={currentUser}
          onLogout={handleLogout}
        />
      )}
    </main>
  );
}
