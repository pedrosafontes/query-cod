import { useEffect, useState } from "react";
import { useParams } from "react-router";

import { ProjectsService, Query } from "../api";
import QueryExplorer from "../components/QueryExplorer";
import ProjectSidebar from "../components/ProjectSidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

const ProjectPage = () => {
  const [project, setProject] =
    useState<Awaited<ReturnType<typeof ProjectsService.projectsRetrieve>>>();
  const [currentQueryId, setCurrentQueryId] = useState<number | undefined>(
    undefined,
  );
  const { projectId : projectParamId } = useParams<{ projectId: string }>();
  const projectId = Number(projectParamId);

  const queries = project?.queries;
  const query = queries?.find((query) => query.id === currentQueryId);

  const fetchProject = async () => {
    const result = await ProjectsService.projectsRetrieve({
      id: projectId,
    });
    setProject(result);
  };

  const createQuery = async (): Promise<void> => {
    try {
      await ProjectsService.projectsQueriesCreate({
        projectPk: projectId,
        requestBody: {
          name: "Query",
          text: "",
        } as Query,
      });

      fetchProject();
    } catch (error) {
      console.error("Error creating query:", error);
    }
  };

  useEffect(() => {
    fetchProject();
  }, []);

  return (
    <SidebarProvider defaultOpen={true}>
        {project && queries && (
          <ProjectSidebar
            project={project}
            currentQueryId={currentQueryId}
            onCreate={createQuery}
            onSelect={setCurrentQueryId}
          />
        )}
        <SidebarInset>
          {query && <QueryExplorer key={query.id} query={query} />}
        </SidebarInset>
    </SidebarProvider>
  );
};

export default ProjectPage;
