/* eslint-disable import/no-duplicates */
import "mathlive";
import { MathfieldElement } from "mathlive";
/* eslint-enable import/no-duplicates */
import { useEffect, useRef, useState } from "react";

import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import AutosaveStatus from "../AutosaveStatus";
import CodeEditor from "../CodeEditor";
import ErrorAlert from "../ErrorAlert";

import RAKeyboard from "./RAKeyboard";

type RAEditorProps = {
  query: Query;
  updateText: (text: string) => Promise<void>;
};

type InputMode = "keyboard" | "code";

const RAEditor = ({ query, updateText }: RAEditorProps) => {
  const [value, setValue] = useState<string | undefined>(query.text);
  const [mode, setMode] = useState<InputMode>("keyboard");
  const mf = useRef<MathfieldElement>(null);

  useEffect(() => {
    const el = mf.current;
    if (!el) return;

    // Customize Mathfield behavior
    el.smartMode = true;

    // Ensure commas are only inserted in math mode
    const handleBeforeInput = (ev: InputEvent) => {
      if (ev.data === ',' && el.mode === 'text') {
        ev.preventDefault();
        el.executeCommand(['switchMode', 'math']);
        el.executeCommand(['insert', ',']);
      }
    };
    el.addEventListener('beforeinput', handleBeforeInput);

    MathfieldElement.soundsDirectory = null;
  }, []);

  const status = useAutosave({ data: value, onSave: updateText });

  return (
    <div className="px-3 shrink overflow-auto">
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
          className="max-h-[300px] border-y -mx-3"
          language="latex"
          options={{
            lineNumbers: "off",
          }}
          value={value}
          onChange={setValue}
        />
      )}

      <div className="mt-2 text-xs text-muted-foreground">
        <h4 className="font-semibold mb-1">Tips</h4>
        <ul className="list-disc pl-4">
          <li>
            Insert identifiers containing underscores in the LaTex editor inside the <span className="font-mono">text</span> tag.
          </li>
          <li>
            For multi-line support, wrap the entire expression in a <span className="font-mono">displaylines</span> tag.
          </li>
        </ul>
      </div>

      {query.validation_errors.map((error) => (
        <ErrorAlert
          key={error.title + error.description}
          className="mt-4"
          description={error.description}
          hint={error.hint}
          title={error.title}
        />
      ))}
    </div>
  );
};

export default RAEditor;
