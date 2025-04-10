import { ArrowLeft, FilePlus } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

import { ProjectsService, QueriesService, Query, type Project } from "../api";
import { useErrorToast } from "../hooks/useErrorToast";

import QueryMenuItem from "./QueryMenuItem";

type ProjectSidebarProps = {
  project: Project;
  currentQueryId?: number;
  onSelect: (id: number | undefined) => void;
  onSuccess: () => void;
};

const ProjectSidebar = ({
  project,
  currentQueryId,
  onSelect,
  onSuccess,
}: ProjectSidebarProps) => {
  const [creatingQueryId, setCreatingQueryId] = useState<number | null>(null);

  const { queries } = project;

  const navigate = useNavigate();

  const toast = useErrorToast();

  useEffect(() => {
    if (!currentQueryId && queries.length > 0) {
      onSelect(queries[0].id);
    }
  }, [queries, currentQueryId, onSelect]);

  const createQuery = async (): Promise<void> => {
    try {
      const newQuery = await ProjectsService.projectsQueriesCreate({
        projectPk: project.id,
        requestBody: {
          name: "Untitled",
          text: "",
        } as Query,
      });
      onSuccess();
      setCreatingQueryId(newQuery.id);
    } catch (error) {
      toast({
        title: "Error creating query",
      });
    }
  };

  const renameQuery = async (id: number, name: string): Promise<void> => {
    try {
      await QueriesService.queriesPartialUpdate({
        id,
        requestBody: {
          name,
        },
      });
      onSuccess();
    } catch (error) {
      toast({
        title: "Error renaming query",
      });
    }
  };

  const deleteQuery = async (id: number): Promise<void> => {
    try {
      await QueriesService.queriesDestroy({
        id,
      });
      await onSuccess();
      if (currentQueryId === id) {
        onSelect(undefined);
      }
    } catch (error) {
      toast({
        title: "Error deleting query",
      });
    }
  };

  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem className="flex items-center">
            <Button
              className="mr-2 h-10"
              size="icon-inline"
              variant="link"
              onClick={() => navigate("/projects")}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-sm">{project.name}</h1>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center justify-between">
            <span>Queries</span>
            <Button
              aria-label="Create Query"
              className="justify-end"
              size="icon"
              variant="ghost"
              onClick={createQuery}
            >
              <FilePlus />
            </Button>
          </SidebarGroupLabel>

          <SidebarGroupContent>
            <SidebarMenu>
              {queries.map(({ id, name }) => (
                <QueryMenuItem
                  key={id}
                  isActive={currentQueryId === id}
                  isCreating={creatingQueryId === id}
                  name={name}
                  onCreationEnd={() => setCreatingQueryId(null)}
                  onDelete={() => deleteQuery(id)}
                  onRename={(name: string) => renameQuery(id, name)}
                  onSelect={() => onSelect(id)}
                />
              ))}
              {queries.length === 0 && (
                <span className="text-sm text-muted-foreground p-2">
                  Click the{" "}
                  <FilePlus className="inline align-baseline h-4 w-4" /> button
                  to create your first query.
                </span>
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
};

export default ProjectSidebar;
