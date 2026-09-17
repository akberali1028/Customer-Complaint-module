export type ComplaintFields = {
  complaint_source: string | null; customer_name: string | null; product_name: string | null;
  product_strength_grade: string | null; batch_lot_number: string | null; manufacturing_date: string | null;
  expiry_date: string | null; quantity_affected: string | null; complaint_type: string | null;
  complaint_date: string | null; detailed_complaint_description: string | null;
};

export type RiskAssessment = {
  severity_suggested: "Minor" | "Major" | "Critical";
  priority: "Low" | "Medium" | "High" | "Urgent";
  suggested_next_action: string; initial_risk_assessment: string;
};

export type IntakeResponse = {
  input_type: "text" | "email"; fields: ComplaintFields; risk_assessment: RiskAssessment;
  used_fallback_model: boolean; missing_fields: string[];
};
