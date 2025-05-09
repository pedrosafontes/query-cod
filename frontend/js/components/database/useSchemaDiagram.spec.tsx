import { renderHook, act, waitFor } from "@testing-library/react";

import { Database, DatabasesService } from "api";

import useSchemaDiagram from "./useSchemaDiagram";

jest.mock("api", () => ({
  DatabasesService: {
    databasesRetrieve: jest.fn(),
  },
}));

jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => jest.fn(),
}));

jest.mock("hooks/useLayout", () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe("useSchemaDiagram", () => {
  const mockSchema: Database["schema"] = {
    users: {
      id: {
        type: "integer",
        primary_key: true,
        references: null,
        nullable: false,
      },
      email: {
        type: "varchar",
        primary_key: false,
        references: null,
        nullable: false,
      },
    },
    posts: {
      id: {
        type: "integer",
        primary_key: true,
        references: null,
        nullable: false,
      },
      title: {
        type: "varchar",
        primary_key: false,
        references: null,
        nullable: false,
      },
      user_id: {
        type: "integer",
        primary_key: false,
        references: { table: "users", column: "id" },
        nullable: false,
      },
    },
  };

  const mockDatabase: Database = {
    id: 1,
    name: "Test DB",
    schema: mockSchema,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("should fetch database schema on mount", async () => {
    (DatabasesService.databasesRetrieve as jest.Mock).mockResolvedValue(
      mockDatabase,
    );

    const { result } = renderHook(() => useSchemaDiagram({ databaseId: 1 }));

    await waitFor(() => {
      expect(result.current.nodes).toHaveLength(2); // users and posts tables
      expect(result.current.edges).toHaveLength(1); // One foreign key relationship
    });
  });

  test("should handle API error", async () => {
    const errorMock = new Error("API Error");
    (DatabasesService.databasesRetrieve as jest.Mock).mockRejectedValue(
      errorMock,
    );

    const { result } = renderHook(() => useSchemaDiagram({ databaseId: 1 }));

    // Wait for the error to be handled
    await waitFor(() => {
      expect(DatabasesService.databasesRetrieve).toHaveBeenCalledWith({
        id: 1,
      });
    });

    // Should not create nodes and edges
    expect(result.current.nodes).toEqual([]);
    expect(result.current.edges).toEqual([]);
  });
});
