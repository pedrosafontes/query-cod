import { cn } from "lib/utils";

import RAKeyboardButton from "./RAKeyboardButton";
import { RAKeyboardItem } from "./RAKeyboardItems";

interface RAKeyboardGroupProps {
  operators: RAKeyboardItem[];
  onInsert: (expr: string) => void;
  className?: string;
  disabled?: boolean;
}

const RAKeyboardGroup = ({
  operators,
  onInsert,
  className,
  disabled,
}: RAKeyboardGroupProps) => (
  <div className={cn("flex gap-2 flex-wrap mb-2", className)}>
    {operators.map((op) => (
      <RAKeyboardButton
        key={op.label}
        disabled={disabled}
        operator={op}
        onInsert={() => onInsert(op.expr)}
      />
    ))}
  </div>
);

export default RAKeyboardGroup;
