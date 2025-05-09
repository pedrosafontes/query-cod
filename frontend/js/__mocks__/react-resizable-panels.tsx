import { ReactNode } from "react";

export const PanelGroup = ({ children }: { children: ReactNode }) => (
  <div data-testid="mock-panel-group">{children}</div>
);

export const Panel = ({ children }: { children: ReactNode }) => (
  <div data-testid="mock-panel">{children}</div>
);

export const PanelResizeHandle = () => (
  <div data-testid="mock-panel-resize-handle" />
);
