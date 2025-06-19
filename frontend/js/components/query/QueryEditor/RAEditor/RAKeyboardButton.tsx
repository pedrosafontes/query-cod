import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

import LatexFormula from "./LatexFormula";
import { RAKeyboardItem } from "./RAKeyboardItems";

type RAKeyboardButtonProps = {
  operator: RAKeyboardItem;
  onInsert: () => void;
  disabled?: boolean;
};

const RAKeyboardButton = ({
  operator,
  onInsert,
  disabled,
}: RAKeyboardButtonProps) => {
  const renderButton = () => {
    return (
      <Button
        className="px-2"
        disabled={disabled}
        size="sm"
        variant="outline"
        onClick={onInsert}
      >
        <LatexFormula expression={operator.label} />
      </Button>
    );
  };

  if (!operator.details) {
    return renderButton();
  }

  const { displayExpr, name, args, description, example } = operator.details;

  return (
    <HoverCard openDelay={800}>
      <HoverCardTrigger asChild>{renderButton()}</HoverCardTrigger>
      <HoverCardContent className="w-auto min-w-64 max-w-80" side="bottom">
        <div className="text-xs">
          <h3 className="text-sm font-medium">{name}</h3>
          <p className="mt-1 text-muted-foreground">{description}</p>
          <LatexFormula
            className="my-2 bg-muted px-2 py-1 rounded-sm text-center"
            expression={displayExpr}
          />
          <ul className="pl-4 list-disc">
            {args.map((arg, i) => (
              <li key={i}>
                <LatexFormula className="inline" expression={arg.name} />
                <span className="text-muted-foreground">
                  {" "}
                  - {arg.description}
                </span>
              </li>
            ))}
          </ul>
          {example && (
            <div className="mt-2">
              <span className="text-muted-foreground">Example:</span>
              <LatexFormula
                className="mt-1 bg-muted px-2 py-1 rounded-sm text-center"
                expression={example}
              />
            </div>
          )}
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};

export default RAKeyboardButton;
