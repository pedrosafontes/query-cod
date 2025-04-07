import { ArrowLeft, FilePlus } from "lucide-react";
import { useEffect } from "react";
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

import type { Project } from "../api";

import QueryMenuItem from "./QueryMenuItem";

type ProjectSidebarProps = {
  project: Project;
  currentQueryId?: number;
  onSelect: (id: number) => void;
  onCreate: () => void;
  onRename: (id: number, name: string) => void;
  onDelete: (id: number) => void;
};

const ProjectSidebar = ({
  project,
  currentQueryId,
  onSelect,
  onCreate,
  onRename,
  onDelete,
}: ProjectSidebarProps) => {
  const { queries } = project;

  const navigate = useNavigate();

  useEffect(() => {
    if (!currentQueryId && queries.length > 0) {
      onSelect(queries[0].id);
    }
  }, [queries, currentQueryId, onSelect]);

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
              className="justify-end"
              size="icon"
              variant="ghost"
              onClick={onCreate}
            >
              <FilePlus />
            </Button>
          </SidebarGroupLabel>

          <SidebarGroupContent>
            <SidebarMenu>
              {queries.map((query) => (
                <QueryMenuItem
                  key={query.id}
                  id={query.id}
                  isActive={currentQueryId === query.id}
                  name={query.name}
                  onDelete={onDelete}
                  onRename={onRename}
                  onSelect={onSelect}
                />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
};

export default ProjectSidebar;
