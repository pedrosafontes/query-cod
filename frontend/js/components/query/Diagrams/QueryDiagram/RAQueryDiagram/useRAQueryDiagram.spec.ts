import { renderHook, waitFor } from "@testing-library/react";

import { QueriesService, Query, RATree } from "api";

import useRAQueryDiagram from "./useRAQueryDiagram";

jest.mock("api", () => ({
  QueriesService: {
    queriesTreeRetrieve: jest.fn(),
  },
}));

jest.mock("hooks/useLayout", () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe("useRAQueryDiagram", () => {
  const mockTree: RATree = {
    id: 1,
    ra_node_type: "Projection",
    attributes: ["name"],
    children: [
      {
        id: 2,
        ra_node_type: "Selection",
        condition: "id = 1",
        children: [
          {
            id: 3,
            ra_node_type: "Relation",
            name: "Users",
            children: [],
            validation_errors: [],
          },
        ],
        validation_errors: [],
      },
    ],
    validation_errors: [],
  };

  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    text: "SELECT * FROM users",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
  };

  beforeEach(() => {
    jest.clearAllMocks();

    (QueriesService.queriesTreeRetrieve as jest.Mock).mockResolvedValue({
      ra_tree: mockTree,
    });
  });

  test("should generate nodes and edges from simple tree", async () => {
    const setQueryResult = jest.fn();
    const { result } = renderHook(() =>
      useRAQueryDiagram({ query: mockQuery, setQueryResult }),
    );

    await waitFor(() => {
      // Should have 3 nodes (Project, Select, Users)
      expect(result.current.nodes).toHaveLength(3);

      // Should have 2 edges (Select -> Project, Users -> Select)
      expect(result.current.edges).toHaveLength(2);
    });
  });

  test("should handle undefined tree", () => {
    const { result } = renderHook(() =>
      useRAQueryDiagram({ query: undefined, setQueryResult: jest.fn() }),
    );

    // Should have no nodes or edges
    expect(result.current.nodes).toHaveLength(0);
    expect(result.current.edges).toHaveLength(0);
  });
});
