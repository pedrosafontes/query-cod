import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import React from "react";

import "@testing-library/jest-dom";
import { QueriesService, Query } from "../../api";
import QueryEditor from "../QueryEditor";
import QueryExplorer from "../QueryExplorer";
import QueryResult from "../QueryResult";

jest.mock("../../api", () => ({
  QueriesService: {
    queriesExecutionsCreate: jest.fn(),
  },
}));

jest.mock("../QueryEditor", () => {
  return jest.fn(() => (
    <div data-testid="query-editor">Query Editor Component</div>
  ));
});

jest.mock("../QueryResult", () => {
  return jest.fn(() => (
    <div data-testid="query-result">Query Result Component</div>
  ));
});

describe("QueryExplorer Component", () => {
  const mockQuery: Query = {
    id: 1,
    text: "SELECT * FROM users",
    created: "2024-01-01T00:00:00Z",
    modified: "2024-01-02T00:00:00Z",
  };

  const mockExecutionResult = {
    success: true,
    results: {
      columns: ["id", "name", "email"],
      rows: [
        [1, "John Doe", "john@example.com"],
        [2, "Jane Smith", "jane@example.com"],
      ],
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (QueriesService.queriesExecutionsCreate as jest.Mock).mockResolvedValue(
      mockExecutionResult,
    );
  });

  test("renders the component with QueryEditor and QueryResult", async () => {
    await act(async () => {
      render(<QueryExplorer query={mockQuery} />);
    });

    // Check if component renders correctly
    expect(screen.getByText("Execute")).toBeInTheDocument();
    expect(screen.getByTestId("query-editor")).toBeInTheDocument();
    expect(screen.getByTestId("query-result")).toBeInTheDocument();

    // Verify QueryEditor was called with the right props
    expect(QueryEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockQuery,
      }),
      expect.anything(),
    );

    // Verify QueryResult was called with initial state
    expect(QueryResult).toHaveBeenCalledWith(
      expect.objectContaining({
        result: undefined,
        success: true,
      }),
      expect.anything(),
    );
  });

  test("executes query when Execute button is clicked", async () => {
    await act(async () => {
      render(<QueryExplorer query={mockQuery} />);
    });

    fireEvent.click(screen.getByText("Execute"));

    // Check if queriesExecutionsCreate was called with correct parameters
    expect(QueriesService.queriesExecutionsCreate).toHaveBeenCalledWith({
      id: mockQuery.id,
    });

    // Verify that QueryResult was called with updated props after execution
    await waitFor(() => {
      expect(QueryResult).toHaveBeenCalledWith(
        expect.objectContaining({
          result: mockExecutionResult.results,
          success: mockExecutionResult.success,
        }),
        expect.anything(),
      );
    });
  });
});
