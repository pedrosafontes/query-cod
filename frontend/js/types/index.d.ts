import { MathfieldElement } from "mathlive";
import * as React from "react";

export {};

declare global {
  interface Window {
    SENTRY_DSN: string;
    COMMIT_SHA: string;

    Urls: unknown;
  }

  namespace JSX {
    interface IntrinsicElements {
      "math-field": React.DetailedHTMLProps<
        React.HTMLAttributes<MathfieldElement>,
        MathfieldElement
      >;
    }
  }
}
