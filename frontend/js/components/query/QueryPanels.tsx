import { ReactNode, useEffect, useRef, useState } from "react";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "../ui/resizable";

const QueryPanels = ({
  left,
  right,
}: {
  left: ReactNode;
  right: ReactNode;
}) => {
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

  const MIN_SIZE_IN_PX = 400;
  const size =
    Math.min(1, containerWidth ? MIN_SIZE_IN_PX / containerWidth : 1 / 3) * 100;

  const renderLeft = () => {
    if (left) {
      return (
        <ResizablePanel
          collapsedSize={0}
          collapsible
          defaultSize={size}
          minSize={size}
        >
          <div className="py-5 h-full overflow-auto">{left}</div>
        </ResizablePanel>
      );
    }
    return <ResizablePanel maxSize={0} />;
  };

  return (
    <div ref={containerRef} className="w-full h-full">
      <ResizablePanelGroup direction="horizontal">
        {renderLeft()}
        {left && right && <ResizableHandle withHandle />}
        <ResizablePanel className="bg-secondary">{right}</ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default QueryPanels;
