import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";

import Diagrams from ".";

const mockSetNodes = jest.fn();
const mockSetEdges = jest.fn();

jest.mock("@xyflow/react", () => {
  const original = jest.requireActual("@xyflow/react");
  return {
    ...original,
    useNodesState: () => [[], mockSetNodes, jest.fn()],
    useEdgesState: () => [[], mockSetEdges, jest.fn()],
  };
});

const mockSchemaNodes = [{ id: "schema" }];

jest.mock("components/database/useSchemaDiagram", () => () => ({
  nodes: mockSchemaNodes,
  edges: [],
}));

const mockQueryNodes = [{ id: "query" }];

jest.mock("./QueryDiagram/useQueryDiagram", () => () => ({
  nodes: mockQueryNodes,
  edges: [],
}));

jest.mock("hooks/useTopCenterView", () => ({
  useTopCenterFitView: jest.fn(),
}));

describe("Diagrams", () => {
  test("switches to query diagram when 'Query' tab is clicked", async () => {
    const user = userEvent.setup();
    render(<Diagrams databaseId={1} />);

    expect(mockSetNodes).toHaveBeenCalledWith(mockSchemaNodes);

    const tab = screen.getByRole("tab", { name: /query/i });
    await user.click(tab);

    expect(mockSetNodes).toHaveBeenCalledWith(mockQueryNodes);
  });

  test("renders children in the bottom panel", () => {
    render(
      <Diagrams databaseId={1}>
        <div data-testid="custom-child" />
      </Diagrams>,
    );
    expect(screen.getByTestId("custom-child")).toBeInTheDocument();
  });
});
