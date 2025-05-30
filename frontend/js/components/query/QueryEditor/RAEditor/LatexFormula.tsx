import katex from "katex";
import { useEffect, useRef } from "react";
import "katex/dist/katex.min.css";

type LatexFormulaProps = {
  expression: string;
  className?: string;
};

function convertDisplayLinesToAligned(input: string): string {
  if (!input.startsWith("\\displaylines{")) return input;

  console.log(input)

  const content = input.slice(14, -1); // Extract content inside \displaylines{}

  const alignedContent = content
    .split('\\\\')
    .map(line => `& ${line}`)
    .join('\\\\');

  return `\\begin{align*}\n${alignedContent}\n\\end{align*}`;
}

function LatexFormula({ expression, className }: LatexFormulaProps) {
  const containerRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      const processed = convertDisplayLinesToAligned(expression);
      katex.render(processed, containerRef.current, {
        displayMode: true,
        throwOnError: false,
      });
    }
  }, [expression]);

  return <div ref={containerRef} className={className} />;
}

export default LatexFormula;