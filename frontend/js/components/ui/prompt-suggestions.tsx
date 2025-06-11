/* eslint-disable unicorn/no-abusive-eslint-disable */
/* eslint-disable */
interface PromptSuggestionsProps {
  label: string;
  append: (message: { role: "user"; content: string }) => void;
  suggestions: string[];
}

export function PromptSuggestions({
  label,
  append,
  suggestions,
}: PromptSuggestionsProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-center text-lg font-bold mt-5">{label}</h2>
      <div className="flex gap-6 text-sm">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            className="h-max flex-1 rounded-xl border bg-background p-4 hover:bg-muted"
            onClick={() => append({ role: "user", content: suggestion })}
          >
            <p>{suggestion}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
