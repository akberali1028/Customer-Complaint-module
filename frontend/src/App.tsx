import { type FormEvent, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { intakeFailed, intakeStarted, intakeSucceeded, resetComplaint, type RootState } from "./store";
import type { ComplaintFields } from "./types";

const groups: Array<{ title: string; fields: Array<[keyof ComplaintFields, string]> }> = [
  { title: "1. Origin & Customer Details", fields: [["complaint_source", "Complaint Source"], ["customer_name", "Customer Name"]] },
  { title: "2. Product & Batch Identification", fields: [["product_name", "Product Name"], ["product_strength_grade", "Product Strength/Grade"], ["batch_lot_number", "Batch/Lot Number"], ["manufacturing_date", "Manufacturing Date"], ["expiry_date", "Expiry Date"], ["quantity_affected", "Quantity Affected"]] },
  { title: "3. Complaint Details", fields: [["complaint_type", "Complaint Type"], ["complaint_date", "Complaint Date"], ["detailed_complaint_description", "Detailed Complaint Description"]] },
];

export function App() {
  const dispatch = useDispatch();
  const { result, status, error } = useSelector((state: RootState) => state.complaint);
  const [prompt, setPrompt] = useState("");
  const fields = result?.fields;

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!prompt.trim() || status === "loading") return;
    dispatch(intakeStarted());
    try {
      const response = await fetch("/api/complaints/intake", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: prompt }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Unable to process the complaint.");
      dispatch(intakeSucceeded(body));
    } catch (caught) {
      dispatch(intakeFailed(caught instanceof Error ? caught.message : "Unable to process the complaint."));
    }
  }

  return <main className="app-shell">
    <section className="panel complaint-panel">
      <header><div><h1>Log Customer Complaint</h1><p>API & FDF Quality Assurance Module</p></div></header>
      {groups.map((group) => <fieldset key={group.title}><legend>{group.title}</legend><div className="field-grid">
        {group.fields.map(([key, label]) => <label className={key === "detailed_complaint_description" ? "wide" : ""} key={key}><span>{label}</span>
          {key === "detailed_complaint_description" ? <textarea readOnly value={fields?.[key] || "Awaiting AI extraction..."} /> : <input readOnly value={fields?.[key] || "Awaiting AI extraction..."} />}
        </label>)}
      </div></fieldset>)}
      <fieldset><legend>4. Initial Assessment & Priority</legend><div className="field-grid"><label><span>Initial Severity</span><input readOnly value={result?.risk_assessment.severity_suggested || "Awaiting AI extraction..."} /></label><label><span>Priority</span><input readOnly value={result?.risk_assessment.priority || "Awaiting AI extraction..."} /></label></div></fieldset>
      <div className="form-actions"><button className="secondary" onClick={() => dispatch(resetComplaint())}>Reset Form</button><button disabled>Save Complaint</button></div>
    </section>
    <section className="right-column">
      <section className="panel assistant-panel"><header><div><h2>✦ Aivoa AI Complaint Intake Assistant</h2><p>Describe a complaint and the form will populate automatically.</p></div><span className="beta">BETA</span></header>
        <form onSubmit={submit}><textarea aria-label="Complaint prompt" value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="Paste complaint text or email here..." /><button type="submit" disabled={!prompt.trim() || status === "loading"}>{status === "loading" ? "Analyzing complaint..." : "Log complaint with AI"}</button></form>
        {status === "loading" && <div className="progress"><i /></div>}{error && <p className="error">{error}</p>}{result?.missing_fields.length ? <p className="notice">AI could not find: {result.missing_fields.join(", ")}</p> : null}
      </section>
      <section className="panel risk-panel"><h2>⌾ AI Copilot Risk Assessment</h2><div className="risk-grid"><label><span>Severity (Suggested)</span><output>{result?.risk_assessment.severity_suggested || "Awaiting AI assessment..."}</output></label><label><span>Suggested Next Action</span><output>{result?.risk_assessment.suggested_next_action || "Awaiting AI assessment..."}</output></label></div><label><span>Initial Risk Assessment</span><output>{result?.risk_assessment.initial_risk_assessment || "Awaiting AI assessment..."}</output></label></section>
    </section>
  </main>;
}
