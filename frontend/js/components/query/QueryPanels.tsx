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

  return (
    <div ref={containerRef} className="w-full h-full">
      <ResizablePanelGroup direction="horizontal">
        <ResizablePanel className="px-3 py-5" defaultSize={size} minSize={size}>
          {left}
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel>{right}</ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default QueryPanels;
