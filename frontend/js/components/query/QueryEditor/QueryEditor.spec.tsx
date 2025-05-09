import { render, screen } from "@testing-library/react";

import "@testing-library/jest-dom";
import { Query } from "api";

import RAEditor from "./RAEditor";
import SQLEditor from "./SQLEditor";

import QueryEditor from ".";

jest.mock("./SQLEditor", () => {
  return jest.fn(() => <div data-testid="sql-editor">SQL Editor</div>);
});

jest.mock("./RAEditor", () => {
  return jest.fn(() => <div data-testid="ra-editor">RA Editor</div>);
});

describe("QueryEditor", () => {
  const mockSetQuery = jest.fn();

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
    render(<QueryEditor query={mockSQLQuery} setQuery={mockSetQuery} />);

    expect(screen.getByTestId("sql-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("ra-editor")).not.toBeInTheDocument();
    expect(SQLEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockSQLQuery,
        setQuery: mockSetQuery,
      }),
      expect.anything(),
    );
  });

  test("renders RAEditor when query language is ra", () => {
    render(<QueryEditor query={mockRAQuery} setQuery={mockSetQuery} />);

    expect(screen.getByTestId("ra-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("sql-editor")).not.toBeInTheDocument();
    expect(RAEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockRAQuery,
        setQuery: mockSetQuery,
      }),
      expect.anything(),
    );
  });
});
