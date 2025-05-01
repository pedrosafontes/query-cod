import RAKeyboardGroup from "./RAKeyboardGroup";
import {
  basicOperators,
  setOperators,
  joinOperators,
  extendedOperators,
  references,
  logicalOperators,
  comparisons,
  literals,
} from "./RAKeyboardItems";

interface RAKeyboardProps {
  onInsert: (expr: string) => void;
  className?: string;
}

export default function RAKeyboard({ onInsert, className }: RAKeyboardProps) {
  const groups = [
    { title: "Basic Operators", operators: [basicOperators] },
    { title: "Set Operators", operators: [setOperators] },
    { title: "Join Operators", operators: [joinOperators] },
    { title: "Extended Operators", operators: [extendedOperators] },
    {
      title: "Expressions",
      operators: [references, logicalOperators, comparisons, literals],
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
              operators={operatorGroup}
              onInsert={onInsert}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
