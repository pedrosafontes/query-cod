import { ReactNode } from "react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LanguageEnum, ProjectsService, Query } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type CreateQueryButtonProps = {
  children?: ReactNode;
  projectId: number;
  onSuccess?: (id: number) => Promise<void>;
};

const CreateQueryButton = ({
  children,
  projectId,
  onSuccess,
}: CreateQueryButtonProps) => {
  const toast = useErrorToast();

  const createQuery = async (language: LanguageEnum): Promise<void> => {
    try {
      const newQuery = await ProjectsService.projectsQueriesCreate({
        projectPk: projectId,
        requestBody: {
          name: "Untitled",
          language,
        } as Query,
      });
      await onSuccess?.(newQuery.id);
    } catch (error) {
      toast({
        title: "Error creating query",
      });
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>{children}</DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => createQuery("sql")}>
          SQL
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => createQuery("ra")}>
          RA
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default CreateQueryButton;
