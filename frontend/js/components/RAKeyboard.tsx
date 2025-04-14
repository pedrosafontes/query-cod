import RAOperatorButton, { RAOperator } from "./RAOperatorButton";

type RAKeyboardProps = {
  onInsert: (expr: string) => void;
  className?: string;
};

export default function RAKeyboard({ onInsert, className }: RAKeyboardProps) {
  const operators: RAOperator[] = [
    {
      label: "\\pi",
      expr: "\\pi_{\\placeholder{attr}}#0",
      displayExpr: "\\pi_{\\text{attrs}}(R)",
      name: "Projection",
      description: "Extracts specific columns from a relation.",
      args: [
        { name: "\\text{attrs}", description: "attributes to project" },
        { name: "R", description: "input relation" },
      ],
      example: "\\pi_{name, age}(Person)",
    },
    {
      label: "\\sigma",
      expr: "\\sigma_{\\placeholder{condition}}#0",
      displayExpr: "\\sigma_{\\theta}(R)",
      name: "Selection",
      description: "Selects tuples from a relation that satisfy a condition.",
      args: [
        { name: "\\theta", description: "predicate to filter rows" },
        { name: "R", description: "input relation" },
      ],
      example: "\\sigma_{age > 30}(Employee)",
    },
    {
      label: "\\cup",
      expr: "#@\\cup\\placeholder{rrel}",
      displayExpr: "R \\cup S",
      name: "Union",
      description: "Combines tuples from two union-compatible relations.",
      args: [
        { name: "R", description: "left-hand relation" },
        { name: "S", description: "right-hand relation" },
      ],
    },
    {
      label: "-",
      expr: "#@-\\placeholder{rrel}",
      displayExpr: "R - S",
      name: "Difference",
      description:
        "Returns tuples in the left relation that are not in the right.",
      args: [
        { name: "R", description: "left-hand relation" },
        { name: "S", description: "right-hand relation" },
      ],
    },
    {
      label: "\\cap",
      expr: "#@\\cap\\placeholder{rrel}",
      displayExpr: "R \\cap S",
      name: "Intersection",
      description: "Returns tuples present in both relations.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
    {
      label: "\\times",
      expr: "#@\\times\\placeholder{rrel}",
      displayExpr: "R \\times S",
      name: "Cartesian Product",
      description: "Forms all combinations of tuples from two relations.",
      args: [
        { name: "R", description: "left-hand relation" },
        { name: "S", description: "right-hand relation" },
      ],
    },
    {
      label: "\\Join",
      expr: "#@\\Join\\placeholder{rrel}",
      displayExpr: "R \\Join S",
      name: "Natural Join",
      description: "Joins two relations on common attribute names.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
    {
      label: "\\ltimes",
      expr: "#@\\ltimes\\placeholder{rrel}",
      displayExpr: "R \\ltimes S",
      name: "Left Semi Join",
      description:
        "Returns rows from the left relation with matches in the right.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
    {
      label: "\\overset\\theta\\bowtie",
      expr: "#@\\overset{\\placeholder{cond}}{\\bowtie}\\placeholder{rrel}",
      displayExpr: "R \\overset{\\theta}{\\bowtie} S",
      name: "Theta Join",
      description: "Joins two relations based on an arbitrary condition.",
      args: [
        { name: "\\theta", description: "join condition" },
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
      example: "R \\overset{id = deptId}{\\bowtie} S",
    },
    {
      label: "\\div",
      expr: "#@\\div\\placeholder{rrel}",
      displayExpr: "R \\div S",
      name: "Division",
      description:
        "Finds tuples in the left relation associated with all tuples in the right.",
      args: [
        { name: "R", description: "dividend relation" },
        { name: "S", description: "divisor relation" },
      ],
    },
    {
      label: "\\Gamma",
      expr: "\\Gamma_{(\\placeholder{grp_attrs}), ((\\placeholder{in}, \\placeholder{fn}, \\placeholder{out}))}#0",
      displayExpr: "\\Gamma_{(group), ((in, fn, out))}(R)",
      name: "Aggregation",
      description: "Performs aggregation on grouped attributes.",
      args: [
        { name: "group", description: "attributes to group by" },
        {
          name: "(in, fn, out)",
          description: "input attr, function, output attr",
        },
        { name: "R", description: "input relation" },
      ],
      example: "\\Gamma_{(dept), ((salary, avg, avg_salary))}(Employee)",
    },
    {
      label: "T",
      expr: "T_{(\\placeholder{n}, \\placeholder{attr})}#0",
      displayExpr: "T_{(n, attr)}(R)",
      name: "Top-N",
      description: "Returns the top-N tuples ordered by a given attribute.",
      args: [
        { name: "n", description: "number of tuples to return" },
        { name: "attr", description: "attribute to sort by" },
        { name: "R", description: "input relation" },
      ],
      example: "T_{(3, salary)}(Employee)",
    },
  ];

  return (
    <div className={`flex gap-2 flex-wrap ${className}`}>
      {operators.map((op) => (
        <RAOperatorButton
          key={op.label}
          operator={op}
          onInsert={() => onInsert(op.expr)}
        />
      ))}
    </div>
  );
}
