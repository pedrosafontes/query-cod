import { useEffect } from "react";
import { FilePlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import type { Project, Query } from "../api";

type ProjectSidebarProps = {
  project: Project;
  currentQueryId?: number;
  onSelect: (id: number) => void;
  onCreate: () => void;
};

const ProjectSidebar = ({
  project,
  currentQueryId,
  onSelect,
  onCreate,
}: ProjectSidebarProps) => {
  const queries = project.queries;
  
  useEffect(() => {
    if (!currentQueryId && queries.length > 0) {
      onSelect(queries[0].id);
    }
  }, [queries, currentQueryId, onSelect]);

  return (
      <Sidebar>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel className="flex items-center justify-between">
              <span>{project.name}</span>
              <Button
                className = "justify-end"
                variant="ghost"
                size="icon"
                onClick={onCreate}
              >
                <FilePlus />
                <span className="sr-only">Add Query</span>
              </Button>
            </SidebarGroupLabel>

            <SidebarGroupContent>
              <SidebarMenu>
                {queries.map((query) => (
                  <SidebarMenuItem key={query.id}>
                    <SidebarMenuButton
                      onClick={() => onSelect(query.id)}
                      isActive={currentQueryId === query.id}
                    >
                      {query.name} ({query.id})
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
  );
};

export default ProjectSidebar;
