import { useEffect, useState } from "react";
import { useParams } from "react-router";

import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { ProjectsService } from "api";
import ProjectSidebar from "components/ProjectSidebar";
import QueryExplorer from "components/QueryExplorer";
import { useToast } from "hooks/use-toast";

const ProjectPage = () => {
  const [project, setProject] =
    useState<Awaited<ReturnType<typeof ProjectsService.projectsRetrieve>>>();
  const [currentQueryId, setCurrentQueryId] = useState<number | undefined>(
    undefined,
  );
  const { projectId: projectParamId } = useParams<{ projectId: string }>();
  const { toast } = useToast();

  const projectId = Number(projectParamId);
  const queries = project?.queries;
  const query = queries?.find((query) => query.id === currentQueryId);

  const fetchProject = async () => {
    try {
      const result = await ProjectsService.projectsRetrieve({
        id: projectId,
      });
      setProject(result);
    } catch (error) {
      toast({
        title: "Error loading project",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchProject();
  }, []);

  return (
    <SidebarProvider defaultOpen>
      {project && queries && (
        <ProjectSidebar
          currentQueryId={currentQueryId}
          project={project}
          onSelect={setCurrentQueryId}
          onSuccess={fetchProject}
        />
      )}
      <SidebarInset className="h-screen overflow-auto">
        {query && <QueryExplorer query={query} />}
      </SidebarInset>
    </SidebarProvider>
  );
};

export default ProjectPage;
