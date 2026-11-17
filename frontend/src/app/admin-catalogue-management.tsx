"use client";

import React, { useEffect, useState } from "react";

interface Measurement {
  measurement_id: number;
  measurement_type: string;
  measurement_value: number;
  unit: string;
}
interface Size {
  garment_size_id: number;
  size_label: string;
  measurements: Measurement[];
}
interface Garment {
  garment_id: number;
  garment_name: string;
  garment_category: string;
  fit_type: string;
  description?: string;
  sizes?: Size[];
}

const inputStyle: React.CSSProperties = {
  width: "100%", background: "var(--bg-secondary)", border: "1px solid var(--border-color)",
  color: "var(--text-primary)", padding: "10px 12px", borderRadius: "var(--radius-sm)",
};
const labelStyle: React.CSSProperties = { display: "block", marginBottom: "6px", color: "var(--text-secondary)", fontSize: "0.85rem" };
const buttonStyle: React.CSSProperties = { padding: "10px 16px", background: "var(--accent-plum)", color: "#fff", border: "none", borderRadius: "var(--radius-sm)", cursor: "pointer" };
const measurementTypes = ["waist", "hip", "thigh", "inseam", "rise"];

export default function AdminCatalogueManagement({ token, apiBase }: { token: string | null; apiBase: string }) {
  const [brands, setBrands] = useState<{ brand_id: number; brand_name: string }[]>([]);
  const [brandId, setBrandId] = useState("");
  const [garments, setGarments] = useState<Garment[]>([]);
  const [garmentId, setGarmentId] = useState("");
  const [detail, setDetail] = useState<Garment | null>(null);
  const [sizeId, setSizeId] = useState("");
  const [newSize, setNewSize] = useState("");
  const [measurementType, setMeasurementType] = useState("waist");
  const [measurementValue, setMeasurementValue] = useState("");
  const [unit, setUnit] = useState("cm");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  const [garmentRevision, setGarmentRevision] = useState(0);
  const sizes = detail?.sizes || [];
  const selectedSize = sizes.find((size) => String(size.garment_size_id) === sizeId);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${apiBase}/brands`, { signal: controller.signal })
      .then(async (res) => { if (!res.ok) throw new Error("Unable to load brands."); return res.json(); })
      .then(setBrands)
      .catch((err) => { if (!controller.signal.aborted) setStatus(err.message); });
    return () => controller.abort();
  }, [apiBase]);

  useEffect(() => {
    if (!brandId) return;
    const controller = new AbortController();
    fetch(`${apiBase}/garments?brand_id=${brandId}`, { signal: controller.signal })
      .then(async (res) => { if (!res.ok) throw new Error("Unable to load garments."); return res.json(); })
      .then(setGarments)
      .catch((err) => { if (!controller.signal.aborted) setStatus(err.message); });
    return () => controller.abort();
  }, [apiBase, brandId, garmentRevision]);

  useEffect(() => {
    if (!garmentId) return;
    const controller = new AbortController();
    setDetail(null);
    fetch(`${apiBase}/garments/${garmentId}`, { signal: controller.signal })
      .then(async (res) => { if (!res.ok) throw new Error("Unable to load garment details."); return res.json(); })
      .then((data: Garment) => {
        setDetail(data);
        setSizeId((previous) => (data.sizes || []).some((size) => String(size.garment_size_id) === previous) ? previous : "");
      })
      .catch((err) => { if (!controller.signal.aborted) setStatus(err.message); });
    return () => controller.abort();
  }, [apiBase, garmentId, revision]);

  const writeCatalogue = async (path: string, method: string, payload?: object) => {
    const res = await fetch(`${apiBase}/admin${path}`, {
      method,
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      ...(payload ? { body: JSON.stringify(payload) } : {}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Check the catalogue values and try again.");
    return data;
  };

  const perform = async (action: () => Promise<void>) => {
    setBusy(true);
    setStatus("");
    try { await action(); } catch (err: any) { setStatus(err.message || "Catalogue update failed."); }
    finally { setBusy(false); }
  };

  const addSize = (e: React.FormEvent) => {
    e.preventDefault();
    if (!detail || !newSize.trim()) return;
    perform(async () => {
      const added = await writeCatalogue(`/garments/${garmentId}/sizes`, "POST", { size_label: newSize.trim() });
      setNewSize("");
      setSizeId(String(added.garment_size_id));
      setRevision((value) => value + 1);
      setStatus(`Size ${added.size_label} added.`);
    });
  };

  const addMeasurement = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSize) return;
    perform(async () => {
      await writeCatalogue(`/garment-sizes/${sizeId}/measurements`, "POST", {
        measurement_type: measurementType, measurement_value: Number(measurementValue), unit,
      });
      setMeasurementValue("");
      setRevision((value) => value + 1);
      setStatus("Measurement added.");
    });
  };

  const deleteSize = () => {
    if (!selectedSize || !window.confirm(`Delete size ${selectedSize.size_label} from this garment? Its associated catalogue measurements will also be removed.`)) return;
    perform(async () => {
      await writeCatalogue(`/garment-sizes/${sizeId}`, "DELETE");
      setSizeId("");
      setRevision((value) => value + 1);
      setStatus("Size and its associated catalogue measurements removed.");
    });
  };

  const deleteGarment = () => {
    if (!detail || !window.confirm(`Delete garment ${detail.garment_name}?`)) return;
    perform(async () => {
      await writeCatalogue(`/garments/${garmentId}`, "DELETE");
      setGarmentId("");
      setSizeId("");
      setDetail(null);
      setGarments([]);
      setGarmentRevision((value) => value + 1);
      setStatus("Garment removed.");
    });
  };

  return (
    <div className="glass-panel" style={{ padding: "28px" }}>
      <h3 style={{ marginBottom: "12px" }}>Catalogue Management</h3>
      <p style={{ color: "var(--text-secondary)", marginBottom: "16px" }}>Manage catalogue sizes and their physical measurements.</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "12px" }}>
        <div>
          <label htmlFor="catalogue-admin-brand" style={labelStyle}>Brand</label>
          <select id="catalogue-admin-brand" style={inputStyle} value={brandId} disabled={busy} onChange={(e) => {
            setBrandId(e.target.value); setGarments([]); setGarmentId(""); setDetail(null); setSizeId(""); setStatus("");
          }}>
            <option value="">Select brand...</option>
            {brands.map((brand) => <option key={brand.brand_id} value={brand.brand_id}>{brand.brand_name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="catalogue-admin-garment" style={labelStyle}>Garment</label>
          <select id="catalogue-admin-garment" style={inputStyle} value={garmentId} disabled={busy || !garments.length} onChange={(e) => {
            setGarmentId(e.target.value); setDetail(null); setSizeId(""); setStatus("");
          }}>
            <option value="">Select garment...</option>
            {garments.map((garment) => <option key={garment.garment_id} value={garment.garment_id}>{garment.garment_name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="catalogue-admin-size" style={labelStyle}>Size</label>
          <select id="catalogue-admin-size" style={inputStyle} value={sizeId} disabled={busy || !sizes.length} onChange={(e) => setSizeId(e.target.value)}>
            <option value="">Select size...</option>
            {sizes.map((size) => <option key={size.garment_size_id} value={size.garment_size_id}>{size.size_label}</option>)}
          </select>
        </div>
      </div>
      {detail && (
        <div style={{ marginTop: "18px" }}>
          <p>{detail.garment_name} · {detail.garment_category} · {detail.fit_type}</p>
          {detail.description && <p style={{ color: "var(--text-muted)" }}>{detail.description}</p>}
          <p style={{ marginTop: "8px" }}>Available sizes: {sizes.map((size) => size.size_label).join(", ") || "None"}</p>
          <form onSubmit={addSize} style={{ display: "flex", gap: "12px", alignItems: "end", marginTop: "16px", flexWrap: "wrap" }}>
            <div><label htmlFor="catalogue-new-size" style={labelStyle}>New size label</label>
              <input id="catalogue-new-size" value={newSize} onChange={(e) => setNewSize(e.target.value)} style={inputStyle} maxLength={20} required disabled={busy} />
            </div>
            <button type="submit" style={buttonStyle} disabled={busy}>Add Size</button>
          </form>
          {selectedSize && (
            <div style={{ marginTop: "18px" }}>
              <h4>Measurements for size {selectedSize.size_label}</h4>
              {selectedSize.measurements.length ? (
                <table style={{ width: "100%", marginTop: "10px", textAlign: "left" }}>
                  <thead><tr><th>Measurement</th><th>Value</th><th>Unit</th></tr></thead>
                  <tbody>{selectedSize.measurements.map((measurement) => <tr key={measurement.measurement_id}>
                    <td>{measurement.measurement_type}</td><td>{measurement.measurement_value}</td><td>{measurement.unit}</td>
                  </tr>)}</tbody>
                </table>
              ) : <p>No measurements yet.</p>}
              <form onSubmit={addMeasurement} style={{ display: "flex", gap: "12px", alignItems: "end", marginTop: "16px", flexWrap: "wrap" }}>
                <div><label htmlFor="catalogue-measurement-type" style={labelStyle}>Measurement Type</label>
                  <select id="catalogue-measurement-type" value={measurementType} onChange={(e) => setMeasurementType(e.target.value)} style={inputStyle} disabled={busy}>
                    {measurementTypes.map((type) => <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>)}
                  </select>
                </div>
                <div><label htmlFor="catalogue-measurement-value" style={labelStyle}>Value</label>
                  <input id="catalogue-measurement-value" type="number" min="0.01" max="9999.99" step="0.01" value={measurementValue} onChange={(e) => setMeasurementValue(e.target.value)} style={inputStyle} required disabled={busy} />
                </div>
                <div><label htmlFor="catalogue-measurement-unit" style={labelStyle}>Unit</label>
                  <select id="catalogue-measurement-unit" value={unit} onChange={(e) => setUnit(e.target.value)} style={inputStyle} disabled={busy}>
                    <option value="cm">cm</option><option value="in">in</option>
                  </select>
                </div>
                <button type="submit" style={buttonStyle} disabled={busy}>Add Measurement</button>
              </form>
              <button type="button" onClick={deleteSize} style={{ ...buttonStyle, marginTop: "16px" }} disabled={busy}>Delete Size</button>
            </div>
          )}
          <button type="button" onClick={deleteGarment} style={{ ...buttonStyle, marginTop: "16px" }} disabled={busy}>Delete Garment</button>
        </div>
      )}
      {status && <p role="status" style={{ marginTop: "14px", color: "var(--text-secondary)" }}>{status}</p>}
    </div>
  );
}
