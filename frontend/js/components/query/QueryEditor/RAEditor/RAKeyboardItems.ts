export type RAKeyboardItem = {
  label: string; // LaTeX symbol to show in button
  expr: string; // Expression to insert into MathLive
  details?: {
    displayExpr: string; // LaTeX expression to show in hover card
    name: string; // Human-friendly name
    args: { name: string; description: string }[]; // List of arguments
    description: string; // Short explanation
    example?: string; // LaTeX string showing example usage
  };
};

export const logicalOperators: RAKeyboardItem[] = [
  {
    label: "\\land",
    expr: "#@ \\land \\placeholder{right}",
    details: {
      displayExpr: "\\theta_1 \\land \\theta_2",
      name: "AND",
      description: "Logical AND operator.",
      args: [
        { name: "\\theta_1", description: "first condition" },
        { name: "\\theta_2", description: "second condition" },
      ],
    },
  },
  {
    label: "\\lor",
    expr: "#@ \\lor \\placeholder{right}",
    details: {
      displayExpr: "\\theta_1 \\lor \\theta_2",
      name: "OR",
      description: "Logical OR operator.",
      args: [
        { name: "\\theta_1", description: "first condition" },
        { name: "\\theta_2", description: "second condition" },
      ],
    },
  },
  {
    label: "\\lnot",
    expr: "\\lnot #0",
    details: {
      displayExpr: "\\lnot \\theta",
      name: "NOT",
      description: "Logical NOT operator.",
      args: [{ name: "\\theta", description: "condition to negate" }],
    },
  },
];

export const comparisons: RAKeyboardItem[] = [
  {
    label: "=",
    expr: "#@ = \\placeholder{right}",
  },
  {
    label: "\\neq",
    expr: "#@ \\neq \\placeholder{right}",
  },
  {
    label: "<",
    expr: "#@ < \\placeholder{right}",
  },
  {
    label: ">",
    expr: "#@ > \\placeholder{right}",
  },
  {
    label: "\\leq",
    expr: "#@ \\leq \\placeholder{right}",
  },
  {
    label: "\\geq",
    expr: "#@ \\geq \\placeholder{right}",
  },
];

export const literals: RAKeyboardItem[] = [
  {
    label: "\\text{\\footnotesize 'string'}",
    expr: "\\text{''}",
  },
];

export const unaryOperators: RAKeyboardItem[] = [
  {
    label: "\\pi",
    expr: "\\pi_{\\placeholder{attr}}(#0)",
    details: {
      displayExpr: "\\pi_{\\text{attrs}}(R)",
      name: "Projection",
      description: "Extracts specific columns from a relation.",
      args: [
        { name: "\\text{attrs}", description: "attributes to project" },
        { name: "R", description: "input relation" },
      ],
      example: "\\pi_{name, age}(Person)",
    },
  },
  {
    label: "\\sigma",
    expr: "\\sigma_{\\placeholder{condition}}(#0)",
    details: {
      displayExpr: "\\sigma_{\\theta}(R)",
      name: "Selection",
      description: "Selects tuples from a relation that satisfy a condition.",
      args: [
        { name: "\\theta", description: "predicate to filter rows" },
        { name: "R", description: "input relation" },
      ],
      example: "\\sigma_{age > 30}(Employee)",
    },
  },
  {
    label: "\\rho",
    expr: "\\rho_{\\placeholder{alias}}(#0)",
    details: {
      displayExpr: "\\rho_{\\text{alias}}(R)",
      name: "Rename",
      description: "Renames a relation.",
      args: [
        { name: "\\text{alias}", description: "new name for the relation" },
        { name: "R", description: "input relation" },
      ],
    },
  },
];

export const binaryOperators: RAKeyboardItem[] = [
  {
    label: "\\cup",
    expr: "(#@)\\cup(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\cup S",
      name: "Union",
      description: "Combines tuples from two union-compatible relations.",
      args: [
        { name: "R", description: "left-hand relation" },
        { name: "S", description: "right-hand relation" },
      ],
    },
  },
  {
    label: "-",
    expr: "(#@)-(\\placeholder{rrel})",
    details: {
      displayExpr: "R - S",
      name: "Difference",
      description:
        "Returns tuples in the left relation that are not in the right.",
      args: [
        { name: "R", description: "left-hand relation" },
        { name: "S", description: "right-hand relation" },
      ],
    },
  },
  {
    label: "\\cap",
    expr: "(#@)\\cap(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\cap S",
      name: "Intersection",
      description: "Returns tuples present in both relations.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
  },
  {
    label: "\\div",
    expr: "(#@)\\div(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\div S",
      name: "Division",
      description:
        "Finds tuples in the left relation associated with all tuples in the right.",
      args: [
        { name: "R", description: "dividend relation" },
        { name: "S", description: "divisor relation" },
      ],
    },
  },
];

export const joinOperators: RAKeyboardItem[] = [
  {
    label: "\\times",
    expr: "(#@)\\times(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\times S",
      name: "Cartesian Product",
      description: "Forms all combinations of tuples from two relations.",
      args: [
        { name: "R", description: "left-hand relation" },
        { name: "S", description: "right-hand relation" },
      ],
    },
  },
  {
    label: "\\Join",
    expr: "(#@)\\Join(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\Join S",
      name: "Natural Join",
      description: "Joins two relations on common attribute names.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
  },
  {
    label: "\\ltimes",
    expr: "(#@)\\ltimes(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\ltimes S",
      name: "Left Semi Join",
      description:
        "Returns rows from the left relation with matches in the right.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
  },
  {
    label: "\\overset\\theta\\bowtie",
    expr: "(#@)\\overset{\\placeholder{cond}}{\\bowtie}(\\placeholder{rrel})",
    details: {
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
  },
  {
    label: "\\overline{\\Join}",
    expr: "(#@)\\overline{\\Join}(\\placeholder{rrel})",
    details: {
      displayExpr: "R \\ \\overline{\\Join} \\ S",
      name: "Anti Join",
      description:
        "Returns rows from the left relation without matches in the right.",
      args: [
        { name: "R", description: "left relation" },
        { name: "S", description: "right relation" },
      ],
    },
  },
];

export const extendedOperators: RAKeyboardItem[] = [
  {
    label: "\\Gamma",
    expr: "\\Gamma_{(\\placeholder{grp_attrs}), ((\\placeholder{in}, \\placeholder{fn}, \\placeholder{out}))}(#0)",
    details: {
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
  },
  {
    label: "\\operatorname{T}",
    expr: "\\operatorname{T}_{(\\placeholder{n}, \\placeholder{attr})}(#0)",
    details: {
      displayExpr: "\\operatorname{T}_{(n, attr)}(R)",
      name: "Top-N",
      description: "Returns the top-N tuples ordered by a given attribute.",
      args: [
        { name: "n", description: "number of tuples to return" },
        { name: "attr", description: "attribute to sort by" },
        { name: "R", description: "input relation" },
      ],
      example: "\\operatorname{T}_{(3, salary)}(Employee)",
    },
  },
];
