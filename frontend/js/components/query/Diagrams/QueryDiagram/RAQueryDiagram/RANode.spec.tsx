import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { QueryContext } from "contexts/QueryContext";

import RADiagramNode, { RANodeData } from "./RANode";

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

describe("RANode Component", () => {
  const mockSetQueryResult = jest.fn();
  const mockExecuteSubquery = jest.fn();

  const queryId = 1;
  const subqueryId = 2;

  const renderNode = (data: RANodeData) => {
    render(
      <QueryContext.Provider
        value={{
          setQueryResult: mockSetQueryResult,
          fetchTree: jest.fn(),
          executeSubquery: mockExecuteSubquery,
        }}
      >
        <RADiagramNode
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
          type="ra"
          zIndex={0}
        />
      </QueryContext.Provider>,
    );
  };

  test("calls query service and updates result on click", async () => {
    const mockResponse = { results: { rows: [{ name: "John" }] } };

    mockExecuteSubquery.mockResolvedValue(mockResponse);

    renderNode({
      queryId,
      id: subqueryId,
      ra_node_type: "Projection",
      attributes: ["name"],
      errors: [],
      setQueryResult: mockSetQueryResult,
    } as RANodeData);

    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => {
      expect(mockExecuteSubquery).toHaveBeenCalledWith({
        id: queryId,
        subqueryId,
      });
      expect(mockSetQueryResult).toHaveBeenCalledWith(mockResponse.results);
    });
  });

  test("shows error toast on failure", async () => {
    mockExecuteSubquery.mockRejectedValue(new Error("fail"));

    renderNode({
      queryId,
      id: subqueryId,
      ra_node_type: "Projection",
      attributes: ["name"],
      errors: [],
      setQueryResult: mockSetQueryResult,
    } as RANodeData);

    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error executing subquery",
      });
    });
  });
});
