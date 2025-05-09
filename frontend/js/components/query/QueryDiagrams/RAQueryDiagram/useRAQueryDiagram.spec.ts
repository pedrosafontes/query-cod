import { renderHook } from "@testing-library/react";

import { RATree } from "api";

import useRAQueryDiagram from "./useRAQueryDiagram";

jest.mock("hooks/useLayout", () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe("useRAQueryDiagram", () => {
  const mockTree: RATree = {
    id: 1,
    label: "Project",
    sub_trees: [
      {
        id: 2,
        label: "Select",
        sub_trees: [
          {
            id: 3,
            label: "Users",
            sub_trees: [],
          },
        ],
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("should generate nodes and edges from simple tree", () => {
    const { result } = renderHook(() => useRAQueryDiagram({ tree: mockTree }));

    // Should have 3 nodes (Project, Select, Users)
    expect(result.current.nodes).toHaveLength(3);

    // Should have 2 edges (Select -> Project, Users -> Select)
    expect(result.current.edges).toHaveLength(2);


    // Verify node structure
    expect(result.current.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: '1',
          type: 'ra',
          data: { label: 'Project' },
        }),
        expect.objectContaining({
          id: '2',
          type: 'ra',
          data: { label: 'Select' },
        }),
        expect.objectContaining({
          id: '3',
          type: 'ra',
          data: { label: 'Users' },
        }),
      ])
    );

    // Verify edge structure
    expect(result.current.edges).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: '1-2',
          source: '2',
          target: '1',
        }),
        expect.objectContaining({
          id: '2-3',
          source: '3',
          target: '2',
        }),
      ])
    );
  });

  test("should handle undefined tree", () => {
    const { result } = renderHook(() => useRAQueryDiagram({ tree: undefined }));

    // Should have no nodes or edges
    expect(result.current.nodes).toHaveLength(0);
    expect(result.current.edges).toHaveLength(0);
  });
});
