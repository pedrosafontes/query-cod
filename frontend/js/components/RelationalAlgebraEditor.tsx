/* eslint-disable import/no-duplicates */
import "mathlive";
import { MathfieldElement } from "mathlive";
/* eslint-enable import/no-duplicates */
import React, { useEffect, useRef, useState } from "react";

import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";
import { QueryError } from "types/query";

import AutosaveStatus from "./AutosaveStatus";
import RAKeyboard from "./RAKeyboard";

type RelationalAlgebraEditorProps = {
  onErrorsChange: (errors: QueryError[]) => void;
  query: Query;
};

const RelationalAlgebraEditor: React.FC<RelationalAlgebraEditorProps> = ({
  query,
  onErrorsChange,
}) => {
  const [value, setValue] = useState<string | undefined>(query.ra_text);
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

    MathfieldElement.soundsDirectory = null;
  }, []);

  const updateRaText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { ra_text: value },
    });

    onErrorsChange(result.validation_errors);
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
      <div className="flex justify-end text-xs mt-2">
        <AutosaveStatus status={status} />
      </div>
      <RAKeyboard
        className="mt-4"
        onInsert={(expr) => mf.current?.executeCommand(["insert", expr])}
      />
    </>
  );
};

export default RelationalAlgebraEditor;
