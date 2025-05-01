import RAKeyboardButton from "./RAKeyboardButton";
import { RAKeyboardItem } from "./RAKeyboardItems";

interface RAKeyboardGroupProps {
  operators: RAKeyboardItem[];
  onInsert: (expr: string) => void;
  className?: string;
}

const RAKeyboardGroup = ({
  operators,
  onInsert,
  className,
}: RAKeyboardGroupProps) => (
  <div className={`flex gap-2 flex-wrap mb-2 ${className ?? ""}`}>
    {operators.map((op) => (
      <RAKeyboardButton
        key={op.label}
        operator={op}
        onInsert={() => onInsert(op.expr)}
      />
    ))}
  </div>
);

export default RAKeyboardGroup;
