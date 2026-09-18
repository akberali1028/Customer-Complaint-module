import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { ChatResponse, IntakeResponse } from "./types";

type ComplaintState = { result: IntakeResponse | null; status: "idle" | "loading" | "success" | "error"; error: string | null };
const initialState: ComplaintState = { result: null, status: "idle", error: null };
const complaintSlice = createSlice({
  name: "complaint", initialState,
  reducers: {
    intakeStarted: (state) => { state.status = "loading"; state.error = null; },
    intakeSucceeded: (state, action: PayloadAction<IntakeResponse>) => { state.status = "success"; state.result = action.payload; },
    intakeFailed: (state, action: PayloadAction<string>) => { state.status = "error"; state.error = action.payload; },
    resetComplaint: () => initialState,
    chatApplied: (state, action: PayloadAction<ChatResponse>) => {
      if (!state.result) return;
      for (const update of action.payload.updates) state.result.fields[update.field_name] = update.value;
      if (action.payload.risk_assessment) state.result.risk_assessment = action.payload.risk_assessment;
    },
  },
});
export const { intakeStarted, intakeSucceeded, intakeFailed, resetComplaint, chatApplied } = complaintSlice.actions;
export const store = configureStore({ reducer: { complaint: complaintSlice.reducer } });
export type RootState = ReturnType<typeof store.getState>;
