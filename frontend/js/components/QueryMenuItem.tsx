import { MoreVertical, Pencil, Trash } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";

interface QueryMenuItemProps {
  name: string;
  isActive: boolean;
  onSelect: () => void;
  onRename: (newName: string) => void;
  onDelete: () => void;
  isCreating?: boolean;
  onCreationEnd?: () => void;
}

const QueryMenuItem = ({
  name,
  isActive,
  onSelect,
  onRename,
  onDelete,
  isCreating,
  onCreationEnd,
}: QueryMenuItemProps) => {
  const [manuallyEditing, setManuallyEditing] = useState(false);
  const editing = isCreating || manuallyEditing;

  const endEditing = () => isCreating ? onCreationEnd?.() : setManuallyEditing(false);

  return (
    <SidebarMenuItem>
      {editing ? (
        <Input
          autoFocus
          className="h-8 text-sm"
          defaultValue={name}
          onBlur={(e) => {
            onRename(e.target.value);
            endEditing();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onRename((e.target as HTMLInputElement).value);
              endEditing();
            } else if (e.key === "Escape") {
              endEditing();
            }
          }}
        />
      ) : (
        <SidebarMenuButton
          className="group justify-between"
          isActive={isActive}
          onClick={() => onSelect()}
        >
          <span className="truncate">{name}</span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                size="icon"
                variant="ghost"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreVertical />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" side="right">
              <DropdownMenuItem onSelect={() => setManuallyEditing(true)}>
                <Pencil className="mr-2" />
                Rename
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => onDelete()}>
                <Trash className="mr-2 text-red-600" />
                <span className="text-red-600">Delete</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuButton>
      )}
    </SidebarMenuItem>
  );
};

export default QueryMenuItem;
