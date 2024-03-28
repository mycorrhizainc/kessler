import { ReactNode } from "react";
import ToolBar from "./ToolBar";

type Props = {
  children: ReactNode;
};
export default function Layout({ children }: Props) {
  return (
    <div className="container h-screen">
      {children}
      <ToolBar />
    </div>
  );
}
