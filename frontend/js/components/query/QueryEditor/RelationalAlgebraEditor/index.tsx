/* eslint-disable import/no-duplicates */
import "mathlive";
import { MathfieldElement } from "mathlive";
/* eslint-enable import/no-duplicates */
import { useEffect, useRef, useState } from "react";

import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import AutosaveStatus from "../AutosaveStatus";
import CodeEditor from "../CodeEditor";
import ErrorAlert from "../ErrorAlert";

import RAKeyboard from "./RAKeyboard";

type RelationalAlgebraEditorProps = {
  query: Query;
  setQuery: (query: Query) => void;
};

type InputMode = "keyboard" | "code";

const RelationalAlgebraEditor = ({
  query,
  setQuery,
}: RelationalAlgebraEditorProps) => {
  const [value, setValue] = useState<string | undefined>(query.ra_text);
  const [mode, setMode] = useState<InputMode>("keyboard");
  const mf = useRef<MathfieldElement>(null);

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

    el.smartMode = true;

    MathfieldElement.soundsDirectory = null;
  }, []);

  const updateRaText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { ra_text: value },
    });
    setQuery(result);
  };

  const status = useAutosave({ data: value, onSave: updateRaText });

  return (
    <>
      <math-field
        ref={mf}
        onInput={() => {
          setValue(mf.current?.getValue?.());
        }}
      >
        {value}
      </math-field>

      <div className="flex justify-between text-xs mt-2 mb-4">
        <div className="flex items-center space-x-2">
          <Switch
            checked={mode === "code"}
            id="mode-switch"
            size="sm"
            onCheckedChange={(checked) =>
              setMode(checked ? "code" : "keyboard")
            }
          />
          <Label htmlFor="mode-switch">LaTeX code</Label>
        </div>
        <AutosaveStatus status={status} />
      </div>

      {mode === "keyboard" && (
        <RAKeyboard
          className="mt-4"
          onInsert={(expr) => mf.current?.executeCommand(["insert", expr])}
        />
      )}

      {mode === "code" && (
        <CodeEditor
          className="max-h-[300px]"
          language="latex"
          options={{
            lineNumbers: "off",
          }}
          value={value}
          onChange={setValue}
        />
      )}

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
