import RAKeyboardGroup from "./RAKeyboardGroup";
import {
  unaryOperators,
  binaryOperators,
  joinOperators,
  extendedOperators,
  logicalOperators,
  comparisons,
  literals,
} from "./RAKeyboardItems";

interface RAKeyboardProps {
  onInsert: (expr: string) => void;
  className?: string;
  disabled?: boolean;
}

export default function RAKeyboard({
  onInsert,
  className,
  disabled,
}: RAKeyboardProps) {
  const groups = [
    { title: "Unary Operators", operators: [unaryOperators] },
    { title: "Binary Operators", operators: [binaryOperators] },
    { title: "Join Operators", operators: [joinOperators] },
    { title: "Second-order Operators", operators: [extendedOperators] },
    {
      title: "Expressions",
      operators: [logicalOperators, comparisons, literals],
    },
  ];

  return (
    <div className={className}>
      {groups.map(({ title, operators }, i) => (
        <div key={i}>
          {title && (
            <h4 className="text-xs text-muted-foreground mb-2">{title}</h4>
          )}
          {operators.map((operatorGroup, j) => (
            <RAKeyboardGroup
              key={j}
              className="mb-2"
              disabled={disabled}
              operators={operatorGroup}
              onInsert={onInsert}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
