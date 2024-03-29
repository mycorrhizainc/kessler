import { ReactNode } from "react";
import ToolBar from "./ToolBar";

type Props = {
  children: ReactNode;
};
export default function Layout({ children }: Props) {
  return (
    <div className="appMain flex flex-col z-0 h-screen w-full justify-center items-center">
      {children}
      <ToolBar />
    </div>
  );
}
