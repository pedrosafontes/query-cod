import { renderHook, waitFor } from "@testing-library/react";

import { Database, DatabasesService } from "api";

import useSchemaDiagram from "./useSchemaDiagram";

jest.mock("api", () => ({
  DatabasesService: {
    databasesRetrieve: jest.fn(),
  },
}));

const mockToast = jest.fn();

jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => mockToast,
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

      // Verify node structure
      expect(result.current.nodes).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            id: "users",
            type: "table",
            data: expect.objectContaining({
              table: "users",
              fields: mockSchema.users,
            }),
          }),
          expect.objectContaining({
            id: "posts",
            type: "table",
            data: expect.objectContaining({
              table: "posts",
              fields: mockSchema.posts,
            }),
          }),
        ]),
      );

      // Verify edge structure
      expect(result.current.edges).toEqual([
        expect.objectContaining({
          id: "posts.user_id-users.id",
          source: "posts",
          sourceHandle: "posts.user_id",
          target: "users",
          targetHandle: "users.id",
        }),
      ]);
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

    expect(mockToast).toHaveBeenCalled();

    // Should not create nodes and edges
    expect(result.current.nodes).toEqual([]);
    expect(result.current.edges).toEqual([]);
  });
});
