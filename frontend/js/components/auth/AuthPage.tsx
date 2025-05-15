import { ReactNode } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import appIcon from "../../../assets/images/query-cod.png";

type AuthPageProps = {
  title: string;
  children: ReactNode;
};

const AuthPage = ({ title, children }: AuthPageProps) => {
  return (
    <div className="bg-gray-50 w-screen h-screen">
      <div className="flex gap-1 p-12 items-center justify-center font-semibold">
        <img alt="Query Cod icon" className="size-8" src={appIcon} /> Query Cod
      </div>
      <Card className="max-w-sm mx-auto rounded-xl">
        <CardHeader>
          <CardTitle className="text-center">{title}</CardTitle>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </div>
  );
};

export default AuthPage;
