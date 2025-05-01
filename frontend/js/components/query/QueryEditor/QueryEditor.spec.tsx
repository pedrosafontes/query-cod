import { render, screen } from "@testing-library/react";

import "@testing-library/jest-dom";
import { Query } from "api";

import RelationalAlgebraEditor from "./RelationalAlgebraEditor";
import SQLEditor from "./SQLEditor";

import QueryEditor from ".";

jest.mock("./SQLEditor", () => {
  return jest.fn(() => <div data-testid="sql-editor">SQL Editor</div>);
});

jest.mock("./RelationalAlgebraEditor", () => {
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
});
