import { Badge } from "@/components/ui/badge";
import { DifficultyEnum } from "api";
import { cn } from "lib/utils";

const DifficultyBadge = ({ difficulty }: { difficulty: DifficultyEnum }) => {
  let className: string;

  switch (difficulty) {
    case "easy":
      className = "bg-green-100 text-green-800";
      break;
    case "medium":
      className = "bg-yellow-100 text-yellow-800";
      break;
    case "hard":
      className = "bg-red-100 text-red-800";
      break;
    default:
      className = "bg-gray-100 text-gray-800";
  }

  return <Badge className={cn(className, "capitalize")}>{difficulty}</Badge>;
};

export default DifficultyBadge;
