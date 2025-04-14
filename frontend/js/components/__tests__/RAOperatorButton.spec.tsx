import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { userEvent } from "@testing-library/user-event";

import RAOperatorButton, { RAOperator } from "../RAOperatorButton";

jest.mock("../LatexFormula", () => {
  return jest.fn(({ expression }: { expression: string }) => (
    <span data-testid="latex">{expression}</span>
  ));
});

describe("RAOperatorButton", () => {
  const operator: RAOperator = {
    label: "\\pi",
    expr: "\\pi_{\\text{attr}}R",
    displayExpr: "\\pi_{\\text{attrs}}(R)",
    name: "Projection",
    description: "Selects specific attributes from a relation.",
    args: [
      { name: "\\text{attrs}", description: "attributes to project" },
      { name: "R", description: "input relation" },
    ],
    example: "\\pi_{name, age}(Person)",
  };

  const mockOnInsert = jest.fn();

  test("renders the operator label in the button", () => {
    render(<RAOperatorButton operator={operator} onInsert={mockOnInsert} />);
    expect(screen.getByText("\\pi")).toBeInTheDocument();
  });

  test("calls onInsert when the button is clicked", async () => {
    const user = userEvent.setup();

    render(<RAOperatorButton operator={operator} onInsert={mockOnInsert} />);

    const button = screen.getByRole("button");
    await user.click(button);

    expect(mockOnInsert).toHaveBeenCalledTimes(1);
  });

  test("displays the hover card content with name, description, args, and example", async () => {
    const user = userEvent.setup();

    render(<RAOperatorButton operator={operator} onInsert={mockOnInsert} />);

    const button = screen.getByRole("button");
    await user.hover(button);

    expect(await screen.findByText(operator.name)).toBeInTheDocument();

    expect(screen.getByText(operator.description)).toBeInTheDocument();
    expect(screen.getByText(operator.example!)).toBeInTheDocument();
  });
});
