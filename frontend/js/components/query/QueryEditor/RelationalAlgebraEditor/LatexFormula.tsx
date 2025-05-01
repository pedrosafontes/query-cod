import katex from "katex";
import { useEffect, useRef } from "react";
import "katex/dist/katex.min.css";

type LatexFormulaProps = {
  expression: string;
  className?: string;
};

function LatexFormula({ expression, className }: LatexFormulaProps) {
  const containerRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    katex.render(expression, containerRef.current as HTMLInputElement);
  }, [expression]);

  return <div ref={containerRef} className={className} />;
}

export default LatexFormula;
