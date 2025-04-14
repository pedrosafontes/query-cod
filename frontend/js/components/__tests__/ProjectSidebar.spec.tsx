import { render, screen, waitFor, within } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { BrowserRouter } from "react-router";

import { SidebarProvider } from "@/components/ui/sidebar";
import { Project, ProjectsService, QueriesService } from "api";

import ProjectSidebar from "../ProjectSidebar";

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
          onSelect={jest.fn()}
          onSuccess={jest.fn()}
          {...props}
        />
      </SidebarProvider>
    </BrowserRouter>,
  );

const openQueryDropdown = async (queryName: string) => {
  const queryItem = screen.getByText(queryName).closest("li")!;
  const dropdownButton = within(queryItem).getByRole("button", {
    name: /actions/i,
  });
  await userEvent.click(dropdownButton);
};

describe("ProjectSidebar", () => {
  const onSelect = jest.fn();
  const onSuccess = jest.fn();

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

  test("calls onSelect for a query click", async () => {
    renderComponent({ onSelect });

    await userEvent.click(screen.getByText("Query 2"));
    expect(onSelect).toHaveBeenCalledWith(102);
  });

  describe("Query CRUD operations", () => {
    describe("Creating queries", () => {
      test("creates a new query", async () => {
        (ProjectsService.projectsQueriesCreate as jest.Mock).mockResolvedValue({
          id: 999,
          name: "Untitled",
          text: "",
        });

        renderComponent({ onSuccess });

        const createButton = screen.getByRole("button", {
          name: /create query/i,
        });
        await userEvent.click(createButton);

        await waitFor(() =>
          expect(ProjectsService.projectsQueriesCreate).toHaveBeenCalled(),
        );
        expect(onSuccess).toHaveBeenCalled();
      });

      test("handles network errors during query creation", async () => {
        (ProjectsService.projectsQueriesCreate as jest.Mock).mockRejectedValue(
          new Error("Create error"),
        );

        renderComponent();

        const createButton = screen.getByRole("button", {
          name: /create query/i,
        });
        await userEvent.click(createButton);

        await waitFor(() => {
          expect(mockToast).toHaveBeenCalledWith(
            expect.objectContaining({
              title: expect.stringContaining("Error"),
            }),
          );
        });
      });
    });

    describe("Renaming queries", () => {
      test("allows renaming a query", async () => {
        (QueriesService.queriesPartialUpdate as jest.Mock).mockResolvedValue(
          {},
        );

        renderComponent({ onSuccess });

        await openQueryDropdown("Query 1");

        const renameItem = await screen.findByRole("menuitem", {
          name: /rename query/i,
        });

        await userEvent.click(renameItem);

        const input = await screen.findByDisplayValue("Query 1");
        await userEvent.clear(input);
        await userEvent.type(input, "Renamed Query");
        await userEvent.keyboard("{Enter}");

        expect(QueriesService.queriesPartialUpdate).toHaveBeenCalledWith({
          id: 101,
          requestBody: { name: "Renamed Query" },
        });
        expect(onSuccess).toHaveBeenCalled();
      });

      test("enters rename mode on double click", async () => {
        renderComponent();
      
        const queryItem = screen.getByText("Query 1");
        await userEvent.dblClick(queryItem);
      
        const input = await screen.findByDisplayValue("Query 1");
        expect(input).toBeInTheDocument();
      });

      test("allows cancelling a query rename operation", async () => {
        renderComponent();

        await openQueryDropdown("Query 1");

        const renameItem = await screen.findByRole("menuitem", {
          name: /rename query/i,
        });

        await userEvent.click(renameItem);

        const input = await screen.findByDisplayValue("Query 1");
        await userEvent.clear(input);
        await userEvent.type(input, "Renamed Query");

        // Press Escape to cancel
        await userEvent.keyboard("{Escape}");

        // The original text should still be there
        expect(screen.getByText("Query 1")).toBeInTheDocument();
        expect(QueriesService.queriesPartialUpdate).not.toHaveBeenCalled();
      });

      test("handles network errors during query rename", async () => {
        (
          QueriesService.queriesPartialUpdate as jest.Mock
        ).mockRejectedValueOnce(new Error("Network error"));

        renderComponent();

        await openQueryDropdown("Query 1");

        const renameItem = await screen.findByRole("menuitem", {
          name: /rename query/i,
        });

        await userEvent.click(renameItem);

        const input = await screen.findByDisplayValue("Query 1");
        await userEvent.clear(input);
        await userEvent.type(input, "Renamed Query");
        await userEvent.keyboard("{Enter}");

        await waitFor(() => {
          expect(mockToast).toHaveBeenCalledWith(
            expect.objectContaining({
              title: expect.stringContaining("Error"),
            }),
          );
        });
      });
    });

    describe("Deleting queries", () => {
      test("deletes a query", async () => {
        (QueriesService.queriesDestroy as jest.Mock).mockResolvedValue({});

        renderComponent({ onSuccess });

        await openQueryDropdown("Query 1");

        const deleteItem = await screen.findByRole("menuitem", {
          name: /delete query/i,
        });

        await userEvent.click(deleteItem);

        expect(QueriesService.queriesDestroy).toHaveBeenCalledWith({ id: 101 });
        expect(onSuccess).toHaveBeenCalled();
      });

      test("handles network errors during query deletion", async () => {
        (QueriesService.queriesDestroy as jest.Mock).mockRejectedValueOnce(
          new Error("Network error"),
        );

        renderComponent();

        await openQueryDropdown("Query 1");

        const deleteItem = await screen.findByRole("menuitem", {
          name: /delete query/i,
        });

        await userEvent.click(deleteItem);

        await waitFor(() => {
          expect(mockToast).toHaveBeenCalledWith(
            expect.objectContaining({
              title: expect.stringContaining("Error"),
            }),
          );
        });
      });
    });
  });
});
