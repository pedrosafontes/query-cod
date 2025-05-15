import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { QueriesService } from "api";

import SQLDiagramNode, { SQLNodeData } from "./SQLNode";

jest.mock("@xyflow/react", () => {
  const original = jest.requireActual("@xyflow/react");
  return {
    ...original,
    Handle: () => <span />,
  };
});

// Mock dependencies
jest.mock("api");
const mockToast = jest.fn();
jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => mockToast,
}));

describe("SQLNode Component", () => {
  const mockSetQueryResult = jest.fn();
  const queryId = 1;
  const subqueryId = 2;

  const renderNode = (data: SQLNodeData) => {
    render(
      <SQLDiagramNode
        data={data}
        deletable={false}
        draggable={false}
        dragging={false}
        id="node-id"
        isConnectable={false}
        positionAbsoluteX={0}
        positionAbsoluteY={0}
        selectable={false}
        selected={false}
        type="sql"
        zIndex={0}
      />,
    );
  };

  test("calls query service and updates result on click", async () => {
    const mockResponse = { results: { rows: [{ name: "John" }] } };

    (
      QueriesService.queriesSubqueriesExecutionsCreate as jest.Mock
    ).mockResolvedValue(mockResponse);

    renderNode({
      queryId,
      id: subqueryId,
      sql_node_type: "Select",
      columns: ["name"],
      errors: [],
      setQueryResult: mockSetQueryResult,
    } as SQLNodeData);

    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => {
      expect(
        QueriesService.queriesSubqueriesExecutionsCreate,
      ).toHaveBeenCalledWith({
        id: queryId,
        subqueryId,
      });
      expect(mockSetQueryResult).toHaveBeenCalledWith(mockResponse.results);
    });
  });

  test("shows error toast on failure", async () => {
    (
      QueriesService.queriesSubqueriesExecutionsCreate as jest.Mock
    ).mockRejectedValue(new Error("fail"));

    renderNode({
      queryId,
      id: subqueryId,
      sql_node_type: "Select",
      columns: ["name"],
      errors: [],
      setQueryResult: mockSetQueryResult,
    } as SQLNodeData);

    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error executing subquery",
      });
    });
  });
});
