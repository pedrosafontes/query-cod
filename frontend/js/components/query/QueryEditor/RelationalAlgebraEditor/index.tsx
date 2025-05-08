/* eslint-disable import/no-duplicates */
import "mathlive";
import { MathfieldElement } from "mathlive";
/* eslint-enable import/no-duplicates */
import React, { useEffect, useRef, useState } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import AutosaveStatus from "../AutosaveStatus";
import ErrorAlert from "../ErrorAlert";

import RAKeyboard from "./RAKeyboard";

type RelationalAlgebraEditorProps = {
  query: Query;
  setQuery: (query: Query) => void;
};

const RelationalAlgebraEditor: React.FC<RelationalAlgebraEditorProps> = ({
  query,
  setQuery,
}) => {
  const [value, setValue] = useState<string | undefined>(query.ra_text);
  const mf = useRef<MathfieldElement>(null);
  const [isPlainText, setPlainText] = useState<boolean>(false);

  useEffect(() => {
    const el = mf.current;
    if (!el) return;

    // Customize Mathfield behavior
    el.inlineShortcuts = {
      project: "\\pi_{\\placeholder{attr}}\\placeholder{rel}",
      select: "\\sigma_{\\placeholder{condition}}\\placeholder{rel}",
      union: "#@\\cup\\placeholder{rrel}",
      intersect: "#@\\cap\\placeholder{rrel}",
    };

    MathfieldElement.soundsDirectory = null;
  }, []);

  useEffect(() => {
    const el = mf.current;
    if (!el) return;

    // When switching from plain text to mathfield, update mathfield value
    if (!isPlainText && value !== undefined) {
      el.setValue(value);
    }
  }, [isPlainText, value]);

  const updateRaText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { ra_text: value },
    });
    setQuery(result);
  };

  const status = useAutosave({ data: value, onSave: updateRaText });

  const renderInput = () => {
    if (isPlainText) {
      return (
        <Input
          className="py-6"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      );
    }
    return (
      <math-field
        ref={mf}
        onInput={() => {
          setValue(mf.current?.getValue?.());
        }}
      >
        {value}
      </math-field>
    );
  };

  return (
    <>
      {renderInput()}
      <div className="flex justify-between text-xs mt-2">
        <div className="flex items-center space-x-2">
          <Switch
            checked={isPlainText}
            id="plain-text"
            size="sm"
            onCheckedChange={setPlainText}
          />
          <Label htmlFor="plain-text">Plain text</Label>
        </div>
        <AutosaveStatus status={status} />
      </div>
      <RAKeyboard
        className="mt-4"
        disabled={isPlainText}
        onInsert={(expr) => mf.current?.executeCommand(["insert", expr])}
      />

      {query.validation_errors.map((error) => (
        <ErrorAlert
          key={error.title + error.description}
          className="mt-4"
          description={error.description}
          hint={error.hint}
          title={error.title}
        />
      ))}
    </>
  );
};

export default RelationalAlgebraEditor;
