import { LanguageEnum } from "api";

import CodeEditor from "./QueryEditor/CodeEditor";
import LatexFormula from "./QueryEditor/RAEditor/LatexFormula";

const ReadOnlyQuery = ({
  text,
  language,
}: {
  text: string;
  language: LanguageEnum;
}) => {
  switch (language) {
    case "sql":
      return (
        <CodeEditor
          className="max-h-[400px]"
          language="sql"
          options={{
            lineNumbers: "on",
            readOnly: true,
          }}
          value={text}
        />
      );

    case "ra":
      return (
        <LatexFormula className="mx-3 pb-3 overflow-auto" expression={text} />
      );

    default:
      return null;
  }
};

export default ReadOnlyQuery;
