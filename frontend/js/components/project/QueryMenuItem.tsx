import { Ellipsis, Pencil, SquareCode, SquarePi, Trash } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import * as React from "react";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";
import { QueriesService, QuerySummary } from "api";
import { useErrorToast } from "hooks/useErrorToast";
import { cn } from "lib/utils";

interface QueryMenuItemProps {
  query: QuerySummary;
  isActive: boolean;
  onSelect: () => void;
  onRename: () => Promise<void>;
  onDelete: (id: number) => void;
  isCreating?: boolean;
  onCreationEnd?: () => void;
}

const QueryMenuItem = ({
  query: { id, name, language },
  isActive,
  onSelect,
  onRename,
  onDelete,
  isCreating,
  onCreationEnd,
}: QueryMenuItemProps) => {
  const [manuallyEditing, setManuallyEditing] = useState(false);
  const [inputValue, setInputValue] = useState(name);
  const inputRef = useRef<HTMLInputElement>(null);
  const editing = isCreating || manuallyEditing;

  useEffect(() => {
    setInputValue(name);
  }, [name]);

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  const toast = useErrorToast();

  const renameQuery = async (name: string): Promise<void> => {
    try {
      await QueriesService.queriesPartialUpdate({
        id,
        requestBody: {
          name,
        },
      });
      await onRename();
    } catch (error) {
      toast({
        title: "Error renaming query",
      });
    }
  };

  const deleteQuery = async (): Promise<void> => {
    try {
      await QueriesService.queriesDestroy({
        id,
      });
      await onDelete(id);
    } catch (error) {
      toast({
        title: "Error deleting query",
      });
    }
  };

  const handleRename = () => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue && trimmedValue !== name) {
      renameQuery(trimmedValue);
    } else {
      setInputValue(name); // Reset to original name if empty or unchanged
    }
    endEditing();
  };

  const endEditing = () =>
    isCreating ? onCreationEnd?.() : setManuallyEditing(false);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleRename();
    } else if (e.key === "Escape") {
      endEditing();
    }
  };

  let LangageIcon;
  if (language === "ra") {
    LangageIcon = SquarePi;
  } else {
    LangageIcon = SquareCode;
  }

  return (
    <SidebarMenuItem className={cn(editing && "py-1")}>
      {editing ? (
        <Input
          ref={inputRef}
          className="h-8 text-sm"
          value={inputValue}
          onBlur={handleRename}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      ) : (
        <SidebarMenuButton
          className="group/item justify-between"
          isActive={isActive}
          onClick={onSelect}
          onDoubleClick={() => setManuallyEditing(true)}
        >
          <LangageIcon className="size-4 shrink-0 text-muted-foreground" />
          <span className="truncate text-clip grow [background-image:linear-gradient(to_right,_black_90%,_transparent_100%)] bg-clip-text text-transparent">
            {name}
          </span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div
                aria-label="Actions"
                className="opacity-0 group-hover/item:opacity-100 data-[state=open]:opacity-75 transition-opacity focus-visible:outline-none"
                role="button"
                tabIndex={0}
              >
                <Ellipsis className="size-4 shrink-0" />
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" side="right">
              <DropdownMenuItem
                aria-label="Rename Query"
                onClick={() => setManuallyEditing(true)}
              >
                <Pencil />
                Rename
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                aria-label="Delete Query"
                className="text-destructive"
                onClick={deleteQuery}
              >
                <Trash />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuButton>
      )}
    </SidebarMenuItem>
  );
};

export default QueryMenuItem;
