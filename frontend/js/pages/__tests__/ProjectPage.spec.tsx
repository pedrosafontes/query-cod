import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";

import { ProjectsService } from "api";
import { useErrorToast } from "hooks/useErrorToast";
import { QueryExplorerProps } from "js/components/query/QueryExplorer";

import ProjectsPage from "../ProjectPage";

jest.mock("api", () => ({
  ProjectsService: {
    projectsRetrieve: jest.fn(),
  },
}));

jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: jest.fn(),
}));

jest.mock(
  "components/query/QueryExplorer",
  () =>
    ({ queryId }: QueryExplorerProps) => (
      <div data-testid="query-explorer">{queryId}</div>
    ),
);

describe("ProjectPage", () => {
  const sampleProject = {
    id: 1,
    name: "Sample Project",
    queries: [
      {
        id: 101,
        name: "First Query",
        text: "SELECT 1",
      },
      {
        id: 102,
        name: "Second Query",
        text: "SELECT 2",
      },
    ],
    database: {
      name: "TestDB",
    },
  };

  const mockToast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useErrorToast as jest.Mock).mockReturnValue(mockToast);
    (ProjectsService.projectsRetrieve as jest.Mock).mockResolvedValue(
      sampleProject,
    );
  });

  // Helper to render the ProjectPage with a router so that useParams works.
  const renderComponent = () =>
    render(
      <MemoryRouter initialEntries={[`/projects/${sampleProject.id}`]}>
        <Routes>
          <Route element={<ProjectsPage />} path="/projects/:projectId" />
        </Routes>
      </MemoryRouter>,
    );

  test("fetches and renders the project, then auto-selects the first query", async () => {
    renderComponent();

    expect(ProjectsService.projectsRetrieve).toHaveBeenCalledWith({
      id: sampleProject.id,
    });

    await waitFor(() => {
      expect(screen.getByTestId("query-explorer")).toHaveTextContent(
        sampleProject.queries[0].id.toString(),
      );
    });
  });

  test("shows an error toast when project retrieval fails", async () => {
    (ProjectsService.projectsRetrieve as jest.Mock).mockRejectedValueOnce(
      new Error("API failure"),
    );
    renderComponent();

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error loading project",
      });
    });
  });
});
