import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { BrowserRouter } from "react-router";

import { SidebarProvider } from "@/components/ui/sidebar";
import { Project } from "api";

import ProjectSidebar from "./ProjectSidebar";

jest.mock("api");
const mockToast = jest.fn();
jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => mockToast,
}));

const mockProject = {
  id: 1,
  name: "Test Project",
  queries: [
    {
      id: 101,
      name: "Query 1",
    },
    {
      id: 102,
      name: "Query 2",
    },
  ],
  database: {
    id: 1,
    name: "testdb",
  },
  created: new Date().toISOString(),
  modified: new Date().toISOString(),
  last_modified: new Date().toISOString(),
} as Project;

const renderComponent = (props = {}) =>
  render(
    <BrowserRouter>
      <SidebarProvider>
        <ProjectSidebar
          currentQueryId={101}
          project={mockProject}
          setCurrentQueryId={jest.fn()}
          onSuccess={jest.fn()}
          {...props}
        />
      </SidebarProvider>
    </BrowserRouter>,
  );

describe("ProjectSidebar", () => {
  const setCurrentQueryId = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Rendering", () => {
    test("renders project name and query list", () => {
      renderComponent();
      expect(screen.getByText("Test Project")).toBeInTheDocument();
      expect(screen.getByText("Query 1")).toBeInTheDocument();
      expect(screen.getByText("Query 2")).toBeInTheDocument();
    });

    test("renders correctly with no queries", () => {
      const emptyProject = {
        ...mockProject,
        queries: [],
      };

      renderComponent({ project: emptyProject });

      expect(screen.getByText("Test Project")).toBeInTheDocument();
      expect(screen.getByText(/create your first query/i)).toBeInTheDocument();
    });
  });

  test("calls setCurrentQueryId for a query click", async () => {
    renderComponent({ setCurrentQueryId });

    await userEvent.click(screen.getByText("Query 2"));
    expect(setCurrentQueryId).toHaveBeenCalledWith(102);
  });
});
