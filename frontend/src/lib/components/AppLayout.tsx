import { ReactNode } from "react";
import ToolBar from "./ToolBar";

type Props = {
  children: ReactNode;
};
export default function Layout({ children }: Props) {
  return (
<<<<<<< HEAD
    <div className="appMain flex flex-col z-0 h-screen w-full justify-center items-center">
=======
    <div className="container h-screen">
>>>>>>> d57a0f4 (working frontend link add !)
      {children}
      <ToolBar />
    </div>
  );
}
