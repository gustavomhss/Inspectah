import React from "react";

interface FeedbackButtonProps {
  targetId: string;
  variant: "case" | "event";
}

/**
 * Button placeholder for the "reportar problema" flow.
 */
export function FeedbackButton({ targetId, variant }: FeedbackButtonProps): JSX.Element {
  return (
    <button
      type="button"
      className="s12-feedback-button"
      onClick={() => alert(`Feedback placeholder para ${variant} ${targetId}`)}
    >
      Reportar problema
    </button>
  );
}
