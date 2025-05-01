/* eslint-disable import/no-duplicates */
import "mathlive";
import { MathfieldElement } from "mathlive";
/* eslint-enable import/no-duplicates */
import React, { useEffect, useRef, useState } from "react";

import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";
import { QueryError } from "types/query";

import AutosaveStatus from "./AutosaveStatus";
import ErrorAlert from "./ErrorAlert";
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
  const [errors, setErrors] = useState<QueryError[]>(query.validation_errors);

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
    onErrorsChange(errors);
  }, [errors]);

  const updateRaText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { ra_text: value },
    });

    setErrors(result.validation_errors);
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

      {errors.length > 0 &&
        errors.map((error) => (
          <ErrorAlert
            key={error.description}
            className="mt-4"
            description={error.description}
            title={error.title}
          />
        ))}
    </>
  );
};

export default RelationalAlgebraEditor;
