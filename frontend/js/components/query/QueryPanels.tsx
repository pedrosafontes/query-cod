import { ReactNode, useEffect, useRef, useState } from "react";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "../ui/resizable";

type QueryPanelsProps = {
  left: ReactNode;
  right: ReactNode;
  minLeftWidth?: number;
  collapsible?: boolean;
  withHandle?: boolean;
};

const QueryPanels = ({
  left,
  right,
  minLeftWidth = 400,
  collapsible = true,
  withHandle = true,
}: QueryPanelsProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number | null>(null);

  useEffect(() => {
    const container = containerRef.current;

    let observer: ResizeObserver | null = null;

    if (container) {
      observer = new ResizeObserver((entries) => {
        for (const entry of entries) {
          setContainerWidth(entry.contentRect.width);
        }
      });

      observer.observe(container);
    }

    return () => {
      if (observer) observer.disconnect();
    };
  }, []);

  const size =
    Math.min(1, containerWidth ? minLeftWidth / containerWidth : 1 / 3) * 100;

  const renderLeft = () => {
    if (left) {
      return (
        <ResizablePanel
          className="py-5"
          collapsedSize={0}
          collapsible={collapsible}
          defaultSize={size}
          minSize={size}
        >
          {left}
        </ResizablePanel>
      );
    }
    return <ResizablePanel maxSize={0} />;
  };

  return (
    <div ref={containerRef} className="w-full h-full">
      <ResizablePanelGroup direction="horizontal">
        {renderLeft()}
        {left && right && <ResizableHandle withHandle={withHandle} />}
        <ResizablePanel className="bg-secondary">{right}</ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default QueryPanels;
