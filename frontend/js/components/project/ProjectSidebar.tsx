import {
  ArrowLeft,
  FilePlus,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
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
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { type Project } from "api";
import { cn } from "lib/utils";

import CreateQueryButton from "./CreateQueryButton";
import QueryMenuItem from "./QueryMenuItem";

type ProjectSidebarProps = {
  project: Project;
  currentQueryId?: number;
  setCurrentQueryId: (id?: number) => void;
  onSuccess: () => Promise<void>;
};

const ProjectSidebar = ({
  project,
  currentQueryId,
  setCurrentQueryId,
  onSuccess,
}: ProjectSidebarProps) => {
  const [creatingQueryId, setCreatingQueryId] = useState<number | null>(null);

  const { queries } = project;

  const navigate = useNavigate();

  useEffect(() => {
    if (!currentQueryId && queries.length > 0) {
      setCurrentQueryId(queries[0].id);
    }
  }, [queries, currentQueryId, setCurrentQueryId]);

  const onDeleteQuery = async (id: number): Promise<void> => {
    await onSuccess();
    if (currentQueryId === id) {
      setCurrentQueryId(undefined);
    }
  };

  const onCreateQuery = async (id: number): Promise<void> => {
    setOpen(true);
    await onSuccess();
    setCurrentQueryId(id);
    setCreatingQueryId(id);
  };

  const { open, toggleSidebar, setOpen } = useSidebar();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu className={open ? "flex flex-row justify-between" : ""}>
          {open && (
            <SidebarMenuItem className="flex items-center">
              <Button
                className="mr-2"
                size="inline"
                variant="link"
                onClick={() => navigate("/projects")}
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <h1 className="text-sm text-ellipsis">{project.name}</h1>
            </SidebarMenuItem>
          )}
          <SidebarMenuItem
            className={cn(
              "text-sm inline",
              open ? "text-muted-foreground" : "text-primary",
            )}
          >
            <SidebarMenuButton onClick={toggleSidebar}>
              {open ? <PanelLeftClose /> : <PanelLeftOpen />}
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      {open ? (
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel className="flex items-center justify-between">
              <span>Queries</span>
              <CreateQueryButton
                projectId={project.id}
                onSuccess={onCreateQuery}
              >
                <Button
                  aria-label="Create Query"
                  className="justify-end"
                  size="icon"
                  variant="link"
                >
                  <FilePlus />
                </Button>
              </CreateQueryButton>
            </SidebarGroupLabel>

            <SidebarGroupContent>
              <SidebarMenu>
                {queries.map((query) => (
                  <QueryMenuItem
                    key={query.id}
                    isActive={currentQueryId === query.id}
                    isCreating={creatingQueryId === query.id}
                    query={query}
                    onCreationEnd={() => setCreatingQueryId(null)}
                    onDelete={onDeleteQuery}
                    onRename={onSuccess}
                    onSelect={() => setCurrentQueryId(query.id)}
                  />
                ))}
                {queries.length === 0 && (
                  <span className="text-sm text-muted-foreground p-2">
                    Click the{" "}
                    <FilePlus className="inline align-baseline h-4 w-4" />{" "}
                    button to create your first query.
                  </span>
                )}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      ) : (
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <CreateQueryButton
                    projectId={project.id}
                    onSuccess={onCreateQuery}
                  >
                    <SidebarMenuButton>
                      <FilePlus />
                    </SidebarMenuButton>
                  </CreateQueryButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      )}
    </Sidebar>
  );
};

export default ProjectSidebar;
