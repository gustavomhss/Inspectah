import React from "react";
import { Timeline } from "./components/Timeline";
import { FeedbackButton } from "./components/FeedbackButton";

/**
 * Placeholder case page for Explorer v0. Timeline rendering is stubbed until
 * Wave 3 wires the real data sources.
 */
export function CasePage(): JSX.Element {
  return (
    <section className="s12-case-page">
      <header>
        <h2>Caso piloto</h2>
        <p>Esta página será alimentada com dados reais após Wave 3.</p>
      </header>
      <Timeline events={[]} />
      <FeedbackButton targetId="case-placeholder" variant="case" />
    </section>
  );
}
