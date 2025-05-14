import { useEffect, useState } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LanguageEnum, QueriesService, Query } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type QueryLanguageTabsProps = {
  query?: Query;
  setQuery: (query: Query) => void;
  setIsLoading: (isLoading: boolean) => void;
};

const QueryLanguageTabs = ({
  query,
  setQuery,
  setIsLoading,
}: QueryLanguageTabsProps) => {
  const [language, setLanguage] = useState<LanguageEnum>();
  const toast = useErrorToast();
  useEffect(() => {
    setLanguage(query?.language);
  }, [query]);

  if (!query) {
    return <Skeleton className="h-10 w-52" />;
  }

  const updateQueryLanguage = async (newLanguage: LanguageEnum) => {
    const oldLanguage = query.language;
    setIsLoading(true);
    setLanguage(newLanguage);
    try {
      const updatedQuery = await QueriesService.queriesPartialUpdate({
        id: query.id,
        requestBody: {
          language: newLanguage,
        },
      });
      setQuery(updatedQuery);
    } catch (err) {
      setLanguage(oldLanguage);
      toast({
        title: "Error updating query language",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Tabs
      value={language}
      onValueChange={(value) => updateQueryLanguage(value as LanguageEnum)}
    >
      <TabsList>
        <TabsTrigger value="sql">SQL</TabsTrigger>
        <TabsTrigger value="ra">Relational Algebra</TabsTrigger>
      </TabsList>
    </Tabs>
  );
};

export default QueryLanguageTabs;
