import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

import LatexFormula from "./LatexFormula";

export type RAOperator = {
  label: string; // LaTeX symbol to show in button
  expr: string; // Expression to insert into MathLive
  displayExpr: string; // LaTeX expression to show in hover card
  name: string; // Human-friendly name
  args: { name: string; description: string }[]; // List of arguments
  description: string; // Short explanation
  example?: string; // LaTeX string showing example usage
};

type RAOperatorButtonProps = {
  operator: RAOperator;
  onInsert: () => void;
};

const RAOperatorButton = ({ operator, onInsert }: RAOperatorButtonProps) => {
  return (
    <HoverCard openDelay={800}>
      <HoverCardTrigger asChild>
        <Button className="px-2" size="sm" variant="outline" onClick={onInsert}>
          <LatexFormula expression={operator.label} />
        </Button>
      </HoverCardTrigger>
      <HoverCardContent side="top">
        <div className="text-xs">
          <h3 className="text-sm font-medium">{operator.name}</h3>
          <p className="mt-1 text-muted-foreground">{operator.description}</p>
          <LatexFormula
            className="my-2 bg-muted px-2 py-1 rounded-sm"
            expression={operator.displayExpr}
          />
          <ul className="pl-4 list-disc">
            {operator.args.map((arg, i) => (
              <li key={i}>
                <LatexFormula className="inline" expression={arg.name} />
                <span className="text-muted-foreground">
                  {" "}
                  - {arg.description}
                </span>
              </li>
            ))}
          </ul>
          {operator.example && (
            <div className="mt-2">
              <span className="text-muted-foreground">Example:</span>
              <LatexFormula
                className="mt-1 bg-muted px-2 py-1 rounded-sm"
                expression={operator.example}
              />
            </div>
          )}
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};

export default RAOperatorButton;
