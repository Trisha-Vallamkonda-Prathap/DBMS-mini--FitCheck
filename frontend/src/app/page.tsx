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
} from "lucide-react";

// API Base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Demo Users for fast switching during evaluation (authenticated via Member B auth)
const DEMO_USERS = [
  { id: 2, name: "Priya Sharma", email: "priya@example.com", note: "Kept Levis sz 28 (Good fit) — Ideal cross-brand demo" },
  { id: 3, name: "Ananya Rao", email: "ananya@example.com", note: "Petite (Waist 64cm), Kept sz 26 (Tight fit)" },
  { id: 5, name: "Kavya Iyer", email: "kavya@example.com", note: "Multi-brand evidence (Levis, Mango, Madewell)" },
  { id: 10, name: "Lakshmi Reddy", email: "lakshmi@example.com", note: "Cold-start test (No profile, no purchases)" },
];

export default function FitCheckMemberA() {
  // Navigation
  const [activeTab, setActiveTab] = useState<
    "recommend" | "profile" | "purchases" | "catalogue" | "reviews"
  >("recommend");
  const [selectedUserId, setSelectedUserId] = useState<number>(2);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Data states
  const [brands, setBrands] = useState<any[]>([]);
  const [garments, setGarments] = useState<any[]>([]);
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

  // Recommendation state
  const [recommendation, setRecommendation] = useState<any | null>(null);
  const [manualWaist, setManualWaist] = useState<string>("");
  const [manualHip, setManualHip] = useState<string>("");
  const [isRecommending, setIsRecommending] = useState<boolean>(false);
  const [recError, setRecError] = useState<string | null>(null);

  // Backend connectivity status
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Helper: Authenticate with Member B's login endpoint to obtain real JWT
  const loginDemoPersona = async (email: string): Promise<string | null> => {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password: "password123" }),
      });
      if (res.ok) {
        const data = await res.json();
        setAuthToken(data.access_token);
        return data.access_token;
      }
    } catch (err) {
      console.warn("Auto-login note: Backend offline or B-auth pending.", err);
    }
    return null;
  };

  // Initial load
  useEffect(() => {
    checkHealth();
    fetchBrands();
    fetchGarments();
  }, []);

  // When selected user changes, login and reload profile + purchases
  useEffect(() => {
    if (selectedUserId) {
      const user = DEMO_USERS.find((u) => u.id === selectedUserId);
      if (user) {
        loginDemoPersona(user.email).then((token) => {
          fetchUserProfile(token);
          fetchUserPurchases(token);
        });
      }
      setRecommendation(null);
      setRecError(null);
    }
  }, [selectedUserId]);

  // When selected garment changes, load detail
  useEffect(() => {
    if (selectedGarmentId) {
      fetchGarmentDetail(selectedGarmentId);
    } else {
      setGarmentDetail(null);
    }
  }, [selectedGarmentId]);

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

  // API Call: Fetch Brands
  const fetchBrands = async () => {
    try {
      const res = await fetch(`${API_BASE}/brands`);
      if (res.ok) {
        const data = await res.json();
        setBrands(data);
        if (data.length > 0 && !selectedBrandId) {
          // Default to Zara (brand 2) for cross-brand recommendation testing
          const zara = data.find((b: any) => b.brand_name.toLowerCase() === "zara") || data[0];
          setSelectedBrandId(zara.brand_id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch brands", err);
    }
  };

  // API Call: Fetch Garments
  const fetchGarments = async (brandId?: number) => {
    try {
      const url = brandId ? `${API_BASE}/garments?brand_id=${brandId}` : `${API_BASE}/garments`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setGarments(data);
        if (data.length > 0) {
          setSelectedGarmentId(data[0].garment_id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch garments", err);
    }
  };

  // API Call: Garment Detail
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
    } catch (err) {
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
      if (authToken) {
        payload.user_id = selectedUserId;
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

  return (
    <main style={{ maxWidth: "1280px", margin: "0 auto", padding: "36px 20px 80px" }}>
      {/* Top Header */}
      <header style={{ marginBottom: "32px", display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "20px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
            <span className="badge badge-info">Member A Contribution</span>
            <span className={`badge ${apiConnected ? "badge-success" : "badge-info"}`}>
              {apiConnected ? "API Connected (8000)" : "Backend Offline / Demo Mode"}
            </span>
          </div>
          <h1 style={{ fontSize: "2.4rem", fontWeight: 800, letterSpacing: "-0.03em" }}>
            FitCheck <span className="gradient-text">Fit Intelligence</span>
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", marginTop: "4px" }}>
            Cross-Brand Apparel Fit Recommender &bull; Relational Catalogue, Body Profiles &amp; Deterministic Tolerance Scoring
          </p>
        </div>

        {/* Demo User Switcher */}
        <div className="glass-panel" style={{ padding: "16px 20px", display: "flex", flexDirection: "column", gap: "8px" }}>
          <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
            Active Demo Persona (Viva Evaluation)
          </label>
          <select
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(parseInt(e.target.value))}
            style={{
              background: "var(--bg-secondary)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)",
              padding: "8px 12px",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.9rem",
              cursor: "pointer",
              outline: "none",
            }}
          >
            {DEMO_USERS.map((u) => (
              <option key={u.id} value={u.id}>
                User #{u.id}: {u.name}
              </option>
            ))}
          </select>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "8px", marginTop: "2px" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--accent-purple)" }}>
              {DEMO_USERS.find((u) => u.id === selectedUserId)?.note}
            </span>
            <span style={{ fontSize: "0.75rem", color: authToken ? "#10b981" : "#94a3b8" }}>
              {authToken ? "✓ Bearer JWT Active" : "• Guest / Unauthenticated"}
            </span>
          </div>
        </div>
      </header>

      {/* Offline Alert if backend is unreachable */}
      {apiConnected === false && (
        <div
          style={{
            background: "rgba(245, 158, 11, 0.15)",
            border: "1px solid rgba(245, 158, 11, 0.4)",
            borderRadius: "var(--radius-sm)",
            padding: "14px 20px",
            marginBottom: "28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            color: "#fde68a",
            fontSize: "0.9rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <AlertCircle size={20} color="#f59e0b" />
            <span>
              Backend is not connected on <code>http://localhost:8000</code>. Run <code>uvicorn backend.app.main:app --reload</code> in terminal to enable live MySQL queries.
            </span>
          </div>
          <button
            onClick={checkHealth}
            style={{
              background: "rgba(245, 158, 11, 0.3)",
              border: "none",
              color: "#fff",
              padding: "6px 14px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.8rem",
              fontWeight: 600,
            }}
          >
            Retry Ping
          </button>
        </div>
      )}

      {/* Main Navigation Tabs */}
      <nav style={{ display: "flex", gap: "12px", marginBottom: "32px", borderBottom: "1px solid var(--border-color)", paddingBottom: "12px", flexWrap: "wrap" }}>
        <button
          onClick={() => setActiveTab("recommend")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 20px",
            background: activeTab === "recommend" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "recommend" ? "#fff" : "var(--text-secondary)",
            border: "none",
            borderRadius: "var(--radius-sm)",
            cursor: "pointer",
            fontWeight: 600,
            fontSize: "0.95rem",
          }}
        >
          <Sparkles size={18} />
          Cross-Brand Recommendation
        </button>

        <button
          onClick={() => setActiveTab("profile")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 20px",
            background: activeTab === "profile" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "profile" ? "#fff" : "var(--text-secondary)",
            border: "none",
            borderRadius: "var(--radius-sm)",
            cursor: "pointer",
            fontWeight: 600,
            fontSize: "0.95rem",
          }}
        >
          <UserIcon size={18} />
          Body Profile
        </button>

        <button
          onClick={() => setActiveTab("purchases")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 20px",
            background: activeTab === "purchases" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "purchases" ? "#fff" : "var(--text-secondary)",
            border: "none",
            borderRadius: "var(--radius-sm)",
            cursor: "pointer",
            fontWeight: 600,
            fontSize: "0.95rem",
          }}
        >
          <ShoppingBag size={18} />
          Purchase History &amp; Fit Outcomes
        </button>

        <button
          onClick={() => setActiveTab("catalogue")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 20px",
            background: activeTab === "catalogue" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "catalogue" ? "#fff" : "var(--text-secondary)",
            border: "none",
            borderRadius: "var(--radius-sm)",
            cursor: "pointer",
            fontWeight: 600,
            fontSize: "0.95rem",
          }}
        >
          <Layers size={18} />
          Garment Catalogue &amp; Measurements
        </button>
        <button
          onClick={() => setActiveTab("reviews")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 20px",
            background:
              activeTab === "reviews" ? "var(--accent-gradient)" : "transparent",
            color:
              activeTab === "reviews" ? "#fff" : "var(--text-secondary)",
            border: "none",
            borderRadius: "var(--radius-sm)",
            cursor: "pointer",
            fontWeight: 600,
            fontSize: "0.95rem",
          }}
        >
          Fit Reviews & Semantic Search
        </button>
      </nav>

      {/* ============================================================== */}
      {/* TAB 1: CROSS-BRAND RECOMMENDATION ENGINE                       */}
      {/* ============================================================== */}
      {activeTab === "recommend" && (
        <section style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: "28px", alignItems: "start" }}>
          {/* Target Garment Selection Panel */}
          <div className="glass-panel" style={{ padding: "28px" }}>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 700, marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
              <Ruler size={20} color="var(--accent-purple)" />
              1. Select Target Garment
            </h2>

            {/* Brand Filter */}
            <div style={{ marginBottom: "18px" }}>
              <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Target Brand
              </label>
              <select
                value={selectedBrandId || ""}
                onChange={(e) => handleBrandChange(parseInt(e.target.value))}
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
                {brands.map((b) => (
                  <option key={b.brand_id} value={b.brand_id}>
                    {b.brand_name} ({b.sizing_system})
                  </option>
                ))}
              </select>
            </div>

            {/* Garment Selector */}
            <div style={{ marginBottom: "22px" }}>
              <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Target Garment
              </label>
              <select
                value={selectedGarmentId || ""}
                onChange={(e) => setSelectedGarmentId(parseInt(e.target.value))}
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
                {garments.map((g) => (
                  <option key={g.garment_id} value={g.garment_id}>
                    {g.garment_name} &bull; {g.garment_category} ({g.fit_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Target Garment Sizing Preview */}
            {garmentDetail && (
              <div style={{ background: "rgba(0,0,0,0.25)", padding: "16px", borderRadius: "var(--radius-sm)", marginBottom: "24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{garmentDetail.garment_name}</span>
                  <span className="badge badge-info">Integrated FitCheck Demo</span>                </div>
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
                <Info size={16} color="var(--accent-purple)" />
                <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                  Optional Manual Overrides (Guest Mode)
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
                background: "var(--accent-gradient)",
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
                boxShadow: "0 4px 20px var(--accent-glow)",
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
              <div className="glass-panel" style={{ padding: "24px", borderColor: "rgba(239, 68, 68, 0.4)", marginBottom: "20px" }}>
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
                    background: "linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)",
                    border: "1px solid rgba(99, 102, 241, 0.4)",
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
                      <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "var(--accent-purple)" }}>
                        {recommendation.primary_recommendation?.match_score}%
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Match Confidence: <strong>{recommendation.confidence}</strong>
                      </div>
                    </div>
                  </div>

                  {/* Verdict & Explanation */}
                  <div style={{ background: "rgba(0,0,0,0.3)", padding: "16px", borderRadius: "var(--radius-sm)", marginBottom: "16px" }}>
                    <div style={{ fontWeight: 600, fontSize: "0.95rem", color: "#34d399", marginBottom: "6px" }}>
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
                    <div style={{ fontSize: "0.8rem", color: "#fbbf24", display: "flex", alignItems: "center", gap: "8px", marginTop: "10px" }}>
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
                            borderBottom: "1px solid rgba(255,255,255,0.05)",
                            background: s.rank === 1 ? "rgba(99, 102, 241, 0.08)" : "transparent",
                          }}
                        >
                          <td style={{ padding: "12px 8px", fontWeight: 700, color: s.rank === 1 ? "var(--accent-purple)" : "inherit" }}>
                            #{s.rank}
                          </td>
                          <td style={{ padding: "12px 8px", fontWeight: 600 }}>{s.size_label}</td>
                          <td style={{ padding: "12px 8px" }}>
                            <span style={{ fontWeight: 700, color: s.match_score >= 70 ? "#34d399" : s.match_score >= 50 ? "#fbbf24" : "#f87171" }}>
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
                <div style={{ width: "64px", height: "64px", borderRadius: "50%", background: "rgba(99, 102, 241, 0.1)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "16px" }}>
                  <Sparkles size={32} color="var(--accent-purple)" />
                </div>
                <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "8px" }}>
                  Ready to Calibrate Size
                </h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", maxWidth: "440px", lineHeight: 1.6 }}>
                  Select an unfamiliar target brand and garment on the left, then click <strong>Calculate Recommended Size</strong> to synthesize reference fit evidence from user #{selectedUserId}.
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
                  Body Profile &bull; User #{selectedUserId}
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
                  background: profileSaveStatus.startsWith("Error") ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)",
                  color: profileSaveStatus.startsWith("Error") ? "var(--danger)" : "var(--success)",
                  border: `1px solid ${profileSaveStatus.startsWith("Error") ? "rgba(239, 68, 68, 0.3)" : "rgba(16, 185, 129, 0.3)"}`,
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
                  background: "var(--accent-gradient)",
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
                  Purchase History &amp; Fit Outcomes &bull; User #{selectedUserId}
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
                    <tr key={p.purchase_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                      <td style={{ padding: "12px 8px", color: "var(--text-muted)" }}>#{p.purchase_id}</td>
                      <td style={{ padding: "12px 8px" }}>{p.purchase_date}</td>
                      <td style={{ padding: "12px 8px", fontWeight: 600 }}>{p.brand_name || "N/A"}</td>
                      <td style={{ padding: "12px 8px" }}>{p.garment_name || "N/A"}</td>
                      <td style={{ padding: "12px 8px", fontWeight: 700, color: "var(--accent-purple)" }}>
                        {p.size_label || `Size ID ${p.garment_size_id}`}
                      </td>
                      <td style={{ padding: "12px 8px" }}>
                        <span
                          className="badge"
                          style={{
                            background: p.outcome === "KEPT" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                            color: p.outcome === "KEPT" ? "var(--success)" : "var(--danger)",
                            border: `1px solid ${p.outcome === "KEPT" ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
                          }}
                        >
                          {p.outcome}
                        </span>
                      </td>
                      <td style={{ padding: "12px 8px" }}>
                        <span style={{ fontWeight: 600, color: p.fit_satisfaction === "GOOD" ? "#34d399" : p.fit_satisfaction === "AVERAGE" ? "#fbbf24" : "#f87171" }}>
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
              <div style={{ padding: "10px 14px", borderRadius: "var(--radius-sm)", marginBottom: "16px", fontSize: "0.85rem", background: "rgba(99, 102, 241, 0.15)", color: "var(--accent-purple)" }}>
                {purchaseStatus}
              </div>
            )}
            <form onSubmit={handleCreatePurchase} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                  Garment Size ID (from Catalogue, e.g. 1 to 70)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 3 (Levis sz 28) or 18 (Zara sz 38)"
                  value={newPurchaseForm.garment_size_id}
                  onChange={(e) => setNewPurchaseForm({ ...newPurchaseForm, garment_size_id: e.target.value })}
                  required
                  style={{
                    width: "100%",
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    padding: "8px 12px",
                    borderRadius: "var(--radius-sm)",
                  }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                    Outcome
                  </label>
                  <select
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
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                    Fit Satisfaction
                  </label>
                  <select
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
                  background: "var(--accent-gradient)",
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
                    background: "rgba(0,0,0,0.25)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "var(--radius-sm)",
                    padding: "20px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                    <h3 style={{ fontSize: "1.05rem", fontWeight: 700 }}>{g.garment_name}</h3>
                    <span className="badge badge-info">{g.garment_category}</span>
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--accent-purple)", marginBottom: "8px" }}>
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
                      background: "rgba(99, 102, 241, 0.15)",
                      border: "1px solid rgba(99, 102, 241, 0.3)",
                      color: "var(--accent-purple)",
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
      {activeTab === "reviews" && <MemberBPanel />}
    </main>
  );
}
