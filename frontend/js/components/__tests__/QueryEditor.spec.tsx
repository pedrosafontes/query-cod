import { render, screen } from "@testing-library/react";

import "@testing-library/jest-dom";
import { Query } from "api";

import QueryEditor from "../QueryEditor";
import RelationalAlgebraEditor from "../RelationalAlgebraEditor";
import SQLEditor from "../SQLEditor";

jest.mock("../SQLEditor", () => {
  return jest.fn(() => <div data-testid="sql-editor">SQL Editor</div>);
});

jest.mock("../RelationalAlgebraEditor", () => {
  return jest.fn(() => <div data-testid="ra-editor">RA Editor</div>);
});

describe("QueryEditor", () => {
  const mockOnErrorsChange = jest.fn();

  const mockSQLQuery: Query = {
    id: 1,
    name: "Test Query",
    sql_text: "SELECT * FROM users",
    language: "sql",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
  };

  const mockRAQuery: Query = {
    ...mockSQLQuery,
    language: "ra",
    ra_text: "\\project_{name}Employee",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders SQLEditor when query language is sql", () => {
    render(
      <QueryEditor query={mockSQLQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(screen.getByTestId("sql-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("ra-editor")).not.toBeInTheDocument();
    expect(SQLEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockSQLQuery,
        onErrorsChange: expect.any(Function),
      }),
      expect.anything(),
    );
  });

  test("renders RelationalAlgebraEditor when query language is ra", () => {
    render(
      <QueryEditor query={mockRAQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(screen.getByTestId("ra-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("sql-editor")).not.toBeInTheDocument();
    expect(RelationalAlgebraEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockRAQuery,
        onErrorsChange: expect.any(Function),
      }),
      expect.anything(),
    );
  });

  test("calls onErrorsChange when query validation_errors change", () => {
    render(
      <QueryEditor query={mockSQLQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(mockOnErrorsChange).toHaveBeenCalledWith(
      mockSQLQuery.validation_errors,
    );
  });

  test("displays ErrorAlert when there are general errors", () => {
    const mockQuery = {
      ...mockSQLQuery,
      validation_errors: [
        { message: "General error 1" },
        { message: "General error 2" },
      ],
    };

    render(
      <QueryEditor query={mockQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(screen.getByText("Query validation failed")).toBeInTheDocument();
    expect(screen.getByText("General error 1")).toBeInTheDocument();
    expect(screen.getByText("General error 2")).toBeInTheDocument();
  });

  test("doesn't display ErrorAlert when there are no general errors", () => {
    const mockQuery = {
      ...mockSQLQuery,
      validation_errors: [
        {
          message: "Error with position",
          position: { line: 1, start_col: 5, end_col: 10 },
        },
      ],
    };

    render(
      <QueryEditor query={mockQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(
      screen.queryByText("Query validation failed"),
    ).not.toBeInTheDocument();
  });
});
