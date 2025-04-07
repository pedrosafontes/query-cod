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
  id: number;
  name: string;
  isActive: boolean;
  onSelect: (id: number) => void;
  onRename: (id: number, newName: string) => void;
  onDelete: (id: number) => void;
}

const QueryMenuItem = ({
  id,
  name,
  isActive,
  onSelect,
  onRename,
  onDelete,
}: QueryMenuItemProps) => {
  const [editing, setEditing] = useState(false);

  return (
    <SidebarMenuItem>
      {editing ? (
        <Input
          autoFocus
          className="h-8 text-sm"
          defaultValue={name}
          onBlur={(e) => {
            onRename(id, e.target.value);
            setEditing(false);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onRename(id, (e.target as HTMLInputElement).value);
              setEditing(false);
            } else if (e.key === "Escape") {
              setEditing(false);
            }
          }}
        />
      ) : (
        <SidebarMenuButton
          className="group justify-between"
          isActive={isActive}
          onClick={() => onSelect(id)}
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
              <DropdownMenuItem onSelect={() => setEditing(true)}>
                <Pencil className="mr-2" />
                Rename
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => onDelete(id)}>
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
