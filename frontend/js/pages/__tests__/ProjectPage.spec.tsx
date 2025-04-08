import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import ProjectsPage from "../ProjectPage";
import { ProjectsService } from "api";
import { useToast } from "hooks/use-toast";

jest.mock("api", () => ({
  ProjectsService: {
    projectsRetrieve: jest.fn(),
  },
}));

jest.mock("hooks/use-toast", () => ({
  useToast: jest.fn(),
}));

jest.mock("components/QueryExplorer", () => ({ query }: any) => (
  <div data-testid="query-explorer">{query?.name}</div>
));

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
      name: "TestDB"
    },
  };

  const mockToast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useToast as jest.Mock).mockReturnValue({ toast: mockToast });
    (ProjectsService.projectsRetrieve as jest.Mock).mockResolvedValue(sampleProject);
  });

  // Helper to render the ProjectPage with a router so that useParams works.
  const renderComponent = () =>
    render(
      <MemoryRouter initialEntries={[`/projects/${sampleProject.id}`]}>
        <Routes>
          <Route path="/projects/:projectId" element={<ProjectsPage />} />
        </Routes>
      </MemoryRouter>
    );

  it("fetches and renders the project, then auto-selects the first query", async () => {
    renderComponent();

    expect(ProjectsService.projectsRetrieve).toHaveBeenCalledWith(
      { id: sampleProject.id}
    );

    await waitFor(() => {
      expect(screen.getByTestId("query-explorer")).toHaveTextContent("First Query");
    });
  });

  it("shows an error toast when project retrieval fails", async () => {
    (ProjectsService.projectsRetrieve as jest.Mock).mockRejectedValueOnce(
      new Error("API failure")
    );
    renderComponent();

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error loading project",
        variant: "destructive",
      });
    });
  });
});
