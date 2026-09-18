import { type FormEvent, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { chatApplied, intakeFailed, intakeStarted, intakeSucceeded, resetComplaint, type RootState } from "./store";
import type { ComplaintFields } from "./types";

const groups: Array<{ title: string; fields: Array<[keyof ComplaintFields, string]> }> = [
  { title: "1. Origin & Customer Details", fields: [["complaint_source", "Complaint Source"], ["customer_name", "Customer Name"]] },
  { title: "2. Product & Batch Identification", fields: [["product_name", "Product Name"], ["product_strength_grade", "Product Strength/Grade"], ["batch_lot_number", "Batch/Lot Number"], ["manufacturing_date", "Manufacturing Date"], ["expiry_date", "Expiry Date"], ["quantity_affected", "Quantity Affected"]] },
  { title: "3. Complaint Details", fields: [["complaint_type", "Complaint Type"], ["complaint_date", "Complaint Date"], ["detailed_complaint_description", "Detailed Complaint Description"]] },
];

type Message = { id: number; sender: "assistant" | "user"; text?: string; fileName?: string; pending?: boolean; error?: boolean };

export function App() {
  const dispatch = useDispatch();
  const { result, status } = useSelector((state: RootState) => state.complaint);
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [messages, setMessages] = useState<Message[]>([{ id: 0, sender: "assistant", text: "Hi, I’m Aivoa AI. Paste a complaint or attach a document and I’ll populate the form and provide an initial risk assessment." }]);
  const [saveMessage, setSaveMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fields = result?.fields;
  const isSending = status === "loading";

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isSending]);

  function append(messageToAdd: Omit<Message, "id">) {
    setMessages((current) => [...current, { ...messageToAdd, id: Date.now() + current.length }]);
  }

  async function send(event: FormEvent) {
    event.preventDefault();
    if (isSending || (!message.trim() && !selectedFile)) return;
    const outgoingText = message.trim();
    const file = selectedFile;
    setMessage(""); setSelectedFile(null); setSaveMessage("");
    append({ sender: "user", text: outgoingText || undefined, fileName: file?.name });

    if (file) {
      dispatch(intakeStarted());
      try {
        const data = new FormData(); data.append("file", file);
        const response = await fetch("/api/complaints/intake-file", { method: "POST", body: data });
        const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Unable to process file.");
        dispatch(intakeSucceeded(body));
        append({ sender: "assistant", text: `Document analysis complete. I populated the complaint form from ${file.name}. You can ask me to change any field.` });
      } catch (caught) {
        const error = caught instanceof Error ? caught.message : "Unable to process file.";
        dispatch(intakeFailed(error)); append({ sender: "assistant", text: error, error: true });
      }
      return;
    }

    if (!result) {
      dispatch(intakeStarted());
      try {
        const response = await fetch("/api/complaints/intake", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: outgoingText }) });
        const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Unable to process the complaint.");
        dispatch(intakeSucceeded(body));
        append({ sender: "assistant", text: `Complaint logged and form populated. Suggested severity is ${body.risk_assessment.severity_suggested}. Ask a question or tell me what to change.` });
      } catch (caught) {
        const error = caught instanceof Error ? caught.message : "Unable to process the complaint.";
        dispatch(intakeFailed(error)); append({ sender: "assistant", text: error, error: true });
      }
      return;
    }

    try {
      const response = await fetch("/api/complaints/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: outgoingText, fields: result.fields, risk_assessment: result.risk_assessment }) });
      const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Assistant request failed.");
      dispatch(chatApplied(body)); append({ sender: "assistant", text: body.answer });
    } catch (caught) { append({ sender: "assistant", text: caught instanceof Error ? caught.message : "Assistant request failed.", error: true }); }
  }

  async function saveComplaint() {
    if (!result) return;
    try {
      const response = await fetch("/api/complaints", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ fields: result.fields, risk_assessment: result.risk_assessment }) });
      const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Save failed."); setSaveMessage(body.message);
    } catch (caught) { setSaveMessage(caught instanceof Error ? caught.message : "Save failed."); }
  }

  return <main className="app-shell">
    <section className="panel complaint-panel">
      <header><div><h1>Log Customer Complaint</h1><p>API & FDF Quality Assurance Module</p></div></header>
      {groups.map((group) => <fieldset key={group.title}><legend>{group.title}</legend><div className="field-grid">
        {group.fields.map(([key, label]) => <label className={key === "detailed_complaint_description" ? "wide" : ""} key={key}><span>{label}</span>{key === "detailed_complaint_description" ? <textarea readOnly value={fields?.[key] || "Awaiting AI extraction..."} /> : <input readOnly value={fields?.[key] || "Awaiting AI extraction..."} />}</label>)}
      </div></fieldset>)}
      <fieldset><legend>4. Initial Assessment & Priority</legend><div className="field-grid"><label><span>Initial Severity</span><input readOnly value={result?.risk_assessment.severity_suggested || "Awaiting AI extraction..."} /></label><label><span>Priority</span><input readOnly value={result?.risk_assessment.priority || "Awaiting AI extraction..."} /></label></div></fieldset>
      <section className="risk-panel inline-risk"><header><div><h2>✦ Aivoa AI Risk Check</h2><p>An initial AI suggestion for review by your QA team.</p></div></header><div className="risk-grid"><label><span>Suggested Severity</span><output>{result?.risk_assessment.severity_suggested || "Awaiting AI assessment..."}</output></label><label><span>Suggested Next Action</span><output>{result?.risk_assessment.suggested_next_action || "Awaiting AI assessment..."}</output></label></div><label><span>Initial Risk Assessment</span><output>{result?.risk_assessment.initial_risk_assessment || "Awaiting AI assessment..."}</output></label></section>
      <div className="form-actions"><button className="secondary" onClick={() => { dispatch(resetComplaint()); setMessages([{ id: Date.now(), sender: "assistant", text: "Form reset. Send a new complaint whenever you’re ready." }]); setSaveMessage(""); }}>Reset Form</button><button disabled={!result} onClick={saveComplaint}>Save Complaint</button></div>{saveMessage && <p className="notice">{saveMessage}</p>}
    </section>
    <section className="right-column">
      <section className="panel assistant-panel chat-shell"><header><div><h2>✦ Aivoa AI Complaint Intake Assistant</h2><p>Send a complaint, document, question, or field change.</p></div><span className="beta">BETA</span></header>
        <div className="messages" aria-live="polite">{messages.map((item) => <div className={`message ${item.sender}${item.error ? " message-error" : ""}`} key={item.id}>{item.fileName && <div className="file-bubble"><span>📄</span><div><strong>{item.fileName}</strong><small>Complaint document</small></div></div>}{item.text && <span>{item.text}</span>}</div>)}{isSending && <div className="message assistant loading"><i /><i /><i /></div>}<div ref={chatEndRef} /></div>
        <form className="composer" onSubmit={send}>{selectedFile && <div className="attachment-chip"><span>📎</span><span>{selectedFile.name}</span><button type="button" aria-label="Remove attachment" onClick={() => setSelectedFile(null)}>×</button></div>}<div className="composer-row"><button className="attach-button" type="button" aria-label="Attach complaint document" onClick={() => fileInputRef.current?.click()} disabled={isSending}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8.7 12.9 6.8-6.8a3.5 3.5 0 1 1 5 5l-9.2 9.2a5.5 5.5 0 0 1-7.8-7.8l8.5-8.5" /></svg></button><input ref={fileInputRef} className="hidden-file-input" type="file" accept=".pdf,.docx,.txt,.eml" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} /><input value={message} onChange={(event) => setMessage(event.target.value)} disabled={isSending} placeholder={result ? "Ask Aivoa to change or clarify something..." : "Type a complaint or paste an email..."} /><button className="send-button" type="submit" disabled={isSending || (!message.trim() && !selectedFile)}>➤</button></div></form>
      </section>
    </section>
  </main>;
}
